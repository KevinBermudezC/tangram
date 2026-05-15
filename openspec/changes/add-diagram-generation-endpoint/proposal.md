## Why

Every previous proposal landed a piece. This one is the **first observable result**: a `POST /generate` endpoint that a user can `curl` from outside the backend and get a valid `Diagram` back. It ties together the schema, the LLM provider abstraction, the component vocabulary, the patterns retrieval, the rules engine, the tutor mode, and the prompt composer. Without this endpoint, all of that is internal plumbing the user cannot see.

This is also the moment the project becomes demo-able for the first time. The endpoint behind a uvicorn run + Ollama (local or cloud) → a screenshot, a tweet, a video clip.

## What Changes

- Add `backend/app/schemas/generate.py` with:
  - `GenerateRequest` — request body (`prompt: str`).
  - `GeneratedDiagramContent` — what the LLM is asked to return (nodes, edges, name, description; no id/timestamps/positions).
- Add `backend/app/services/generation/` package:
  - `layout.py` — `auto_layout(nodes)` assigns deterministic `Position`s based on node type (frontend → left column, backend → middle, database/storage → right column, etc.). MVP keeps it simple; the editor will let users reposition later.
  - `generator.py` — `generate_diagram(prompt)` orchestrates the call: compose prompt, ask LLM for `GeneratedDiagramContent`, assign positions via layout, wrap into a full `Diagram` with ULID + timestamps.
- Add `backend/app/routers/ai.py` exposing `POST /generate`. Wires the request → service → response shape, maps `LLMError` subclasses to HTTP statuses, returns the final `Diagram`.
- Register the new router in `app/main.py`.
- Add tests:
  - The generator with a fake LLM provider that returns a predetermined `GeneratedDiagramContent`.
  - The endpoint via FastAPI's `TestClient` (or async equivalent) with mocked provider.
  - Layout assignment is deterministic and produces non-overlapping positions for the seed component types.
  - Each `LLMError` subclass maps to the correct HTTP status.

This proposal does **not**:
- Add `POST /analyze`. Separate proposal.
- Persist generated diagrams. Separate proposal (`add-diagram-persistence-routes`).
- Stream the response. The first version is non-streaming for simplicity; streaming version is a Phase 2 polish.
- Generate position via the LLM. We assign positions server-side because LLMs are unreliable at spatial layout, and a deterministic backend layout is cheaper, faster, and better.

## Capabilities

### New Capabilities

- `diagram-generation`: A single HTTP endpoint and the underlying generation service that turns a free-text user request into a validated `Diagram`. Includes auto-layout for node positions, a typed error contract that maps internal `LLMError` subclasses to HTTP statuses, and a request schema that enforces input length caps before any LLM call.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `app/schemas/generate.py`, new `app/services/generation/` package, new `app/routers/ai.py`, one line in `app/main.py` to include the router, new tests.
- **Dependencies**: no new packages. Reuses everything that already exists.
- **Configuration**: no new env vars. Uses existing `LLM_PROVIDER`, `OLLAMA_*`, model selection, `MAX_INPUT_CHARS`, `MAX_OUTPUT_TOKENS`.
- **Documentation**: short "Generation endpoint" section in `backend/README.md` with a curl example.
- **Future proposals unblocked**: `add-diagram-analysis-endpoint`, `add-diagram-persistence-routes`, `establish-frontend-foundation` (the UI's first network call is `POST /generate`).
- **First demo moment**: once this merges, with Ollama set up locally or with an Ollama Cloud key, `curl -X POST localhost:8000/generate -d '{"prompt": "delivery app"}'` returns a real diagram.
