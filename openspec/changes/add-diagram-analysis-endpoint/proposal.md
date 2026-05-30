## Why

`POST /generate` turns text into a diagram, but Tangram's whole premise is teaching: a user should be able to draw or edit an architecture and be told what's wrong and *why*. Today the anti-pattern rules engine, the `Finding` schema, the tutor mode, and the prompt composer all exist — but nothing exposes them as feedback on an existing diagram. `POST /analyze` is the endpoint that closes that loop and makes the tutor experience real. It is roadmap MVP item #12 and the backend half of the frontend's AI chat/feedback panel.

## What Changes

- Add `backend/app/schemas/analyze.py` with:
  - `AnalyzeRequest` — request body (`diagram: Diagram`, optional `mode_id: str = "tutor"`).
  - `AnalyzeResponse` — response body (`findings: list[Finding]`, `feedback: str`).
- Add `backend/app/services/analysis/` package:
  - `analyzer.py` — `analyze_diagram(diagram, mode_id)` orchestrates: run `check_all(diagram)` for the deterministic findings, compose a tutor prompt (diagram + findings already wired in `compose_prompt`), ask the LLM for prose feedback, return both.
- Extend `backend/app/routers/ai.py` with `POST /analyze`. Reuses the exact `LLMError` → HTTP status mapping and `TangramHTTPError` contract already established by `/generate`.
- Add an input-size guard: reject diagrams whose serialized size exceeds the configured input cap before any LLM call (the analog of `/generate`'s prompt-length check).
- Add tests:
  - The analyzer with a fake LLM provider returning predetermined feedback, asserting findings come straight from `check_all` and feedback from the LLM.
  - The endpoint via `TestClient` with a mocked provider, including the clean diagram case (no findings) and the violating diagram case.
  - Each `LLMError` subclass maps to the correct HTTP status (shared behaviour with `/generate`).
  - An oversized diagram returns the input-too-large contract before the LLM is called.

This proposal does **not**:
- Stream the feedback. v1 returns the full string in one response; streaming is a Phase 2 polish (shared with `/generate`).
- Add new rules. It consumes the existing five built-in rules as-is; more rules are a separate Phase 2 track.
- Mutate or persist the diagram. `/analyze` is read-only — it never writes to storage.
- Add `senior`/`brainstorm` modes. It accepts `mode_id` but `tutor` is the only mode shipped today; the parameter is forward-looking.

## Capabilities

### New Capabilities

- `diagram-analysis`: A single HTTP endpoint and the underlying analysis service that takes an existing `Diagram` and returns deterministic rule findings plus an LLM-generated prose critique. Includes an input-size guard, the shared typed error contract that maps internal `LLMError` subclasses to HTTP statuses, and a read-only guarantee (no persistence, no mutation).

### Modified Capabilities

<!-- None. The rules engine, prompt composer, and LLM abstraction are consumed as-is. -->

## Impact

- **Code**: new `app/schemas/analyze.py`, new `app/services/analysis/` package, new route in the existing `app/routers/ai.py`, new tests. No change to `app/main.py` (the `ai` router is already registered).
- **Dependencies**: none. Reuses `Finding`, the rules registry, the LLM provider abstraction, and `compose_prompt` (which already accepts a `diagram` and emits the findings section).
- **Configuration**: no new env vars. Uses existing `LLM_PROVIDER`, model selection, `MAX_INPUT_CHARS`, `MAX_OUTPUT_TOKENS`.
- **Documentation**: short "Analysis endpoint" section in `backend/README.md` with a curl example.
- **Frontend unblocked**: the AI chat/feedback panel can call `POST /analyze` for real findings instead of the local mock; pairs with the future `add-chat-about-diagram` for conversational follow-up.
