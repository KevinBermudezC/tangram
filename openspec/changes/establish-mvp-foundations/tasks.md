## 1. Backend project skeleton

- [x] 1.1 Create `backend/` and the `app/{core,middlewares,routers,schemas,tables,services}` package layout with empty `__init__.py` files
- [x] 1.2 Add `backend/pyproject.toml` with runtime deps, optional `[dev]` group, and ruff + pytest config
- [x] 1.3 Add `backend/Dockerfile` (Python 3.12 slim) that installs the package and runs Uvicorn
- [x] 1.4 Add `backend/.env.example` mirroring every field on `Settings`

## 2. Core configuration

- [x] 2.1 Implement `app/core/config.py` with a `Settings` class loading from `.env`
- [x] 2.2 Provide a cached `get_settings()` accessor

## 3. Diagram schema

- [x] 3.1 Implement Pydantic schemas in `app/schemas/diagram.py` matching `docs/schema/diagram-v0.md` (`Diagram`, `Node`, `Edge`, `Message`, supporting enums and sub-models)
- [x] 3.2 Use `Field(alias=...)` to expose `camelCase` JSON while keeping `snake_case` Python
- [ ] 3.3 Add a parity test in `tests/test_schema_parity.py` that round-trips the example JSON from `docs/schema/diagram-v0.md`
- [ ] 3.4 Add a test that an unknown `type` value on a node raises a validation error

## 4. FastAPI runtime

- [x] 4.1 Implement `app/main.py` with a `create_app()` factory, lifespan hook, and CORS middleware reading from settings
- [x] 4.2 Add `app/routers/health.py` exposing `GET /health` returning `{ status, name, version, environment }`
- [x] 4.3 Wire the health router into the app

## 5. Local development environment

- [ ] 5.1 Add `docker-compose.yml` at repo root with two services: `db` (image `pgvector/pgvector:pg16`) and `backend`
- [ ] 5.2 Configure a named volume for Postgres data so it persists across restarts
- [ ] 5.3 Wire env vars from compose into the backend service (DATABASE_URL pointing at `db`)
- [ ] 5.4 Verify `docker compose up` brings up both services and `curl http://localhost:8000/health` returns 200
- [ ] 5.5 Verify `CREATE EXTENSION IF NOT EXISTS vector` succeeds in the running database

## 6. Documentation

- [ ] 6.1 Add `backend/README.md` documenting install, run, test, lint, and the docker-compose dev loop
- [ ] 6.2 Update top-level `README.md` quick-start so the documented commands actually work end-to-end
- [ ] 6.3 Add a note in `CONTRIBUTING.md` that every new field on `Settings` must also be added to `.env.example`

## 7. Verification before merge

- [ ] 7.1 Run `ruff format` and `ruff check` cleanly across `backend/`
- [ ] 7.2 Run `pytest` cleanly across `backend/tests/`
- [ ] 7.3 Validate the OpenSpec change: `openspec validate establish-mvp-foundations --strict`
- [ ] 7.4 Update PR description to link this change and check off the OpenSpec section in the PR template
