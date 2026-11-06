# Airel

Campaign companion for a long-running tabletop RPG: a searchable database of
characters, places, items and session logs, plus a RAG chat that answers
questions about the campaign. Live at https://airel.vip.

| Folder    | What                                                                    |
| --------- | ----------------------------------------------------------------------- |
| `api/`    | Django + Strawberry GraphQL backend, Celery workers, RAG chat pipeline  |
| `web/`    | SvelteKit frontend (Svelte 5, Houdini, Tailwind v4, Vite+)              |
| `.ideas/` | Roadmap: RAG improvement plan, projects, PRDs and issues                |

See `api/README.md` and `web/README.md` for each side's details.
