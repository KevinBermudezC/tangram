## Context

`/generate` proved the text → diagram path. `/analyze` is the inverse and the point of the tutor: diagram → critique. Almost everything it needs already exists:

- `check_all(diagram)` → `list[Finding]` — deterministic, fast, no LLM.
- `compose_prompt(user_request, diagram=..., mode_id="tutor")` — already injects the diagram, the component vocabulary, retrieved patterns, *and* the rule findings into the system prompt (see `_findings_block_safe`).
- `LLMProvider.generate(messages)` → `str` — the plain-text method we want for prose feedback (`/generate` used `generate_structured`; `/analyze` does not need structured output).
- The `LLMError` → HTTP mapping and `TangramHTTPError` contract in `app/routers/ai.py`.

The work is a thin service that wires these together plus a new route. No new subsystem.

## Goals / Non-Goals

**Goals:**

- A single endpoint: `POST /analyze` with body `{ "diagram": Diagram, "mode_id"?: str }` returning `{ "findings": Finding[], "feedback": str }`.
- `findings` is the verbatim output of `check_all` — deterministic, independent of the LLM, returned even if the LLM call fails (see open question).
- `feedback` is prose from the LLM tutor, grounded in those findings.
- Read-only: `/analyze` never writes to storage or mutates the input.
- Input-size guard before any LLM call.
- HTTP error mapping shared with `/generate`.
- Tests that mock the LLM and never hit the network.

**Non-Goals:**

- Streaming feedback. Sync return for v1; the UI shows a spinner. Streaming is a shared Phase 2 item with `/generate`.
- New rules. The five built-ins are consumed as-is.
- Conversational follow-up ("why is that bad?"). That's `add-chat-about-diagram`.
- Multi-mode content. `mode_id` is accepted but `tutor` is the only shipped mode; unknown modes surface as a config-class error.
- Persisting the analysis result.

## Decisions

### Feedback is plain text via `generate`, not structured output

`/generate` constrained the LLM with `GeneratedDiagramContent` because it needed a machine-consumable diagram. `/analyze`'s feedback is for a human to read, so we call `LLMProvider.generate(messages)` and return the string as-is.

**Why**: structured output here would be ceremony with no consumer. The findings already carry the machine-readable structure (rule_id, severity, node_ids); the LLM's job is the narrative *around* them.

**Alternatives considered**: ask the LLM for structured `{ summary, per_finding_explanations[] }` (rejected for v1 — over-engineered before we know the panel's UI needs; revisit if the frontend wants per-finding prose anchored to nodes).

### Findings come from `check_all`, not from the LLM

The deterministic engine is the source of truth for *what* is wrong. The LLM only explains. This keeps findings reproducible and testable without a model, and means a flaky/slow LLM never corrupts the structural verdict.

Note: `compose_prompt` *also* calls `check_all` internally to build the findings section of the system prompt. So `/analyze` runs the rules twice per request — once for the response payload, once inside composition. The duplication is cheap (pure graph checks over a small diagram) and keeps the composer's interface clean. We accept it rather than threading pre-computed findings through `compose_prompt`.

### The user message for composition

`compose_prompt` takes a `user_request` string. `/analyze` has no free-text request — the "request" is implicitly "review this diagram." We pass a fixed instruction string (e.g. `"Review the following architecture diagram and explain any issues."`) as `user_request`, and the diagram via the `diagram=` argument. The composer appends the serialized diagram to the user message automatically (`_user_message_content`).

**Alternatives considered**: add an optional free-text `note` field to `AnalyzeRequest` so the user can steer the review (rejected for v1 — that's chat territory; keep `/analyze` a pure "review everything" pass).

### Input-size guard mirrors `/generate`

`/generate` checks `len(prompt) > MAX_INPUT_CHARS`. `/analyze`'s input is a diagram, so we guard on the serialized JSON length: if `len(diagram.model_dump_json())` exceeds `MAX_INPUT_CHARS`, return 413 with `code: "diagram_too_large"` before composing or calling the LLM. The composed system prompt can still independently trip `LLMInputTooLarge` (vocabulary + patterns inflate it), which maps to 413 `llm_input_too_large` — same as `/generate`.

### Error mapping is shared, not duplicated

Rather than copy the seven-branch `try/except` from `post_generate`, factor the mapping into a small helper in `app/routers/ai.py` (e.g. `_raise_for_llm_error(e)`) that both routes use. This removes drift risk — today the two routes would have identical mappings and could silently diverge.

**Alternatives considered**: copy-paste the except ladder (rejected — two copies of a seven-way map is exactly the kind of thing that rots).

### Mode resolution errors

`compose_prompt` raises `ModeNotFoundError` (a `KeyError`) for an unknown `mode_id`. We map it to 422 (`code: "unknown_mode"`) since it's caller-supplied input, distinct from the `LLMError` family.

## Risks / Trade-offs

- **Risk**: the LLM ignores the findings and invents its own critique. → **Mitigation**: the tutor system prompt already instructs the model to refer to the static-analysis findings explicitly (`_findings_block_safe` says "refer to them explicitly when relevant"). We can't hard-guarantee it; findings in the response are the deterministic backstop.
- **Risk**: a clean diagram (zero findings) yields vague or empty feedback. → **Mitigation**: the findings block emits "No structural issues detected" so the model has something concrete to affirm; we test the clean-diagram path explicitly.
- **Risk**: rules run twice per request. → **Trade-off**: accepted; the checks are pure and cheap relative to the LLM call that dominates latency.
- **Risk**: a very large diagram inflates the prompt past the model's context. → **Mitigation**: the `diagram_too_large` guard plus the composer's own `LLMInputTooLarge` path both return 413.

## Migration Plan

No migration. New endpoint, read-only, no schema or storage changes. Rollback = revert.

## Open Questions

- **If the LLM call fails, should we still return the findings with a 200 and an empty/placeholder `feedback`, or fail the whole request with the mapped error?** v1 chooses **fail the request** (mapped `LLMError` status) for a simple, predictable contract — `findings`-only success would force the frontend to handle a partial-success shape. Revisit if users want the structural verdict even when the model is down.
- **Should `feedback` have a length cap on the way out?** Bounded by `MAX_OUTPUT_TOKENS` already; no separate char cap for v1.
- **Should `mode_id` be validated against the shipped modes at the schema layer (enum) rather than at composition time?** Deferred — keeping it an open string avoids churn when `senior`/`brainstorm` land.
