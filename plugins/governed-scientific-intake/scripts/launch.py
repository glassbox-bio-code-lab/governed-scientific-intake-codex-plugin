#!/usr/bin/env python3
"""Launch a client with only the credential for this installed connection."""
import os
from pathlib import Path
import sys
from connection import launch_environment


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: with-token.sh <command> [arguments...]', file=sys.stderr)
        return 2
    try:
        environment = launch_environment(Path(__file__).resolve().parents[1])
        os.execvpe(sys.argv[1], sys.argv[1:], environment)
    except (ValueError, OSError):
        print('Launch blocked: check active connection and private credential; run configure.py use, then login.py.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
