# api/

Django project `website` (settings, URLs, Celery app). Each domain is its own Django app: `character`, `place`, `item`, `race`, `association`, `quest`, `scientia`, `nucleus` (shared base models, game logs, users, login), `transcription` (session audio → text), `rag_chat` (RAG chat pipeline).

Run everything from `api/` with the venv's binaries (`.venv/bin/python`, `.venv/bin/celery`, `.venv/bin/black`) or `uv run <command>`. Settings read env vars from `api/.env`; `.env.template` lists them.

## GraphQL schema

Each app exposes `Query`/`Mutation` classes from its `types/` package (or `types.py`), and `website/types.py` merges them into the one schema served at `/graphql/`. A new type or field reaches the API only once its class is in that merge. Mutations take a single `input` argument, and IDs are relay global IDs (`MAP_AUTO_ID_AS_GLOBAL_ID`). A schema change usually needs matching changes in `web/` (see root `AGENTS.md`).

## Tests

`.venv/bin/python manage.py test [app]` (Django's unittest runner; needs local Postgres).

- **Known failures:** none. The suite passes on `main`, so treat any failure as yours. (`test_safe_save_json_file_permission_error` is skipped when running as root, as cloud sessions do.)
- **Style:** test behavior through public entry points (the `/graphql/` endpoint, service methods, Celery tasks) and mock only real boundaries: OpenAI (`nucleus.ai`), R2 and Google. `association/tests.py` shows how to call GraphQL as a logged-in user.

## Cloud sessions

`bin/cloud-session-start.sh` (a SessionStart hook) starts Postgres and Redis, writes placeholder `.env` files and installs dependencies. The keys are placeholders, so OpenAI, R2 and Google calls fail: mock them in tests.

## OpenAI

All OpenAI calls go through `nucleus/ai.py` (`transcribe`, `chat_completion`, `chat_completion_text`, `embed`); don't construct `OpenAI(...)` elsewhere. The client is built on first use. Catch `ai.APIError` around calls, not `Exception`. In tests, patch `nucleus.ai` functions or inject a fake (e.g. `TranscriptionService(transcriber=...)`); `nucleus/test_ai.py` checks the module against an autospec of the SDK.

## Dependencies

uv manages them. `pyproject.toml` lists the direct dependencies (`[project] dependencies`) and the dev tools (`[dependency-groups] dev`); `uv.lock` pins every package, transitive ones included. Python is `.python-version` (3.14). The app isn't a package (`[tool.uv] package = false`), so uv never builds it. Don't edit `uv.lock` by hand; CI fails (`uv lock --check`) if it's out of date with `pyproject.toml`.

- **Install / update the venv:** `uv sync` (from `api/`). It creates or updates `.venv` to exactly what `uv.lock` lists, dev tools included, and removes anything else. This replaces `pip install -r requirements.txt`, on your machine too. `uv sync --locked` also fails instead of re-locking if the lock is stale, as CI and the Dockerfile do.
- **Add:** `uv add <package>` (app) or `uv add --dev <package>` (dev tool). No version bound unless you need one, and then say why in a comment.
- **Remove:** `uv remove <package>` (`--dev` for a dev tool).
- **Upgrade one package:** `uv lock --upgrade-package <name>` (repeatable), then `uv sync`. `uv lock --upgrade` upgrades everything; keep that to its own change.

These all update `uv.lock`, and `uv add`/`uv remove` also sync `.venv`. Commit `pyproject.toml` and `uv.lock` together.

## Formatting

black, default settings.
