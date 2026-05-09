## 1. Backend project skeleton

- [x] 1.1 Create `backend/` and the `app/{core,middlewares,routers,schemas,tables,services}` package layout with empty `__init__.py` files
- [x] 1.2 Add `backend/pyproject.toml` with runtime deps (FastAPI, Pydantic, Chroma, LLM SDKs), `[dev]` group, and ruff + pytest config — no Postgres/SQLModel deps
- [x] 1.3 Add `backend/Dockerfile` (Python 3.12 slim) for opt-in production deployments
- [x] 1.4 Add `backend/.env.example` mirroring every field on `Settings`

## 2. Core configuration

- [x] 2.1 Implement `app/core/config.py` with a `Settings` class loading from `.env` (DATA_DIR, CHROMA_PATH, EMBEDDER, LLM provider, guardrail caps)
- [x] 2.2 Provide a cached `get_settings()` accessor

## 3. Diagram schema

- [x] 3.1 Implement Pydantic schemas in `app/schemas/diagram.py` matching `docs/schema/diagram-v0.md` (`Diagram`, `Node`, `Edge`, `Message`, supporting enums and sub-models)
- [x] 3.2 Use `Field(alias=...)` plus `ConfigDict(populate_by_name=True)` to expose `camelCase` JSON while keeping `snake_case` Python
- [ ] 3.3 Add a parity test in `tests/test_schema_parity.py` that round-trips the example JSON from `docs/schema/diagram-v0.md`
- [ ] 3.4 Add a test that an unknown `type` value on a node raises a validation error

## 4. FastAPI runtime

- [x] 4.1 Implement `app/main.py` with a `create_app()` factory, lifespan hook, and CORS middleware reading from settings
- [x] 4.2 Add `app/routers/health.py` exposing `GET /health` returning `{ status, name, version, environment }`
- [x] 4.3 Wire the health router into the app

## 5. Storage layout

- [ ] 5.1 Document the filesystem layout in `backend/README.md` (`<DATA_DIR>/diagrams/<id>.json`, `<CHROMA_PATH>/`)
- [ ] 5.2 Ensure `<DATA_DIR>` and `<CHROMA_PATH>` are created on first use (auto-mkdir) — the routers/services that actually write are out of scope for this proposal
- [ ] 5.3 Add `data/` to `.gitignore` so contributors do not commit their local diagrams

## 6. Documentation

- [ ] 6.1 Add `backend/README.md` documenting install, run, test, lint, the dev loop, and the storage layout — explicitly without Docker
- [ ] 6.2 Update top-level `README.md` quick-start so the documented commands actually work end-to-end (no Docker required)
- [ ] 6.3 Add a note in `CONTRIBUTING.md` that every new field on `Settings` must also be added to `.env.example`

## 7. Architecture decision records

- [ ] 7.1 Update ADR-0001 to remove the assumption of Postgres + pgvector
- [ ] 7.2 Add ADR-0003 — Stack choice (Next.js + FastAPI + filesystem + Chroma + Ollama/BYOK)
- [ ] 7.3 Add ADR-0004 — Persistence: filesystem for diagrams, Chroma for patterns embeddings
- [ ] 7.4 Add ADR-0005 — Patterns library architecture (RAG composition, retrieval k=3, bundleable)
- [ ] 7.5 Update `docs/architecture/README.md` ADR index

## 8. Verification before merge

- [ ] 8.1 Run `ruff format` and `ruff check` cleanly across `backend/`
- [ ] 8.2 Run `pytest` cleanly across `backend/tests/`
- [ ] 8.3 Validate the OpenSpec change: `openspec validate establish-mvp-foundations --strict`
- [ ] 8.4 Update PR description to link this change and check off the OpenSpec section in the PR template
