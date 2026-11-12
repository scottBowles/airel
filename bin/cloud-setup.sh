#!/bin/bash
# Setup script for the Claude Code cloud environment (claude.ai/code > environment > Setup script;
# "Choose file" loads this file). Runs as root on Ubuntu 24.04 before the session starts, and its
# result is cached for about a week. It installs system tools only: per-session project setup
# (services, .env, dependencies) is bin/cloud-session-start.sh, run by a SessionStart hook.
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive

# PostgreSQL 18 + pgvector from the PGDG apt repo, to match production and local dev; the image
# ships 16. Ends with one cluster, 18/main on the default port 5432, which the session hook
# starts. If 18 can't be installed, falls back to pgvector for 16. ffmpeg is for transcription.
install_postgres() {
	install -d /usr/share/postgresql-common/pgdg &&
		curl -fsSo /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc https://www.postgresql.org/media/keys/ACCC4CF8.asc &&
		echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $(. /etc/os-release && echo "$VERSION_CODENAME")-pgdg main" >/etc/apt/sources.list.d/pgdg.list &&
		apt-get update -qq &&
		apt-get install -y -qq postgresql-18 postgresql-18-pgvector ffmpeg >/dev/null &&
		for v in $(pg_lsclusters -h | awk '{print $1}'); do pg_dropcluster --stop "$v" main; done &&
		pg_createcluster 18 main --port 5432 >/dev/null && return
	echo "cloud-setup: postgresql 18 install failed; using 16" >&2
	rm -f /etc/apt/sources.list.d/pgdg.list
	(apt-get update -qq && apt-get install -y -qq postgresql-16-pgvector ffmpeg >/dev/null) || echo "cloud-setup: pgvector install failed" >&2
}

# System libraries for headless Chromium (web/scripts/browse.ts, the verify-ui skill). The
# browser itself is preinstalled in the cloud image (see web/scripts/browse.ts); keep this
# version equal to web/package.json's.
install_chromium_deps() {
	npx -y playwright@1.64.1 install-deps chromium >/dev/null || echo "cloud-setup: chromium deps install failed" >&2
}

# Both use apt, so they run one after the other.
{ install_postgres; install_chromium_deps; } &

# Vite+ (vp) toolchain for web/. The session hook pins it to the lockfile's version.
npm install -g --silent vite-plus || echo "cloud-setup: vite-plus install failed" >&2 &

# Python for api/ (see api/.python-version). Retried: the download has timed out (504) before.
install_python() {
	for attempt in 1 2 3; do
		uv python install 3.14 && return
		echo "cloud-setup: python 3.14 install attempt $attempt failed" >&2
		sleep $((attempt * 5))
	done
	echo "cloud-setup: python 3.14 install failed" >&2
}
install_python &

wait
exit 0
