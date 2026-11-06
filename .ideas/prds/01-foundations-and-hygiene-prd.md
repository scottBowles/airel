# PRD: Project 01 — Foundations & Hygiene

## Problem Statement

The RAG chat embedding pipeline only regenerates when manually triggered (admin action, GraphQL mutation, or management command). This means entity and GameLog edits silently go stale — the embeddings don't reflect the current state of the data. There is no way to know whether reprocessing unchanged content will produce the same chunks (wasting API credits), and no automated way to measure whether retrieval quality has improved or regressed as the pipeline evolves.

These gaps block every downstream project in the RAG improvement roadmap: if embeddings don't auto-refresh, compiled artifacts will go stale instantly; if reprocessing isn't idempotent, bulk re-runs become expensive and unpredictable; and without an eval set, there's no way to know if later projects (canonicalization, compilation, agentic tool-use) actually improve answers.

## Solution

Ship four capabilities that together form the substrate for the rest of the roadmap:

1. **Auto-triggered embedding regeneration** — GameLog and entity saves automatically enqueue re-embedding via Celery, with a content hash guard to short-circuit when nothing meaningful changed.
2. **Idempotent re-chunking** — a new `EmbeddingRevision` model stores a content hash per source object; `process_content` compares before re-embedding.
3. **Eval infrastructure** — a pytest-based retrieval eval using pre-computed embeddings (no live OpenAI calls), asserting on recall@K and context assembly correctness.
4. **Audit documentation** — the `_assemble_context` finding (which field is "summaries of all logs") is recorded for project 03's consumption.

## User Stories

1. As a campaign curator editing an entity in admin, I want its embedding to auto-refresh so the RAG chat reflects my edits without manual intervention.
2. As a campaign curator saving a GameLog from a Google Drive sync, I want its embedding to regenerate automatically so new session content is immediately searchable.
3. As a campaign curator updating an M2M relationship (adding an association to a character, adding a place to a log), I want the affected entity's embedding to refresh with the new relationship data.
4. As a developer running `process_all_content`, I want unchanged content to be skipped automatically so I don't waste OpenAI API credits re-embedding identical text.
5. As a developer using `force_reprocess=True`, I want the hash check to be bypassed entirely so I can force a full re-embed when needed.
6. As a developer running the bulk `create_logs` management command, I want signals to be suppressed during the import loop, with a single batch re-embed at the end, so I don't flood the Celery queue with 150+ tasks.
7. As a developer running `create_logs`, I want clear documentation in the code telling me which command to run afterward to regenerate embeddings.
8. As a developer adding a new save path for entities (new mutation, new admin action), I want the auto-trigger to just work without remembering to add a manual hook.
9. As a developer modifying the embedding pipeline (new fields, new chunking strategy), I want to run the eval suite to confirm retrieval quality hasn't regressed.
10. As a developer, I want the eval suite to run in CI without any OpenAI API calls, using pre-computed embeddings.
11. As a developer working on project 03, I want to know exactly which GameLog field is currently used in the "summaries of all logs" context surface, and which call site to modify.
12. As a developer, I want orphaned `EmbeddingRevision` rows (from deleted source objects) to be cleaned up by the existing `cleanup_orphaned_chunks` task.
13. As a developer, I want the hash computation to live on the processor class so "what I embed" and "what I hash" always evolve together.
14. As a developer working on project 03, I want adding `compiled_summary` to the hash surface to be a one-method change on `GameLogProcessor`.

## Implementation Decisions

### Module 1: `EmbeddingRevision` model

- New Django model in `rag_chat/models.py`: `EmbeddingRevision(content_type FK, object_id BigInt, source_hash CharField(64), last_processed_at DateTimeField)`.
- Unique constraint on `(content_type, object_id)`.
- Data migration: create one `EmbeddingRevision` per distinct `(content_type, object_id)` in `ContentChunk` with `source_hash=None` (triggers reprocessing on next run).
- All migrations generated via `manage.py makemigrations`.

### Module 2: `compute_source_hash` on processors

- `BaseContentProcessor` gains `compute_source_hash(obj) -> str` (calls `_hash_input(obj)`, normalizes via `clean_text()`, returns `sha256` hex digest).
- Each processor subclass implements `_hash_input(obj) -> str` returning concatenated field values.
- Hash fields per content type:
  - `gamelog`: `log_text` + `title`
  - `character`: `name` + `description` + `race.name` + sorted association names
  - `place`: `name` + `description` + `place_type` + `parent.name`
  - `item`: `name` + `description`
  - `artifact`: `name` + `description` + sorted item names
  - `race`: `name` + `description`
  - `association`: `name` + `description`
- FK/M2M values hashed by their string name (not PK), sorted for M2M stability.

### Module 3: Idempotent `process_content`

- At the start of `process_content`, compute the current source hash via the processor.
- Look up `EmbeddingRevision` for this `(content_type, object_id)`.
- If `source_hash` matches and `force_reprocess=False`: return `{"status": "skipped", "reason": "hash_unchanged"}`.
- If processing succeeds: upsert `EmbeddingRevision` with new hash and `last_processed_at=now()`.
- `force_reprocess=True` bypasses the hash check entirely.

### Module 4: Auto-trigger signals

- New file `rag_chat/signals.py` with:
  - `post_save` handler for `GameLog`, `Character`, `Place`, `Item`, `Artifact`, `Race`, `Association`.
  - `m2m_changed` handler for `Character.associations`, `GameLog.places_set_in`, `Artifact.items` (fires on `post_add`, `post_remove`, `post_clear` actions).
  - Both handlers enqueue `process_content.delay(content_type_str, str(instance.pk))`.
- Registered in `rag_chat/apps.py` `ready()`.
- Comment on signal handler documenting the invariant: "Signal handlers must not write back to the source model."
- `process_content` task gains `rate_limit = "30/m"` on its decorator.
- Utility context manager `disconnect_embedding_signals()` for management commands.

### Module 5: Management command updates

- `nucleus/management/commands/create_logs.py`: wrap bulk creation loop in `disconnect_embedding_signals()` context manager.
- After the loop, enqueue `process_all_content.delay(content_types=["gamelog"], force_reprocess=False)`.
- Add comment block explaining the signal disconnect and documenting the follow-up command.

### Module 6: Eval infrastructure

- Directory: `rag_chat/eval/`.
- `cases.yaml`: each case has `id`, `query`, `query_embedding` (list of 1536 floats), `expected_source_content_type`, `expected_source_ids`, `eval_type` (retrieval / context_assembly), `difficulty`, `notes`.
- `fixtures/chunks.json`: pre-computed `ContentChunk` rows (chunk_text, embedding, metadata, content_type, object_id) for the three example logs + a handful of entities.
- `conftest.py`: pytest fixture that loads chunks.json into a test database using `ContentChunk.objects.create()`.
- `test_retrieval.py`: parametrized pytest tests. For each case: run semantic search with stored query embedding → assert expected source IDs appear in top-5 results.
- `test_context_assembly.py`: for context_assembly cases: run `_assemble_context` with retrieved results → assert expected sources appear in assembled string.
- One-off script `rag_chat/eval/generate_fixtures.py` to produce `cases.yaml` and `fixtures/chunks.json` (this one calls OpenAI — run manually, commit the output).

### Architectural decisions

- **Single Celery queue** — no second queue. Backpressure handled by task-level `rate_limit`.
- **No reconciliation safety net** — signals + hash guard provide coverage; reconciliation deferred to project 08 if needed.
- **No answer-quality assertions** — no OpenAI calls in tests. Answer quality is manual spot-checking.
- **Audit finding (no code change):** `_assemble_context` uses `GameLog.summary` for the "Narrative Summaries of All Logs" section via `GameLog.objects.all()`. Project 03 will replace `log.summary` with `log.compiled_summary` at that call site.
- **Orphan cleanup extended:** `cleanup_orphaned_chunks` task also deletes `EmbeddingRevision` rows whose source object no longer exists.

## Testing Decisions

Good tests for this project verify external behavior through the public interfaces of each module, not internal implementation details.

### What gets tested

1. **`compute_source_hash` — unit tests per processor.** For each of the 7 processor subclasses: given a model instance with known field values, assert the hash is deterministic, changes when a tracked field changes, and does NOT change for whitespace-only differences (clean_text normalization). Test M2M/FK field inclusion for character, place, artifact.

2. **`process_content` idempotency — mock-based integration test.** Mock `get_embedding` to return a fixed vector. Call `process_content` twice with the same object: first call creates chunks + revision; second call short-circuits (returns "skipped"). Then change a tracked field, call again: creates new chunks. Test `force_reprocess=True` always processes.

3. **Eval set — retrieval tests.** These ARE the eval infrastructure — they test the retrieval pipeline using pre-computed embeddings against fixture data.

### What does NOT get tested in this project

- Signal wiring (too much mocking for low value; covered by integration tests in later projects).
- Management command signal disconnect (manual verification is sufficient).
- LLM response quality (no API calls in tests).

## Out of Scope

- Canonicalization, alias substitution, OOC tagging (project 02).
- Compiled summaries, key decisions, lore facts (project 03).
- Changes to `_assemble_context` (project 03/04).
- Entity narrative summaries (project 05).
- Entity relation summaries (project 06).
- Agentic tool-use (project 07).
- Reconciliation safety-net / scheduled re-embed job (project 08).
- Any changes to the chunking strategy or chunk sizes.
- Any new fields on GameLog or entity models.

## Further Notes

- The `GameLogProcessor.extract_text` reads `gamelog.log_text`, which is a property preferring `full_text` with a Google Doc fallback. The hash should use whatever `log_text` resolves to at hash time.
- The `_assemble_context` audit finding: line 551 of `rag_chat/services/RAGService.py` formats `f"Log {log.session_number} — {log.title}:\n{log.summary}"` for ALL logs. The full-text section (line 581) uses `log.full_text` for top-ranked retrieved logs within token budget. Project 03 replaces the summary surface; the full-text surface stays.
- Signal recursion is naturally self-terminating: `process_content` writes to `ContentChunk` (not source models), so the chain never loops. This invariant should be documented in a comment on the signal handler.
- When project 03 adds `compiled_summary` to `GameLog`, the only changes needed in this module are: (a) add `compiled_summary` to `GameLogProcessor._hash_input()`, and (b) update `GameLogProcessor.process_content()` to embed the new field. The signal + revision infrastructure works unchanged.
