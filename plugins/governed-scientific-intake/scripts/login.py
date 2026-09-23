#!/usr/bin/env python3
"""Log into the selected Intake API without exposing credentials in chat or output."""
from __future__ import annotations

import getpass
import json
from pathlib import Path
import sys
import warnings
from urllib.error import HTTPError, URLError
from urllib.request import Request

from connection import (direct_opener, load_state, package_profile, validate_profile,
                        validate_token, write_credential)


class LoginError(RuntimeError):
    """A fixed, safe-to-display diagnostic with no server response content."""


def check_api(profile: dict) -> None:
    profile = validate_profile(profile)
    try:
        with direct_opener().open(Request(profile['api_url'] + '/health'), timeout=3) as response:
            if response.status != 200:
                raise LoginError('API health check failed. Check the API service before logging in.')
    except HTTPError as error:
        error.close()
        raise LoginError('API health check failed. Check the configured API address and service.') from None
    except (URLError, TimeoutError, OSError):
        raise LoginError('API is unreachable or not responding. No password was requested; restore the API service first.') from None


def login(username: str, password: str, profile: dict) -> str:
    profile = validate_profile(profile)
    request = Request(profile['api_url'] + '/api/v1/auth/login',
                      data=json.dumps({'username': username, 'password': password}).encode(),
                      headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
    try:
        with direct_opener().open(request, timeout=10) as response:
            result = json.loads(response.read(65537).decode('utf-8'))
    except HTTPError as error:
        status = error.code
        error.close()
        reason = {
            401: 'The account credentials were rejected or sign-in attempts are temporarily limited.',
            403: 'This account is not allowed to sign in here.',
            429: 'Sign-in is temporarily rate limited; wait before trying again.',
            503: 'The API account service is unavailable.',
        }.get(status, 'The API returned an unexpected HTTP status; check its address and service.')
        raise LoginError(f'API login failed (HTTP {status}). {reason}') from None
    except (URLError, TimeoutError, OSError):
        raise LoginError('API login failed: the service is unreachable or timed out. This does not establish whether your password is correct.') from None
    except ValueError:
        raise LoginError('API login failed: the service returned an invalid response.') from None
    token = result.get('token') if isinstance(result, dict) else None
    try:
        validate_token(token)
    except ValueError:
        raise LoginError('API login failed: the service did not return a valid session credential.') from None
    return token


def main() -> int:
    try:
        profile = package_profile(Path(__file__).resolve().parents[1])
        if load_state()['active'] != profile:
            raise ValueError('Run configure.py use for this connection before login.')
        print(f'Connection: {profile["name"]}\nAPI: {profile["api_url"]}\nMCP: {profile["mcp_url"]}')
        check_api(profile)
        if not sys.stdin.isatty():
            raise LoginError('Run this login command in an interactive terminal; do not pipe credentials into it.')
        username = input('Governed Intake username: ').strip()
        print('Enter your application password at the next prompt; typed or pasted characters stay hidden.', flush=True)
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            try:
                password = getpass.getpass('Governed Intake password: ')
            except getpass.GetPassWarning:
                raise LoginError('Hidden password input is unavailable. Use a normal interactive terminal.') from None
        if not username or not password:
            raise LoginError('No login was attempted: username and password must both be entered at their prompts.')
        print('Signing in…', flush=True)
        token = login(username, password, profile)
        # Do not finish a login into a connection that changed while awaiting input.
        if load_state()['active'] != profile or package_profile(Path(__file__).resolve().parents[1]) != profile:
            raise LoginError('Connection changed during login. No credential was saved; select the intended connection and log in again.')
        write_credential(profile, token)
    except LoginError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print('\nLogin cancelled. No credential was saved.', file=sys.stderr)
        return 1
    except (ValueError, OSError):
        print('Login setup or private credential storage failed. Check the selected connection and run as your normal user, without sudo.', file=sys.stderr)
        return 1
    print('Saved a private credential bound to this profile and its exact endpoints.')
    print('Login saved. Reconnect the plugin or restart the app normally. No special launcher is required.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
