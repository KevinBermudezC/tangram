## Why

Tangram has a schema (`docs/schema/diagram-v0.md`) but no runnable backend or reproducible development environment. Contributors who clone the repo today cannot start it. We need a working baseline — an HTTP service, a database, and a one-command setup — so subsequent feature proposals (LLM providers, `/generate`, `/analyze`, editor) have something to build on.

This proposal establishes that baseline. It does not add user-facing features.

## What Changes

- Add `backend/` FastAPI service with project layout (`core`, `middlewares`, `routers`, `schemas`, `tables`, `services`).
- Add Pydantic schemas under `backend/app/schemas/diagram.py` mirroring `docs/schema/diagram-v0.md` (`Diagram`, `Node`, `Edge`, `Message` and supporting enums).
- Add `app/core/config.py` with `pydantic-settings` for environment-driven config (DB URL, LLM provider, guardrail caps).
- Add `GET /health` endpoint as a smoke test.
- Add root-level `docker-compose.yml` running Postgres 16 + `pgvector` extension and the backend service.
- Add `backend/Dockerfile` (Python 3.12 slim) and `backend/.env.example`.
- Add `backend/README.md` documenting the local dev loop (clone → `docker compose up` → `curl /health`).
- No public APIs beyond `/health` are added in this proposal. `/generate`, `/analyze`, and the editor live in future proposals.

## Capabilities

### New Capabilities

- `backend-runtime`: HTTP service shape — FastAPI app factory, configuration surface, health check, project structure conventions, and the contract that all future routers/services build on.
- `developer-environment`: One-command local development — `docker compose up` brings up Postgres (with pgvector) and the backend; `.env.example` documents the configuration surface; backend README documents the loop.

### Modified Capabilities

<!-- None. The diagram schema is already accepted (see docs/schema/diagram-v0.md) but
     is not yet represented as an OpenSpec capability. It will be moved into
     openspec/specs/diagram-schema/ in a separate, follow-up proposal so this
     change stays focused on runtime + environment. -->

## Impact

- **Code**: new top-level `backend/` and `docker-compose.yml`. No existing code is modified.
- **Dependencies**: Python 3.11+, FastAPI, Uvicorn, SQLModel, psycopg, Pydantic v2, pydantic-settings, ruff, pytest. LLM provider SDKs (anthropic, openai, ollama) are declared but unused until the provider-abstraction proposal lands.
- **Infrastructure**: requires Docker on the contributor's machine. We accept this constraint — it is standard for OSS dev tooling.
- **Documentation**: `backend/README.md` (new). Top-level `README.md` quick-start gains accuracy (`docker compose up` actually works after this lands).
- **Future proposals unblocked**: `add-llm-provider-abstraction`, `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint`, `add-diagram-persistence`, `establish-frontend-foundation`.
