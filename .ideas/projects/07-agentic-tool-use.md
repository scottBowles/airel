# Project 07 — Agentic Tool-Use for Chat

Project 07 of 08 in the RAG chat improvement roadmap, in the `dnd-api` repo. Full roadmap and current-state context: [`.ideas/improvement_plan.md`](../improvement_plan.md).

Depends on projects 03, 05, and 06 (compiled artifacts must exist for the agent to navigate by them). Gated on the project-01 eval set showing compilation quality is good enough.

## Goal

Replace today's single-shot retrieval-then-answer with an agentic loop: the model receives a lean, summary-heavy initial context and pulls fidelity (full logs, scenes, relations) only when needed via tool calls. Bound cost and latency. Maintain a non-agentic fallback path.

## Decisions to nail down

1. **Refactor of `RAGService.generate_response` for tool-calling.**
   - Single-shot vs. agentic per request: heuristic, user opt-in, or always.
   - Provider and model choice for tool-calling (current path uses `gpt-3.5-turbo`).
   - Streaming behavior around tool calls: stream final answer only, stream tool-call deltas, or both.
   - Backwards compatibility — keep a non-agentic path for the eval set and as fallback.

2. **Initial context shape.**
   - Conversation history (existing path).
   - `compiled_summary` for _all_ logs as a rolling table-of-contents — and how it scales to hundreds of sessions.
   - Top-k retrieved entity `narrative_summary`.
   - Relevant `EntityRelation.compiled_summary`.
   - Stable IDs for everything the agent might subsequently fetch.

3. **Tool surface.** Signatures, return shapes, and limits for:
   - `fetch_full_log(ids)` — raw `full_text`.
   - `fetch_scene(session_id, scene_index)` — single canonicalized scene.
   - `fetch_entity(id)` — full record plus `narrative_summary`.
   - `fetch_relation(entity_a, entity_b)` — relation summary.
   - `fetch_unresolved_threads(filter?)` — open mysteries / clues.
   - `fetch_lore_facts(subject_id?)` — canonical lore claims.
   - Plus any additional tools (search, date filter, entity-type filter).

4. **Operational guardrails.**
   - Max tool-call rounds.
   - Max total tokens and max LLM dollar cost per request.
   - Retry policy and tool-failure handling.
   - Cheap query-classification heuristic to skip the agent for chitchat.

5. **Sources and citations.**
   - How `SourcesModel` is populated when the agent fetches things.
   - How citations are surfaced to the user, especially across multiple tool-fetched artifacts.

6. **Observability.**
   - What's logged per request: tool calls, latency, cost, tokens.
   - How agent runs feed the project-01 eval set and the project-08 dashboards.

## Out of scope

Improvements to the compilation outputs themselves (handled in 03/05/06). Dashboards and CI integration (project 08).

## Edge cases worth pressure-testing

- Agent loops on the same fetch repeatedly.
- Agent ignores available tools and answers from initial context only.
- Agent over-fetches and blows the cost ceiling.
- No relevant logs exist; agent must say so without hallucinating.
- Conflicting facts between fetched artifacts.
- Streaming UX when a tool call interrupts the answer.
- Realistic queries from the example logs to test the tool surface end-to-end:
  - "what is the egg?"
  - "what's the clew?"
  - "what's between Hrothulf and Bruno?"
  - "what happened in Heorot?"

## Definition of done for the grilling

Ready to create a PRD with concrete acceptance criteria covering when agentic mode runs, the locked tool surface, guardrails with numerical bounds, citation behavior, and observability hooks, plus a list of independently-grabbable issues.
