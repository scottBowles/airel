#!/bin/bash
# Setup script for the Claude Code cloud environment (claude.ai/code > environment > Setup script;
# "Choose file" loads this file). Runs as root on Ubuntu 24.04 before the session starts, and its
# result is cached for about a week. It installs system tools only: per-session project setup
# (services, .env, dependencies) is bin/cloud-session-start.sh, run by a SessionStart hook.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

# pgvector for the preinstalled PostgreSQL 16; ffmpeg for transcription (pydub).
(apt-get update -qq && apt-get install -y -qq postgresql-16-pgvector ffmpeg >/dev/null) || echo "cloud-setup: pgvector install failed" >&2 &

# Vite+ (vp) toolchain for web/. The session hook pins it to the lockfile's version.
npm install -g --silent vite-plus || echo "cloud-setup: vite-plus install failed" >&2 &

# Python for api/ (see api/runtime.txt).
uv python install 3.12 || echo "cloud-setup: python 3.12 install failed" >&2 &

wait
exit 0
