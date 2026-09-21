#!/usr/bin/env python3
"""Log into the selected Intake API without exposing credentials in chat or output."""
from __future__ import annotations

import getpass
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request

from connection import (direct_opener, load_state, package_profile, validate_profile,
                        validate_token, write_credential)


def login(username: str, password: str, profile: dict) -> str:
    profile = validate_profile(profile)
    request = Request(profile['api_url'] + '/api/v1/auth/login',
                      data=json.dumps({'username': username, 'password': password}).encode(),
                      headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    try:
        with direct_opener().open(request, timeout=10) as response:
            result = json.loads(response.read(65537).decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
        raise RuntimeError('API login failed; check the selected API and account credentials.') from error
    token = result.get('token') if isinstance(result, dict) else None
    validate_token(token)
    return token


def main() -> int:
    try:
        profile = package_profile(Path(__file__).resolve().parents[1])
        if load_state()['active'] != profile:
            raise ValueError('Run configure.py use for this connection before login.')
        print(f'Connection: {profile["name"]}\nAPI: {profile["api_url"]}\nMCP: {profile["mcp_url"]}')
        username = input('Governed Intake username: ').strip()
        password = getpass.getpass('Governed Intake password: ')
        if not username or not password:
            raise ValueError('Username and password are required.')
        token = login(username, password, profile)
        # Do not finish a login into a connection that changed while awaiting input.
        if load_state()['active'] != profile or package_profile(Path(__file__).resolve().parents[1]) != profile:
            raise ValueError('Connection changed during login; select the connection and login again.')
        write_credential(profile, token)
    except (RuntimeError, ValueError, OSError, EOFError):
        print('Login failed or connection changed. Check setup and credentials; no token was displayed.', file=sys.stderr)
        return 1
    print('Saved a private credential bound to this profile and its exact endpoints.')
    print('Fully quit Codex and relaunch through scripts/with-token.sh.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
