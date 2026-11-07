#!/bin/bash
# SessionStart hook (.claude/settings.json). Cloud sessions only; exits at once anywhere else.
# Starts Postgres and Redis, writes placeholder .env files, installs api/ and web/ dependencies
# when their manifests changed, and migrates the database. System tools come from bin/cloud-setup.sh.
# Its stdout reaches the agent's context, so it ends with a one-line status; details go to $LOG.
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/..}" || exit 1

LOG=/tmp/cloud-session-start.log
exec 3>&1 >"$LOG" 2>&1 # keep stdout (fd 3) for the status line; everything else to the log
failed=()
log() { echo "cloud-session-start: $*"; failed+=("$*"); }
sudo_() { if [ "$(id -u)" = 0 ]; then "$@"; else sudo "$@"; fi; }
as_pg() { sudo_ su postgres -c "$1"; }
hash_of() { cat "$@" 2>/dev/null | sha256sum | cut -d' ' -f1; }

# Services. The cloud cache keeps files, not processes, so start them every session.
sudo_ service postgresql start >/dev/null || log "postgresql failed to start"
sudo_ service redis-server start >/dev/null || log "redis failed to start"

# Database: a superuser role, so tests can create their database and the vector extension.
as_pg "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='airel'\"" | grep -q 1 ||
	as_pg "psql -qc \"CREATE ROLE airel LOGIN SUPERUSER PASSWORD 'airel'\"" || log "role create failed"
as_pg "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='airel'\"" | grep -q 1 ||
	as_pg "createdb -O airel airel" || log "createdb failed"

# Placeholder env files. No real keys: Algolia indexing is off, and OpenAI/R2/Google calls fail.
if [ ! -f api/.env ]; then
	cat >api/.env <<'EOF'
# Written by bin/cloud-session-start.sh for cloud sessions. Placeholder values only.
DATABASE_URL=postgres://airel:airel@127.0.0.1:5432/airel
REDIS_URL=redis://127.0.0.1:6379/0
SECRET_KEY=cloud-session-only
ALGOLIA_APPLICATION_ID=placeholder
ALGOLIA_API_KEY=placeholder
ALGOLIA_AUTO_INDEXING=false
OPENAI_API_KEY=placeholder
EOF
fi
if [ ! -f web/.env ]; then
	cat >web/.env <<'EOF'
# Written by bin/cloud-session-start.sh for cloud sessions. Placeholder values only.
PUBLIC_GRAPHQL_ENDPOINT=http://127.0.0.1:8000/graphql/
EOF
fi

# api/ dependencies, reinstalled only when the requirements or this script change.
api_hash=$(hash_of api/requirements.txt api/requirements-dev.txt "$0")
if [ "$(cat api/.venv/.deps-hash 2>/dev/null)" != "$api_hash" ]; then
	[ -x api/.venv/bin/python ] || uv venv -q --python 3.12 api/.venv
	if uv pip install -q --python api/.venv/bin/python -r api/requirements.txt -r api/requirements-dev.txt; then
		echo "$api_hash" >api/.venv/.deps-hash
	else
		log "api dependency install failed"
	fi
fi

# NLTK data that rag_chat loads at import time (same set as api/Dockerfile).
[ -d "$HOME/nltk_data/corpora/stopwords" ] ||
	api/.venv/bin/python -m nltk.downloader -q -d "$HOME/nltk_data" punkt punkt_tab averaged_perceptron_tagger averaged_perceptron_tagger_eng stopwords 2>/dev/null ||
	log "nltk data download failed"

# web/ dependencies, same rule.
web_hash=$(hash_of web/package.json web/pnpm-lock.yaml "$0")
if [ "$(cat web/node_modules/.deps-hash 2>/dev/null)" != "$web_hash" ]; then
	if (cd web && vp install --frozen-lockfile >/dev/null); then
		# The global vp must match the locked vite-plus, or vp test breaks.
		locked=$(node -p "require('./web/node_modules/vite-plus/package.json').version")
		global=$(node -p "require('$(npm root -g)/vite-plus/package.json').version" 2>/dev/null)
		[ "$locked" = "$global" ] || sudo_ npm install -g --silent "vite-plus@$locked" || log "vite-plus $locked install failed"
		echo "$web_hash" >web/node_modules/.deps-hash
	else
		log "web dependency install failed"
	fi
fi

(cd api && .venv/bin/python manage.py migrate --noinput -v0) || log "migrate failed"

# Houdini's generated runtime ($houdini), which vp check needs; vp dev/build/test also regenerate it.
(cd web && vp exec houdini generate) || log "houdini generate failed"

if [ ${#failed[@]} -eq 0 ]; then
	echo "Cloud session ready: Postgres + pgvector, Redis, api/.venv, web/node_modules, migrations, \$houdini runtime. .env files hold placeholder keys only." >&3
else
	printf 'Cloud session setup had failures (details in %s):\n' "$LOG" >&3
	printf -- '- %s\n' "${failed[@]}" >&3
fi
exit 0
