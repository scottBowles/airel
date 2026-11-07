# Airel

Monorepo for a tabletop-RPG campaign app.

- `api/`: Django + Strawberry GraphQL backend (Python 3.12, Postgres + pgvector, Redis, Celery). Serves GraphQL at `http://127.0.0.1:8000/graphql/`.
- `web/`: SvelteKit frontend. **Before working in `web/`, read `web/AGENTS.md`**: it has strict rules for Houdini data loading, Svelte 5 runes and the Vite+ (`vp`) toolchain.
- `.ideas/`: roadmap. `.ideas/improvement_plan.md` describes the RAG chat pipeline in depth; `.ideas/issues/` holds numbered work items.

## Running locally

`Procfile.dev` defines the dev processes with fixed ports: `api` (8000), `web` (5173), `worker` (Celery). Start them with `api/.venv/bin/honcho -f Procfile.dev start [api|web|worker]`; with no name, all three start. Postgres and Redis must already be running.

The frontend's `web/schema.graphql` is pulled from the running backend by Houdini. A change to a GraphQL type in `api/` usually needs matching query and UI changes in `web/`, so do both in the same change.

## Pull requests

Open the PR and leave it open: the user reviews and merges every PR. When work comes in parts, branch each part from the previous part's branch, and open each PR against that branch. A hook (`bin/block-pr-merge.sh`) blocks merge and auto-merge calls.
