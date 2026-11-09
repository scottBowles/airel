# api/

Django project `website` (settings, URLs, Celery app). Each domain is its own Django app: `character`, `place`, `item`, `race`, `association`, `quest`, `scientia`, `nucleus` (shared base models, game logs, users, login), `transcription` (session audio → text), `rag_chat` (RAG chat pipeline).

Run everything from `api/` with the venv's binaries (`.venv/bin/python`, `.venv/bin/celery`, `.venv/bin/black`). Settings read env vars from `api/.env`; `.env.template` lists them.

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

Direct dependencies live in `requirements.in` (the app) and `requirements-dev.in` (dev tools). `requirements.txt` and `requirements-dev.txt` are lockfiles generated from them by `./lock-requirements.sh` (`uv pip compile`): every package, transitive ones included, is pinned. Don't edit the `.txt` files by hand; CI reruns the script and fails if they differ.

- **Add:** put the package in the right `.in` file (no version unless you need a bound, and then say why in a comment), run `./lock-requirements.sh`, then `uv pip sync --python .venv/bin/python requirements.txt requirements-dev.txt`.
- **Upgrade one package:** `./lock-requirements.sh --upgrade-package <name>` (repeatable), then sync. `--upgrade` upgrades everything; keep that to its own change.
- **Remove:** delete it from the `.in` file, rerun the script, then sync (sync also uninstalls what the lockfiles no longer list).

Commit the `.in` and `.txt` changes together.

## Formatting

black, default settings.
