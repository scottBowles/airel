#!/usr/bin/env bash
# Regenerate requirements.txt and requirements-dev.txt from the .in files with uv.
# Pins already in the .txt files are kept unless a .in change needs otherwise, so a plain
# run only adds, removes or moves what you changed. Extra arguments go to both compiles:
#   ./lock-requirements.sh --upgrade-package django   # upgrade one package
#   ./lock-requirements.sh --upgrade                  # upgrade everything
set -euo pipefail
cd "$(dirname "$0")"
compile() {
	# --universal: one lockfile for Linux (Docker, CI) and macOS/Windows dev machines.
	uv pip compile --quiet --universal --python-version 3.14 \
		--custom-compile-command ./lock-requirements.sh "$@"
}
compile requirements.in -o requirements.txt "$@"
# After requirements.txt: requirements-dev.in constrains itself to it.
compile requirements-dev.in -o requirements-dev.txt "$@"
