# api/

Django project `website` (settings, URLs, Celery app). Each domain is its own Django app: `character`, `place`, `item`, `race`, `association`, `quest`, `scientia`, `nucleus` (shared base models, game logs, users, login), `transcription` (session audio → text), `rag_chat` (RAG chat pipeline).

Run everything from `api/` with the venv's binaries (`.venv/bin/python`, `.venv/bin/celery`, `.venv/bin/black`). Settings read env vars from `api/.env`; `.env.template` lists them.

## GraphQL schema

Each app exposes `Query`/`Mutation` classes from its `types/` package (or `types.py`), and `website/types.py` merges them into the one schema served at `/graphql/`. A new type or field reaches the API only once its class is in that merge. Mutations take a single `input` argument, and IDs are relay global IDs (`MAP_AUTO_ID_AS_GLOBAL_ID`). A schema change usually needs matching changes in `web/` (see root `AGENTS.md`).

## Tests

`ALGOLIA_AUTO_INDEXING=false .venv/bin/python manage.py test [app]` (Django's unittest runner; needs local Postgres).

- **Algolia:** models in each app's `index.py` are registered with Algolia, so with indexing on, every model save calls the Algolia API. `ALGOLIA_AUTO_INDEXING=false` turns that off; cloud sessions set it in their `.env`.
- **Known failures** on `main`, unrelated to your change: `graphql_jwt` imports, `test_default_initialization`, and (when running as root, as cloud sessions do) `test_safe_save_json_file_permission_error`. Compare against `main` before treating a failure as yours.

## Cloud sessions

`bin/cloud-session-start.sh` (a SessionStart hook) starts Postgres and Redis, writes placeholder `.env` files and installs dependencies. The keys are placeholders, so OpenAI, R2 and Google calls fail: mock them in tests.

## OpenAI

All OpenAI calls go through `nucleus/ai.py` (`transcribe`, `chat_completion`, `chat_completion_text`, `embed`); don't construct `OpenAI(...)` elsewhere. The client is built on first use. Catch `ai.APIError` around calls, not `Exception`. In tests, patch `nucleus.ai` functions or inject a fake (e.g. `TranscriptionService(transcriber=...)`); `nucleus/test_ai.py` checks the module against an autospec of the SDK.

## Formatting

black, default settings.
