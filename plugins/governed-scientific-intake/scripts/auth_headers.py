#!/usr/bin/env python3
"""Supply native HTTP MCP headers from the selected private account credential.

Stdout is the host's credential channel, never user-facing diagnostic output.
"""
import json
from pathlib import Path
import sys

from connection import MissingCredentialError, saved_token


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError('Expected a connection binding.')
        token = saved_token(Path(__file__).resolve().parents[1], sys.argv[1])
    except MissingCredentialError:
        print('Glassbox MCP has no saved login. Run the plugin scripts/login.py, then reconnect.', file=sys.stderr)
        return 1
    except Exception:
        print('Glassbox MCP credential could not be loaded. Check the selected connection and login again.', file=sys.stderr)
        return 1
    print(json.dumps({'Authorization': 'Bearer ' + token}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
