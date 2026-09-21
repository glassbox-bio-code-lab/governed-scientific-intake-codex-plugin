#!/usr/bin/env python3
"""Launch a client with only the credential for this installed connection."""
import os
from pathlib import Path
import shlex
import sys
from connection import MissingCredentialError, launch_environment


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: with-token.sh <command> [arguments...]', file=sys.stderr)
        return 2
    package = Path(__file__).resolve().parents[1]
    login = 'python3 ' + shlex.quote(str(package / 'scripts/login.py'))
    configure = 'python3 ' + shlex.quote(str(package / 'scripts/configure.py'))
    try:
        environment = launch_environment(package)
    except MissingCredentialError:
        print('Launch blocked: this connection has no saved login. Run:\n' + login
              + '\nEnter your account username and password at its prompts, then retry this launcher.'
              + '\nDo not append a password or token to the launcher command. No sudo is needed.', file=sys.stderr)
        return 1
    except (ValueError, OSError):
        print('Launch blocked: connection or private credential setup needs repair. Inspect it with:\n'
              + configure + ' show\nThen activate the intended saved profile with:\n'
              + configure + ' use <profile-name>\nLog in with:\n' + login
              + '\nRun these commands as your normal user, without sudo.', file=sys.stderr)
        return 1
    try:
        os.execvpe(sys.argv[1], sys.argv[1:], environment)
    except OSError:
        print('Client could not be started. Check the executable path passed to with-token.sh.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
