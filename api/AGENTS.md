# api/

Django project `website` (settings, URLs, Celery app). Each domain is its own Django app: `character`, `place`, `item`, `race`, `association`, `quest`, `scientia`, `nucleus` (shared base models, game logs, users, login), `transcription` (session audio → text), `rag_chat` (RAG chat pipeline).

Run everything from `api/` with the venv's binaries (`.venv/bin/python`, `.venv/bin/celery`, `.venv/bin/black`). Settings read env vars from `api/.env`; `.env.template` lists them.

## GraphQL schema

Each app exposes `Query`/`Mutation` classes from its `types/` package (or `types.py`), and `website/types.py` merges them into the one schema served at `/graphql/`. A new type or field reaches the API only once its class is in that merge. Mutations take a single `input` argument, and IDs are relay global IDs (`MAP_AUTO_ID_AS_GLOBAL_ID`). A schema change usually needs matching changes in `web/` (see root `AGENTS.md`).

## Tests

`.venv/bin/python manage.py test [app]` (Django's unittest runner; needs local Postgres).

- **Algolia:** models in each app's `index.py` are registered with Algolia, so a model save calls the Algolia API whenever `.env` has Algolia keys. Run tests with `ALGOLIA["AUTO_INDEXING"] = False`.
- **Known failures** on `main`, unrelated to your change: `graphql_jwt` imports and stale `TranscriptionService.openai` mocks. Compare against `main` before treating a failure as yours.

## Formatting

black, default settings.
