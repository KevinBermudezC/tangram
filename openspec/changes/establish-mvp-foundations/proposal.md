## Why

Tangram has a schema (`docs/schema/diagram-v0.md`) but no runnable backend, no defined storage strategy, and no reproducible setup. Contributors who clone the repo today cannot start it. We need a working baseline — an HTTP service, a storage layer, and a one-command setup — so subsequent feature proposals (LLM providers, patterns library + RAG, `/generate`, `/analyze`, editor) have something to build on.

This proposal establishes that baseline. It does not add user-facing features.

## What Changes

- Add `backend/` FastAPI service with project layout (`core`, `middlewares`, `routers`, `schemas`, `tables`, `services`).
- Add Pydantic schemas under `backend/app/schemas/diagram.py` mirroring `docs/schema/diagram-v0.md` (`Diagram`, `Node`, `Edge`, `Message` and supporting enums).
- Add `app/core/config.py` with `pydantic-settings` for environment-driven config (data directory, Chroma path, LLM provider, embedder, guardrail caps).
- Add `GET /health` endpoint as a smoke test.
- Adopt **filesystem storage** for diagrams: each diagram is a JSON file under `<DATA_DIR>/diagrams/<id>.json`. No relational database in MVP.
- Adopt **Chroma** as the file-based vector store for the patterns library: a folder under `<CHROMA_PATH>` that holds embeddings. Bundleable in the repo with pre-computed defaults.
- Add `backend/Dockerfile` and `backend/.env.example` for opt-in production deployments. **Docker is not required for local development.**
- Add `backend/README.md` documenting the local dev loop (clone → `pip install -e ".[dev]"` → `uvicorn` → `curl /health`).
- Update top-level `README.md` quick-start so the documented commands actually work.
- No public APIs beyond `/health` are added in this proposal. `/generate`, `/analyze`, the patterns library content, and the editor live in future proposals.

## Capabilities

### New Capabilities

- `backend-runtime`: HTTP service shape — FastAPI app factory, configuration surface, health check, project structure conventions, and the contract that all future routers/services build on.
- `developer-environment`: Frictionless local development — `pip install -e ".[dev]"` plus `uvicorn` brings up the backend; `.env.example` documents the configuration surface; backend README documents the loop. **No Docker dependency for MVP.**
- `persistence-layer`: Storage strategy — filesystem JSON for diagrams (user-generated documents), Chroma for patterns embeddings (project-curated knowledge). Defines the shape both stores must conform to and where they live on disk.

### Modified Capabilities

<!-- None. The diagram schema is already accepted (see docs/schema/diagram-v0.md) but
     is not yet represented as an OpenSpec capability. It will be moved into
     openspec/specs/diagram-schema/ in a separate, follow-up proposal so this
     change stays focused on runtime, environment, and storage. -->

## Impact

- **Code**: new top-level `backend/`. No existing code is modified.
- **Dependencies**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, pydantic-settings, ChromaDB. LLM provider SDKs (anthropic, openai, ollama, httpx) are declared but unused until the provider-abstraction proposal lands.
- **Infrastructure**: no required services. Docker is offered as opt-in for production deployments only; contributors can develop locally without it.
- **Documentation**: `backend/README.md` (new). Top-level `README.md` quick-start gains accuracy.
- **Future proposals unblocked**: `add-llm-provider-abstraction`, `add-patterns-library-and-rag`, `add-anti-pattern-rules`, `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint`, `add-diagram-persistence-routes`, `establish-frontend-foundation`.
