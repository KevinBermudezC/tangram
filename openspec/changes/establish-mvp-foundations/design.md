## Context

Tangram is pre-alpha. We have a JSON schema for diagrams (`docs/schema/diagram-v0.md`), an ADR for guardrails (`ADR-0001`), and an ADR for adopting OpenSpec (`ADR-0002`). What we lack is a runnable system: no backend, no database, no `docker compose up`. Without these, every subsequent proposal would have to re-establish them.

This change is the smallest set of artifacts that makes the project bootable end-to-end, without introducing user-facing behavior.

Constraints we honor:

- **Self-host first**: every contributor must be able to clone, run, and start contributing on their own machine.
- **One command**: `docker compose up` should be the entire setup. Anything more is friction we will pay for in lost contributors.
- **No premature features**: this proposal stops at `/health`. LLM endpoints, persistence of diagrams, and the editor are out of scope here.
- **SDD-aligned**: Pydantic schemas are the source of truth and are placed where future codegen can find them (`backend/app/schemas/`).

## Goals / Non-Goals

**Goals:**

- A FastAPI app that boots and responds on `GET /health`.
- A project layout that future contributors can extend without re-organizing (`core`, `middlewares`, `routers`, `schemas`, `tables`, `services`).
- Pydantic schemas matching `diagram-v0.md` available for import by future routers and services.
- Postgres 16 + `pgvector` running in Docker, ready for future RAG and diagram persistence work.
- A `.env.example` that documents every configurable surface.
- Contributors can run the backend with one command and verify it works.

**Non-Goals:**

- LLM providers, prompts, or anything that calls a model.
- The diagram-generation or analysis endpoints.
- Saving or loading diagrams to the database (no `tables/` content yet — only the package).
- Frontend, codegen pipeline, editor UI.
- Authentication or multi-user features.
- CI workflows (a follow-up housekeeping proposal handles that).

## Decisions

### Backend layout: feature-folder per concern

Use `app/{core,middlewares,routers,schemas,tables,services}` rather than a flat `app/` or a domain-driven layout (e.g. `app/diagrams/{router,schema,service}`).

- **Why**: this is the most common shape across mid-sized FastAPI projects; new contributors recognize it instantly. The domain-driven layout (`app/diagrams/...`) is cleaner once the project has 3+ domains, but Tangram has effectively one domain (diagrams) for the foreseeable future. Switching layouts later is mechanical.
- **Alternatives considered**: flat `app/` (rejected — gets unreadable past 5 files), domain-driven `app/diagrams/...` (rejected — premature for the size of the codebase).

### `pyproject.toml` only — no `requirements.txt`

The project is declared as an installable package via `pyproject.toml` (PEP 621). Production deps live under `[project.dependencies]`, dev deps under `[project.optional-dependencies.dev]`. Tool config (ruff, pytest) lives in the same file under `[tool.*]`.

- **Why**: PEP 621 is the modern standard. One file replaces `setup.py`, `setup.cfg`, `requirements.txt`, `requirements-dev.txt`, `.flake8`, `pytest.ini`, `mypy.ini`. Compatible with `uv`, `poetry`, `hatch`, and plain `pip`.
- **Alternatives considered**: `requirements.txt` only (rejected — no metadata, no dev/prod split, no tool config), Poetry-only `pyproject.toml` (rejected — Poetry-flavored TOML is a flavor lock-in). The lockfile question is deferred until CI exists.

### SQLModel for `tables/`, pure Pydantic for `schemas/`

Folder names are deliberate and follow the project's terminology: `schemas/` for Pydantic data shapes, `tables/` for SQLModel classes that map to DB rows. No file in `models/` ever exists.

- **Why**: "model" is overloaded in Python (ORM, ML, DTO). The split makes it impossible to confuse "this is the wire shape" from "this is a row in Postgres". `Table` suffix on SQLModel classes (`DiagramTable`) reinforces it.
- **Alternatives considered**: single `models/` folder mixing both (rejected — the very confusion this layout avoids).

### Postgres + pgvector via docker-compose

Run Postgres 16 with the `pgvector` extension as the database from day one, even though we do not query vectors yet.

- **Why**: when the RAG proposal lands in Phase 2, the database is already correct. Switching DB engines later is a migration; switching extensions on the same engine is one `CREATE EXTENSION` we can run now. pgvector also lets us avoid a separate vector store (Pinecone/Qdrant) for as long as scale permits.
- **Alternatives considered**: SQLite (rejected — no JSONB, no pgvector path), plain Postgres without pgvector (rejected — saves nothing, costs a future migration), separate vector DB later (rejected — extra service to operate, against self-host ethos).

### `psycopg[binary]>=3.2` over `psycopg2`

Use psycopg v3 with the binary wheel.

- **Why**: psycopg v3 is the actively maintained driver. It supports async natively (we will need this when streaming LLM responses interact with DB writes). The binary distribution avoids requiring a C compiler in the Docker build.
- **Alternatives considered**: `psycopg2-binary` (rejected — legacy), `asyncpg` (rejected — does not pair as cleanly with SQLModel).

### Pydantic camelCase aliases on the wire

Schemas use Python `snake_case` internally (`created_at`, `data_flow`) but expose `camelCase` on the JSON wire (`createdAt`, `dataFlow`) via `Field(alias=...)`. The schema doc (`docs/schema/diagram-v0.md`) is the source of truth — wire format must match it.

- **Why**: idiomatic Python on one side, idiomatic JSON/TS on the other, with no manual translation layer.
- **Alternatives considered**: snake_case on the wire (rejected — TypeScript codegen would feel non-native), camelCase in Python (rejected — fights every linter).

## Risks / Trade-offs

- **Risk**: Docker dependency for local dev → **Mitigation**: documented as a prerequisite in the README; the alternative (asking contributors to install Postgres locally) is worse. We accept that contributors without Docker cannot run Tangram.
- **Risk**: feature-folder layout will need refactor when we hit multiple domains → **Mitigation**: the codebase is small; we will refactor in a single PR when the second domain shows up. Not before.
- **Risk**: pgvector extension not available on every Postgres image → **Mitigation**: we pin the `pgvector/pgvector:pg16` image, which ships with the extension preinstalled. No risk if we use this image.
- **Risk**: `.env.example` drifts from real config requirements → **Mitigation**: lint rule (future) verifying every `Settings` field has a matching entry in `.env.example`. For now, manual review.
- **Trade-off**: the proposal includes work that has been partially scaffolded already on the current feature branch. We accept the slight retroactivity for the sake of getting OpenSpec into the workflow with a real, useful first proposal rather than a contrived one.

## Migration Plan

This is the project's first runtime. There is nothing to migrate from. Rollback = revert the PR.

## Open Questions

- Do we want a `Makefile` or `scripts/` entry points (e.g. `scripts/dev.sh`) to wrap common commands, or is `docker compose up` and a documented README sufficient? Leaning toward "README only" until we feel real pain.
- Should we lock dependency versions in a `requirements.lock.txt` for reproducibility? Defer until CI exists — at that point we will pick `uv pip compile` or `pip-tools`.
- Health check shape: `{ status, name, version, environment }` is the current default. If a future load-balancer or k8s probe expects a different shape, we extend it then.
