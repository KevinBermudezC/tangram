## Context

The previous nine PRs built the pieces. This one is the first wire from "outside the backend" to "all of it works together". The endpoint must:

- Validate the user's prompt before any LLM call (input length cap).
- Hand off to the existing prompt composer and provider abstraction.
- Force the LLM to return a *partial* diagram (no id/timestamps/positions); the backend fills those in. This keeps the LLM's job constrained to the parts it's good at.
- Assign positions deterministically. We don't trust the LLM with spatial layout.
- Map internal `LLMError` subclasses to HTTP responses the client can branch on.
- Have a clean test path that runs without Ollama or any cloud provider being available.

## Goals / Non-Goals

**Goals:**

- A single endpoint: `POST /generate` with body `{ "prompt": str }` returning a fully populated `Diagram`.
- The LLM's response is constrained by `GeneratedDiagramContent`, not the full `Diagram` schema. That's the contract.
- Deterministic, sensible positions assigned by the backend after the LLM responds.
- HTTP error mapping that lets the frontend (future) display useful messages.
- Tests that mock the LLM and don't hit the network.

**Non-Goals:**

- Streaming. Sync return for v1; the UI can show a spinner.
- Layout intelligence beyond a column-by-type heuristic. The user will drag nodes around once the editor exists; we don't need a force-directed layout solver.
- Saving the diagram. `add-diagram-persistence-routes` covers that.
- Multi-mode support in this endpoint. Defaults to `tutor`; future endpoints can accept a `mode_id` parameter.
- Idempotency keys. The endpoint returns a new ULID every call. Re-running the same prompt produces a new diagram, deliberately.

## Decisions

### The LLM produces `GeneratedDiagramContent`, not a full `Diagram`

We define a partial schema with everything the LLM should decide (name, description, nodes, edges) and nothing it shouldn't (id, timestamps, positions). The backend completes the rest.

**Why**:
- LLMs are bad at generating stable IDs. Asking for a ULID either gets a fake one or wastes tokens.
- LLMs are bad at timestamps. Server time is the right source.
- LLMs are bad at spatial layout. They produce overlapping coordinates or all-zero positions.
- Constraining the schema shrinks the structured-output surface, which improves reliability.

**Alternatives considered**: ask the LLM for the full `Diagram` (rejected — wastes tokens on fields the backend should own, and the structured-output contract is harder to satisfy reliably).

### Deterministic auto-layout, not LLM-assigned positions

The backend assigns coordinates after the LLM responds. A simple column-by-type layout:

- `frontend` → x=80
- `auth` → x=320
- `backend` → x=560
- `cache`, `queue` → x=560 with y offset (around backend)
- `database`, `storage` → x=800
- `external_service` → top row (y=80) regardless of x

Within each column, nodes stack vertically with a fixed gap. This is not pretty for every diagram, but it's predictable, instant, and the user will reposition with the future editor.

**Alternatives considered**:
- Force-directed layout (rejected — heavier dependency, deterministic results need careful seeding, not worth the engineering for MVP).
- Ask the LLM for positions (rejected — quality is bad and tokens are wasted).
- Random positions (rejected — feels broken even if the user can drag them).

### Error mapping

```
LLMConfigError      → 503 Service Unavailable
LLMTimeoutError     → 504 Gateway Timeout
LLMRateLimited      → 429 Too Many Requests
LLMInvalidResponse  → 502 Bad Gateway
LLMInputTooLarge    → 413 Payload Too Large
LLMError (default)  → 500 Internal Server Error
ValidationError     → 422 Unprocessable Entity (Pydantic handles automatically)
```

Each response body includes a `{ "detail": "...", "code": "<rule-id>" }` shape so the frontend can branch on `code` instead of parsing the human-readable message.

**Alternatives considered**:
- Always 500 with a generic message (rejected — terrible UX for the frontend).
- Map every error to a single 4xx (rejected — conflates client and server fault).

### One async path top-to-bottom

`POST /generate` is an async route. It calls `compose_prompt` (async), `provider.generate_structured` (async), and `auto_layout` (sync, fast). No blocking I/O on the hot path.

**Alternatives considered**: sync route with `asyncio.run` (rejected — FastAPI is async-native; mixing modes is footgun territory).

### Tests use a custom `FakeLLMProvider`, not the real adapters

The fake conforms to the `LLMProvider` Protocol and returns predetermined `GeneratedDiagramContent`. We patch `get_llm` at the call site (same gotcha as the retrieval tests — `from x import y` requires patching at the importing module).

For HTTP-level tests, FastAPI's `TestClient` wraps the app and lets us call routes synchronously. We override `get_llm` via FastAPI's dependency-override mechanism for clean isolation.

**Alternatives considered**: hit a real local Ollama in tests (rejected — couples CI to model availability, not viable on GitHub Actions runners).

### ULID for the diagram id

The backend generates a ULID (`01HXYZ...`) for each generated diagram. ULIDs are lexically sortable by time and URL-safe.

**Alternatives considered**: UUID4 (rejected — unsortable; ULID is a strict win at our scale), short ID like `nanoid` (rejected — extra dep for marginal benefit).

## Risks / Trade-offs

- **Risk**: the LLM returns a `GeneratedDiagramContent` that has internally inconsistent edges (edge references a non-existent node id). → **Mitigation**: post-LLM validation runs Pydantic + a custom check that every `edge.source` and `edge.target` exists in `nodes`. Inconsistent diagrams are rejected with `LLMInvalidResponse` → 502.
- **Risk**: the LLM invents node ids that don't follow our convention. → **Mitigation**: we don't constrain node id format (the LLM can use `node-1`, `frontend`, whatever) but we *do* validate they're unique and that edges reference them.
- **Risk**: auto-layout overlaps nodes for diagrams with many components of the same type. → **Mitigation**: stack vertically with a fixed gap; readable for 1-10 nodes per column; revisit if real diagrams exceed that.
- **Risk**: a slow LLM blocks the endpoint for the full timeout. → **Mitigation**: providers honor `MAX_OUTPUT_TOKENS` cap; future streaming improves perceived latency.
- **Trade-off**: not persisting the diagram means the user can't reload it. We accept this; persistence is the very next proposal.

## Migration Plan

No migration. New endpoint, new ULID per call. Rollback = revert.

## Open Questions

- **Should we cap the number of nodes the LLM can return?** (e.g. reject if >20 nodes). Probably yes eventually, but not for v1 — let real misbehavior inform the cap.
- **Should the endpoint accept an optional `mode_id` parameter?** Easy to add, but no use case yet. Defer to the analyze proposal where modes start to differ.
- **Logging**: should we log every prompt for future eval? Tempting, but privacy concerns for self-hosted deployments. Default off; future opt-in via a config flag.
