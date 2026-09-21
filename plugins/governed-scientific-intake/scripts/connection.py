"""Connection profiles and endpoint-bound credentials (Python standard library only)."""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import tempfile
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

PLUGIN_NAME = 'governed-scientific-intake'
LOCAL_URLS = {'mcp_url': 'http://127.0.0.1:8140/mcp', 'api_url': 'http://127.0.0.1:8010', 'web_url': 'http://127.0.0.1:5173'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, new_url):
        return None


def direct_opener():
    # Credential requests and diagnostics never follow redirects or ambient proxies.
    return build_opener(ProxyHandler({}), NoRedirect())


def normalize_url(value: str) -> str:
    if not isinstance(value, str) or not value or any(ord(ch) <= 32 or ord(ch) >= 127 for ch in value):
        raise ValueError('URLs must be nonempty ASCII without whitespace; use an ASCII hostname.')
    if any(ch in value for ch in ('\\', '%', '?', '#')):
        raise ValueError('URLs cannot contain escapes, backslashes, query strings or fragments.')
    parts = urlsplit(value)
    host = parts.hostname
    if parts.scheme not in ('http', 'https') or not host or parts.username is not None or parts.password is not None:
        raise ValueError('Use an absolute HTTP(S) URL without embedded credentials.')
    port = parts.port  # Also rejects invalid and out-of-range ports.
    if port == 0:
        raise ValueError('Port zero is not a server endpoint.')
    try:
        address = ipaddress.ip_address(host)
        loopback = address.is_loopback
        host = address.compressed
    except ValueError:
        if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?', host) or '..' in host:
            raise ValueError('Invalid hostname.') from None
        loopback = host == 'localhost'
    if parts.scheme == 'http' and not loopback:
        raise ValueError('Non-loopback servers require HTTPS.')
    if not re.fullmatch(r'[A-Za-z0-9/_.~-]*', parts.path) or any(p in ('.', '..') for p in parts.path.split('/')):
        raise ValueError('Endpoint paths cannot contain traversal or special characters.')
    authority = f'[{host}]' if ':' in host else host
    if port is not None and port != (443 if parts.scheme == 'https' else 80):
        authority += f':{port}'
    return urlunsplit((parts.scheme, authority, parts.path, '', ''))


def make_profile(name: str, *, mcp_url: str, api_url: str, web_url: str) -> dict:
    if not isinstance(name, str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,47}', name):
        raise ValueError('Profile names must be lowercase letters, digits and hyphens, starting with a letter (max 48).')
    return {'name': name, 'mcp_url': normalize_url(mcp_url),
            'api_url': normalize_url(api_url).rstrip('/'), 'web_url': normalize_url(web_url).rstrip('/')}


def validate_profile(value: dict) -> dict:
    if not isinstance(value, dict) or set(value) != {'name', *LOCAL_URLS}:
        raise ValueError('Invalid connection profile schema.')
    return make_profile(**value)


def identity(profile: dict) -> str:
    # Name is also bound, so separate named profiles never silently share accounts.
    return hashlib.sha256(json.dumps(validate_profile(profile), sort_keys=True).encode()).hexdigest()


def token_env(profile: dict) -> str:
    return 'GSI_MCP_TOKEN_' + identity(profile).upper()


def state_path() -> Path:
    return Path.home() / '.config' / PLUGIN_NAME / 'connections.json'


def token_path(profile: dict) -> Path:
    return state_path().parent / 'credentials' / (identity(profile) + '.json')


def validate_credential_path(path: Path, *, home: Path | None = None) -> None:
    home = home or Path.home()
    try:
        components = path.parent.relative_to(home).parts
    except ValueError as error:
        raise ValueError('Private paths must remain inside the current user home directory.') from error
    if any(part in ('.', '..') for part in components):
        raise ValueError('Private paths cannot contain traversal.')
    current = home
    for component in components:
        current /= component
        try:
            details = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(details.st_mode):
            raise ValueError('Private path cannot contain a symlink.')
        if not stat.S_ISDIR(details.st_mode) or details.st_uid != os.getuid() or stat.S_IMODE(details.st_mode) & 0o022:
            raise ValueError('Private path contains an unsafe directory.')


def secure_directory(path: Path) -> None:
    validate_credential_path(path / 'placeholder')
    current = Path.home()
    for part in path.relative_to(current).parts:
        current /= part
        current.mkdir(mode=0o700, exist_ok=True)
    validate_credential_path(path / 'placeholder')
    details = path.lstat()
    if stat.S_IMODE(details.st_mode) != 0o700:
        raise ValueError('Private directory must have owner-only permissions (0700).')


def check_file(details) -> None:
    if not stat.S_ISREG(details.st_mode) or details.st_uid != os.getuid() or details.st_nlink != 1 or stat.S_IMODE(details.st_mode) != 0o600:
        raise ValueError('Private file must be an owner-only unlinked regular file (0600).')


def write_private(path: Path, content: str) -> None:
    secure_directory(path.parent)
    try:
        check_file(path.lstat())
    except FileNotFoundError:
        pass
    descriptor, name = tempfile.mkstemp(prefix='.connection-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            os.fchmod(output.fileno(), 0o600)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_private(path: Path) -> str:
    validate_credential_path(path)
    # Open the leaf without following a symlink, then validate the opened inode.
    try:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as error:
        if path.is_symlink():
            raise ValueError('Private file cannot be a symlink.') from error
        raise
    with os.fdopen(descriptor, 'r', encoding='utf-8') as source:
        check_file(os.fstat(source.fileno()))
        if stat.S_IMODE(path.parent.stat().st_mode) != 0o700:
            raise ValueError('Private directory must have owner-only permissions (0700).')
        return source.read(1_000_001)


def json_object(text: str):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON configuration key.')
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique)


def validate_state(state: dict) -> dict:
    if not isinstance(state, dict) or set(state) != {'version', 'active', 'profiles'} or type(state['version']) is not int or state['version'] != 1:
        raise ValueError('Invalid connections file version/schema.')
    if not isinstance(state['profiles'], dict):
        raise ValueError('Invalid profiles collection.')
    profiles = {}
    for name, value in state['profiles'].items():
        profile = validate_profile(value)
        if name != profile['name']:
            raise ValueError('Profile key and name disagree.')
        profiles[name] = profile
    active = validate_profile(state['active']) if state['active'] is not None else None
    return {'version': 1, 'active': active, 'profiles': profiles}


def load_state() -> dict:
    validate_credential_path(state_path())
    try:
        return validate_state(json_object(read_private(state_path())))
    except FileNotFoundError:
        local = make_profile('local', **LOCAL_URLS)
        return {'version': 1, 'active': None, 'profiles': {'local': local}}


def save_state(state: dict) -> None:
    write_private(state_path(), json.dumps(validate_state(state), indent=2) + '\n')


@contextmanager
def settings_lock():
    secure_directory(state_path().parent)
    descriptor = os.open(state_path().parent / 'connections.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        check_file(os.fstat(descriptor))
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    except BlockingIOError as error:
        raise ValueError('Another connection setup command is running; retry after it finishes.') from error
    finally:
        os.close(descriptor)


def mcp_config(profile: dict) -> dict:
    return {'mcpServers': {PLUGIN_NAME: {'type': 'http', 'url': profile['mcp_url'],
            'bearer_token_env_var': token_env(profile), 'tool_timeout_sec': 300}}}


def snapshot_files(profile: dict) -> dict[str, str]:
    profile = validate_profile(profile)
    return {
        'connection.json': json.dumps(profile, indent=2) + '\n',
        '.mcp.json': json.dumps(mcp_config(profile), indent=2) + '\n',
        'skills/intake/references/ACTIVE_CONNECTION.md': (
            '# Selected connection\n\nGenerated by connection setup. Use these addresses for this plugin installation.\n\n'
            f'- Profile: `{profile["name"]}`\n- MCP: {profile["mcp_url"]}\n'
            f'- Login API base: {profile["api_url"]}\n- Web app base: {profile["web_url"]}\n\n'
            'Append relative review/record/verification paths to the web app base, preserving any base path.\n'
            'An absolute URL on another origin is not a configured review destination; do not send credentials there.\n'
            'Changing profiles requires a new task and relaunch through the credential launcher.\n')}


def package_profile(package: Path) -> dict:
    profile = validate_profile(json_object((package / 'connection.json').read_text()))
    for relative, expected in snapshot_files(profile).items():
        if (package / relative).read_text() != expected:
            raise ValueError('Package connection files disagree; run configure.py use again.')
    return profile


def validate_token(token: str) -> None:
    if not isinstance(token, str) or not token or len(token) > 16384 or any(ord(ch) <= 32 or ord(ch) >= 127 for ch in token):
        raise ValueError('API returned an invalid session credential.')


def write_credential(profile: dict, token: str) -> None:
    validate_token(token)
    write_private(token_path(profile), json.dumps({'connection_id': identity(profile), 'token': token}))


def launch_environment(package: Path) -> dict[str, str]:
    profile = package_profile(package)
    if load_state()['active'] != profile:
        raise ValueError('Package does not match the active connection; run configure.py use and relaunch from the personal source.')
    try:
        saved = json_object(read_private(token_path(profile)))
    except FileNotFoundError as error:
        raise ValueError('No credential for this connection; run scripts/login.py first.') from error
    if not isinstance(saved, dict) or saved.get('connection_id') != identity(profile):
        raise ValueError('Credential connection binding mismatch; login again.')
    validate_token(saved.get('token'))
    environment = {key: value for key, value in os.environ.items() if key != 'GSI_MCP_TOKEN' and not key.startswith('GSI_MCP_TOKEN_')}
    environment[token_env(profile)] = saved['token']
    return environment
