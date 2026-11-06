# Issue 01-06: Build eval infrastructure for retrieval regression testing

**Project:** 01 — Foundations & Hygiene
**PRD:** [`prds/01-foundations-and-hygiene-prd.md`](../prds/01-foundations-and-hygiene-prd.md)
**Depends on:** None (can be worked in parallel with 01-01 through 01-05)
**Blocks:** None (but used by every later project to measure improvement)

## Summary

Build a pytest-based retrieval evaluation suite that uses pre-computed embeddings (no live OpenAI calls) to assert that the right sources surface for a fixed set of queries. This is the measurement substrate for the entire RAG improvement roadmap.

## Acceptance Criteria

### Directory structure

- [ ] `rag_chat/eval/` directory with:
  - `cases.yaml` — eval case definitions.
  - `fixtures/chunks.json` — pre-computed `ContentChunk` data (chunk text, embedding vectors, metadata).
  - `fixtures/source_objects.json` — minimal source object data (GameLog, Character, etc.) needed to make generic FKs resolve.
  - `generate_fixtures.py` — one-off script that calls OpenAI to produce `cases.yaml` and fixture files. Run manually, output committed.
  - `conftest.py` — pytest fixtures that load the JSON data into a test database.
  - `test_retrieval.py` — retrieval recall tests.
  - `test_context_assembly.py` — context assembly tests.

### Eval case shape (`cases.yaml`)

- [ ] Each case has:
  - `id` — unique string identifier (e.g., `"solar-cannon-power-cell"`).
  - `query` — natural language question.
  - `query_embedding` — list of 1536 floats (pre-computed).
  - `expected_source_content_type` — string (e.g., `"gamelog"`, `"character"`).
  - `expected_source_ids` — list of object IDs that should appear in results.
  - `eval_type` — `"retrieval"` or `"context_assembly"`.
  - `difficulty` — `"easy"`, `"medium"`, `"hard"`.
  - `notes` — human-readable explanation of what the case tests.

### Test behavior

- [ ] `test_retrieval.py`: parametrized over all `eval_type="retrieval"` cases. For each: perform cosine similarity search using stored query embedding → assert all `expected_source_ids` appear in top-5 results (recall@5).
- [ ] `test_context_assembly.py`: parametrized over all `eval_type="context_assembly"` cases. For each: run retrieval → call `_assemble_context` → assert expected source content appears in the assembled string.
- [ ] Zero OpenAI API calls during test runs.
- [ ] Tests pass with `pytest rag_chat/eval/`.

### Seed cases

- [ ] Minimum 8 cases covering these categories:
  1. Lore extraction (e.g., Solar Cannon power cell from 2019-04-04 log)
  2. Alias resolution (e.g., Carlos → Ego)
  3. Entity state (e.g., Hrothulf's family)
  4. Location exploration (e.g., Thestal Halls of Heorot)
  5. Combat recall (e.g., bot fight on the island)
  6. Cross-session thread (e.g., Solar Cannon across multiple logs)
  7. Character relationship (e.g., Ego and Atchi)
  8. OOC filtering (e.g., "What happened in room 1?" should not surface DM meta-commentary)
  9. Negative case (e.g., query about something that doesn't exist)

### Fixture generation

- [ ] `generate_fixtures.py` script that:
  - Takes the three example logs from `.ideas/example_logs/` as source text.
  - Runs them through the existing `GameLogProcessor` to produce chunks.
  - Calls `get_embedding` for each chunk and each eval query.
  - Writes the results to `fixtures/chunks.json` and populates `query_embedding` in `cases.yaml`.
  - Includes clear instructions in a docstring for how to re-run it when the chunking strategy changes.

## Notes

- The fixture data is derived from the three example logs. This is a small but representative sample covering lore, exploration, and combat.
- When future projects change the chunking strategy (e.g., project 04 switches to compiled-artifact chunks), re-run `generate_fixtures.py` to re-baseline the eval data.
- The eval does NOT test answer quality (no LLM response generation). Answer quality is validated via manual spot-checks.
- Pre-computed embeddings make these tests fully deterministic and CI-friendly.
