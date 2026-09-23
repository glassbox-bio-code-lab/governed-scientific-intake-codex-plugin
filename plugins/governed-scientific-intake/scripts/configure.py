#!/usr/bin/env python3
"""Save, inspect, check and activate Governed Intake connection profiles."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request

from connection import (PLUGIN_NAME, direct_opener, json_object, load_state, make_profile,
                        save_state, settings_lock, snapshot_files, validate_profile)


def marketplace_source(package: Path | None = None) -> tuple[str, Path]:
    # A standalone local Git marketplace keeps this package under plugins/.
    # The existing personal installation keeps it under ~/plugins/.
    package = package or Path(__file__).resolve().parents[1]
    repository = package.parents[1]
    repository_marketplace = repository / '.agents/plugins/marketplace.json'
    if repository_marketplace.is_file():
        marketplace = repository_marketplace
        source = repository / 'plugins' / PLUGIN_NAME
        if package != source:
            raise ValueError('Run setup from the registered local plugin source, not an installed cache.')
    else:
        marketplace = Path.home() / '.agents/plugins/marketplace.json'
        source = Path.home() / 'plugins' / PLUGIN_NAME
    data = json_object(marketplace.read_text())
    name = data.get('name')
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', name):
        raise ValueError('Invalid local marketplace name.')
    entries = [entry for entry in data.get('plugins', []) if entry.get('name') == PLUGIN_NAME]
    if len(entries) != 1 or entries[0].get('source', {}).get('source') != 'local':
        raise ValueError('Register this plugin once in a local marketplace before setup.')
    relative = entries[0]['source'].get('path')
    if relative != f'./plugins/{PLUGIN_NAME}':
        raise ValueError('Local marketplace source must point to ./plugins/' + PLUGIN_NAME)
    if source.is_symlink():
        raise ValueError('Plugin source cannot be a symlink.')
    manifest = json_object((source / '.codex-plugin/plugin.json').read_text())
    if manifest.get('name') != PLUGIN_NAME:
        raise ValueError('Marketplace source has a different plugin identity.')
    return name, source


def activate(profile: dict, state: dict) -> None:
    profile = validate_profile(profile)
    marketplace, source = marketplace_source()
    manifest_path = source / '.codex-plugin/plugin.json'
    manifest = json_object(manifest_path.read_text())
    base = manifest['version'].split('+')[0]
    manifest['version'] = base + '+codex.' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')
    generated = snapshot_files(profile, str(source / 'scripts/auth_headers.py'))
    generated['.codex-plugin/plugin.json'] = json.dumps(manifest, indent=2) + '\n'
    before = {}
    for relative in generated:
        target = source / relative
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent != Path('/')):
            raise ValueError('Generated plugin paths cannot contain symlinks.')
        before[relative] = target.read_bytes() if target.exists() else None
    try:
        for relative, content in generated.items():
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        result = subprocess.run(['codex', 'plugin', 'add', f'{PLUGIN_NAME}@{marketplace}', '--json'],
                                capture_output=True, text=True, timeout=60, check=False)
        if result.returncode:
            raise ValueError('Codex plugin installation failed; the active connection was not changed.')
        installed = json_object(result.stdout)
        if installed.get('version') != manifest['version'] or installed.get('pluginId') != f'{PLUGIN_NAME}@{marketplace}':
            raise ValueError('Codex returned a different installed plugin/version.')
        cache = Path(installed['installedPath'])
        for relative, content in generated.items():
            if (cache / relative).read_text() != content:
                raise ValueError('Installed connection snapshot failed verification.')
        updated = {**state, 'active': profile}
        save_state(updated)
    except Exception:
        for relative, original in before.items():
            target = source / relative
            if original is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(original)
        # A partially installed cache may remain after an ambiguous CLI failure.
        # Launch-time binding checks reject it unless it matches the active state.
        raise
    print(f'Activated {profile["name"]}; installed {manifest["version"]}.')
    print('Reconnect the plugin or restart the app normally, then start a new task. No special launcher is required.')
    print('If this connection has no credential yet, run scripts/login.py in your terminal first.')


def check_endpoints(profile: dict) -> bool:
    """Read-only probes without passwords, tokens, redirects or proxy inheritance."""
    success = True
    targets = {'API health': profile['api_url'] + '/health',
               'MCP': profile['mcp_url'], 'Web app': profile['web_url'] + '/'}
    for label, url in targets.items():
        try:
            with direct_opener().open(Request(url, method='GET'), timeout=5) as response:
                status = response.status
        except HTTPError as error:
            status = error.code
            error.close()
        except (URLError, TimeoutError, OSError):
            print(f'{label}: connection failed')
            success = False
            continue
        expected = status == 200 if label != 'MCP' else status in (200, 400, 401, 403, 405, 406)
        success = success and expected
        print(f'{label}: HTTP {status}' + (' (reachable)' if expected else ' (unexpected; redirects are not followed)'))
    print('Reachability does not verify server identity, account access, compatible tools or a complete intake flow.')
    return success


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    save = commands.add_parser('set', help='Save/update a named profile without switching the active connection')
    save.add_argument('name')
    for option in ('mcp-url', 'api-url', 'web-url'):
        save.add_argument('--' + option, required=True)
    use = commands.add_parser('use', help='Select a saved profile, regenerate and reinstall the personal plugin')
    use.add_argument('name')
    commands.add_parser('list', help='Show saved profile names and the active connection')
    for verb in ('show', 'check'):
        command = commands.add_parser(verb, help='Show addresses' if verb == 'show' else 'Probe endpoints without credentials')
        command.add_argument('name', nargs='?', help='Defaults to the active connection, or the saved local profile')
    args = parser.parse_args()
    try:
        if args.command in ('set', 'use'):
            with settings_lock():
                state = load_state()
                if args.command == 'set':
                    profile = make_profile(args.name, mcp_url=args.mcp_url, api_url=args.api_url, web_url=args.web_url)
                    state['profiles'][args.name] = profile
                    save_state(state)
                    print(f'Saved {args.name}. Run configure.py use {args.name} to activate it.')
                else:
                    activate(state['profiles'][args.name], state)
        else:
            state = load_state()
            if args.command == 'list':
                print('Active: ' + (state['active']['name'] if state['active'] else '(not configured)'))
                for name, value in state['profiles'].items():
                    marker = ' (active)' if value == state['active'] else ''
                    print(name + marker)
                print('Saved edits do not affect the active snapshot until use succeeds.')
            else:
                profile = state['profiles'][args.name] if args.name else state['active'] or state['profiles']['local']
                if args.command == 'show':
                    print(json.dumps(profile, indent=2))
                elif not check_endpoints(profile):
                    return 1
        return 0
    except KeyError:
        print('Profile or required configuration field was not found.', file=sys.stderr)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        # Never echo an untrusted HTTP response, credential, or CLI output.
        print(str(error) if isinstance(error, ValueError) and not isinstance(error, json.JSONDecodeError)
              else 'Connection setup failed; check local files and Codex installation.', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
