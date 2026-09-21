#!/usr/bin/env bash
# Credentials stay inside the Python launcher and are never printed or shell-expanded.
set -euo pipefail
script_directory="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$script_directory/launch.py" "$@"
