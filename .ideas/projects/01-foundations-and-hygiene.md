# Project 01 — Foundations & Hygiene

Project 01 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md). It documents the existing pipeline, models, triggering paths, and source-text characteristics.

This project has no upstream dependencies. Its outputs (auto-triggering, idempotency, eval set) are relied on by every later project.

## Goal

Prepare the ground for the rest of the roadmap. Make embedding regeneration reactive instead of manual, make it cheap to re-run safely, and stand up the measurement substrate that every later project will be evaluated against.

## Decisions to nail down

1. **Audit of `_assemble_context`** in `rag_chat/services/RAGService.py`.
   - Confirm exactly which `GameLog` fields are concatenated as today's "summaries of all logs" surface.
   - Decide which of those fields will be replaced by `compiled_summary` in project 03.
   - Decide what (if anything) needs to change now to make that swap clean later, vs. what can wait.

2. **Auto-trigger for embedding regeneration.** Today `process_content` runs only when invoked manually (admin action, GraphQL mutation, management command).
   - Choose between post_save signals, explicit lifecycle hooks, a scheduled reconciliation job, or a hybrid.
   - Decide what triggers regeneration and what skips it.
   - Decide how bulk imports / Google Drive sync flows interact with the trigger.
   - Decide failure handling (entity save succeeds but enqueue fails).

3. **Idempotent re-chunking.** Add a `source_revision` (or content hash) on `ContentChunk` so reprocessing unchanged content is a no-op.
   - Define what "the source content" is for hashing, per content type.
   - Decide how this interacts with the existing `force_reprocess` flag.
   - Decide migration path for existing rows that have no revision.

4. **Eval set.** Define a fixed list of test cases used to compare retrieval and answer quality across phases.
   - Test-case shape: query, expected source IDs, expected answer keywords / forbidden phrases, retrieval-vs-answer split.
   - Storage location and format (Django fixture, YAML in repo, dedicated model).
   - Runner: management command, pytest, both.
   - Pass/fail criteria and how regressions are reported.
   - Initial seed cases drawn from the example logs in [`.ideas/example_logs/`](../example_logs/).

## Out of scope

Canonicalization, alias substitution, OOC tagging, compiled summaries, entity narratives, relations, agentic tool-use. Those are projects 02–07.

## Edge cases worth pressure-testing

- Bulk imports (initial load, Google Drive resync) producing thousands of trigger events.
- Deletion cascades that remove a source object before its embedding task runs.
- Hash collisions or near-misses from whitespace/newline normalization.
- Signal recursion when an embedding side-effect updates a tracked field.
- Eval flakiness from non-deterministic LLM outputs.
- Ambiguous current semantics of "summaries of all logs" (which field actually flows into the prompt?).

## Definition of done for the grilling

Ready to create PRD with concrete acceptance criteria for each of the four decision areas, plus a list of independently-grabbable issues that together implement the PRD.
