# Project 03 — Session Compilation

Project 03 of 08 in the RAG chat improvement roadmap and the **keystone** of the plan. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md). Sample raw logs: [`.ideas/example_logs/`](../example_logs/).

Depends on projects 01 (hygiene) and 02 (canonicalized text input).

## Goal

Define and stand up a single LLM-driven compilation task that takes a canonicalized session transcript and produces all the structured artifacts the rest of the system reads from: a prose `compiled_summary`, structured lore/decisions/threads, scene structure, entity appearances, and suggestions for new entities, aliases, and relationship changes. Every later project consumes this output.

## Decisions to nail down

1. **New `GameLog` fields.** Types, defaults, nullability, and migration story for:
   - `compiled_summary` — TextField, 400–600 words, canonical names.
   - `key_decisions` — JSONField.
   - `unresolved_threads` — JSONField, each with `origin_session_id`.
   - `lore_facts` — JSONField, each with optional `subject_entity_id`.
   - Confirm `summary`, `brief`, `synopsis`, `full_text` stay untouched as the curated/display surface.

2. **`SessionEntityAppearance` through-model.**
   - Whether it replaces or augments existing `Character.game_logs`-style m2ms across all entity types.
   - Fields: `canonical_quotes[]`, `significance` (enum or free text), `first_appearance` flag.
   - One through-model with a generic FK vs. one per entity type.
   - Migration path for existing m2m data.

3. **`compile_session` task contract.**
   - Inputs: which prior `compiled_summary` to include for continuity (immediately prior, all priors, compressed).
   - Full structured-output schema: `compiled_summary`, `scenes[]`, `key_decisions[]`, `unresolved_threads[]`, `lore_facts[]`, `entity_appearances[]`, `new_entity_candidates[]`, `alias_updates[]`, `relationship_changes[]`. Lock every field's purpose, type, cardinality, and consumer.
   - Two-pass prompt (literal outline → prose render) vs. single call vs. tool-use.
   - LLM model choice and cost ceiling per run.
   - Token-budget strategy for very long sessions (the 2022-12-19 sample is large).
   - Failure modes: partial output, schema violations, hallucinated entities, contradictions with prior compilation.

4. **Suggestion vs. direct-write policy.** For each output category, write directly or queue for human review.
   - `alias_updates[]` — apply automatically vs. confirm.
   - `new_entity_candidates[]` — always queue, never auto-create.
   - `relationship_changes[]` — feed project 06; queue or auto-write.
   - `EntitySuggestion` / `RelationSuggestion` models mirroring the existing `AILogSuggestion`.

5. **Triggering.**
   - On `GameLog` save vs. Google-Drive-pull completion vs. manual.
   - Interaction with project 01's auto-trigger and `source_revision`.
   - What invalidates a compilation: transcript change, roster change, prior-session change.

6. **Quality and observability.**
   - How compilation quality is evaluated against the project-01 eval set.
   - Side-by-side compares for prompt iteration.
   - Hallucination spot-checks and how they fail the build.

## Out of scope

How compiled artifacts get embedded and how `_assemble_context` consumes them (project 04). Entity narratives, relation summaries, agentic tool-use (projects 05–07).

## Edge cases worth pressure-testing

- Very short logs (the 2023-06-05 sample, ~800 words).
- OOC-heavy logs with extensive meta commentary.
- Logs introducing many new entities at once.
- Logs with mid-session renames (Carlos → Ego in 2019-04-04).
- Single throwaway lines that contain canonical lore ("the egg is one of the nine power cells of the Solar Cannon").
- Speculation framed as exposition ("maybe it's an eel needing healing") that must not become a lore fact.
- Long sessions that exceed a single LLM call's input budget.

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria for each of the six decision areas, including the locked structured-output schema, plus a list of independently-grabbable issues.
