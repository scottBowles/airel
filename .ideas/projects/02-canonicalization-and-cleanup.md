# Project 02 — Canonicalization & Cleanup Pipeline

Project 02 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md). Sample raw logs: [`.ideas/example_logs/`](../example_logs/) — they demonstrate the noise this project must address (pronoun drift, alias drift, mid-session renames, typos, OOC commentary, jokes/metaphors, speculation vs. canon).

Depends on project 01 (auto-trigger, `source_revision` idempotency, eval set).

## Goal

Build a preprocessing pass that turns noisy raw `GameLog.full_text` into a clean, canonicalized form suitable for downstream LLM compilation and for embedding. Run before session compilation (project 03), independent of any LLM-driven extraction.

## Decisions to nail down

1. **Typo normalization.** Deterministic fuzzy-match against the canonical entity roster + alias table to fix things like `Horthulf` → `Hrothulf`.
   - Algorithm and threshold (Levenshtein / Jaro-Winkler / trigram).
   - Where the canonical roster comes from and how it stays in sync as new entities are created.
   - Word-boundary handling, capitalization, possessives.
   - False-positive guardrails — `Hayete` and `Hiare` may be distinct entities and must not collapse. `Thiton` and `Thiten` are different and do not refer to the same entity.
   - Whether normalized text is applied in place, stored as a separate `canonical_full_text` field, or both.

2. **Alias substitution and coreference.** Substitute aliases (Carlos → Ego, after the rename point) and resolve pronouns where confidence is high enough.
   - Pure rule-based, LLM-assisted, or hybrid (rules for aliases, LLM for pronouns).
   - Handling of mid-session renames — when does a rename take effect within a single transcript?
   - How ambiguous coreferences are surfaced for human review rather than silently guessed.
   - Output shape: field on `GameLog`, separate model, or scene-level structure.

3. **OOC tagging.** Mark out-of-character content (closing meta paragraphs, parenthetical DM asides, player-name references like Greg/Joel) so compilation can skip it but raw text retains it.
   - Detection by heuristics vs. LLM classification.
   - Tag format: inline markers, separate spans, scene-level flag.
   - Downstream contract: how embedding and assembly skip / weight tagged content.

4. **Pipeline shape.**
   - Single Celery task vs. chained tasks (e.g., normalize → substitute → tag).
   - Idempotency and re-runs, including interaction with `source_revision` from project 01.
   - Behavior when the canonical roster changes — re-run all logs, selective, opt-in.
   - Code location (`rag_chat/preprocessing/`, extension of `content_processors.py`, or new module).

## Out of scope

LLM-driven session compilation itself, structured field extraction (`compiled_summary`, `key_decisions`, etc.), and embedding-strategy changes. Those are projects 03 and 04.

## Edge cases worth pressure-testing

- Familiar vs. owner name collisions (Hayete the mount vs. Hiare the familiar).
- Mid-session renames inside a single transcript.
- Near-miss aliases that should not be substituted (typo vs. intentional new entity).
- OOC content interleaved inside in-character paragraphs (parenthetical asides).
- Logs that are entirely OOC summary or entirely in-character.
- Roster changes that retroactively reinterpret old text.

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria, including measurable quality gates (e.g., "X% of pronouns resolved on the eval set", "no false-positive rewrites in the eval seed cases"), plus a list of independently-grabbable issues.
