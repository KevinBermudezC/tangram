# Tangram backend

FastAPI service for the Tangram system-design copilot. Pre-alpha.

## Prerequisites

- Python 3.11 or newer
- (Optional) [Ollama](https://ollama.com) for local LLM and embedding inference

**Docker is not required for development.** A `Dockerfile` is provided for production deployments only.

## Local development

From the `backend/` directory:

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# 2. Install the project in editable mode with dev extras
pip install -e ".[dev]"

# 3. Copy the example env file and edit if needed
cp .env.example .env

# 4. Run the development server with auto-reload
uvicorn app.main:app --reload
```

Then in another terminal:

```bash
curl http://localhost:8000/health
# → {"status":"ok","name":"Tangram","version":"0.1.0","environment":"development"}
```

OpenAPI docs are at <http://localhost:8000/docs>.

## Project layout

```
app/
├── core/             # Pydantic Settings, dependencies, security utilities
├── middlewares/      # CORS, request logging, error handling (added per feature)
├── routers/          # FastAPI routers grouped by domain (health, diagrams, ai, ...)
├── schemas/          # Pure Pydantic data shapes (Diagram, Node, Edge, ...)
├── tables/           # Reserved for future ORM models (empty in MVP)
├── services/         # Business logic — LLM providers, retrieval, storage
└── main.py           # FastAPI app factory
tests/                # pytest suite
.env.example          # All configuration surfaces, with defaults
Dockerfile            # Opt-in production deployment
pyproject.toml        # Dependencies, ruff config, pytest config
```

## Storage layout

Tangram persists data on the local filesystem. Two roots, both under `<DATA_DIR>` (default `data/`, configurable via the `DATA_DIR` env var):

```
data/
├── diagrams/                # one JSON file per diagram (created on first save)
│   ├── 01HXYZ123ABCDEF.json
│   └── 01HXYZ234ABCDEF.json
└── patterns.chroma/         # Chroma vector store for the patterns library
```

- **Diagrams** are documents conforming to `app/schemas/diagram.py`. Backups: `cp -r data/`.
- **Patterns embeddings** live in a Chroma file-based collection. The repo will ship a pre-computed default; users on a different embedder can rebuild via `tangram seed` (Phase 2).

`data/` is git-ignored — your local diagrams are not committed by accident.

See [ADR-0004](../docs/architecture/0004-persistence.md) for the full reasoning.

## Running tests

```bash
pytest
```

## Linting and formatting

```bash
ruff format .
ruff check .
```

Both are part of `[dev]` extras; no extra install needed.

## Configuration reference

All configuration is loaded from environment variables (or a `.env` file) via Pydantic Settings. See `app/core/config.py` for the current `Settings` class. **Every field on `Settings` MUST be present in `.env.example`** — see [CONTRIBUTING.md](../CONTRIBUTING.md).

Key variables:

| Variable             | Default                            | Purpose                                      |
| -------------------- | ---------------------------------- | -------------------------------------------- |
| `ENVIRONMENT`        | `development`                      | One of `development`, `production`, `test`   |
| `DATA_DIR`           | `data`                             | Root for filesystem-backed storage           |
| `CHROMA_PATH`        | `data/patterns.chroma`             | Patterns vector store path                   |
| `CORS_ORIGINS`       | `["http://localhost:3000"]`        | Allowed frontend origins                     |
| `LLM_PROVIDER`       | `ollama`                           | One of `ollama`, `openai`, `anthropic`       |
| `OLLAMA_BASE_URL`    | `http://localhost:11434`           | Local Ollama runtime                         |
| `OPENAI_API_KEY`     | (empty)                            | BYOK if using OpenAI                         |
| `ANTHROPIC_API_KEY`  | (empty)                            | BYOK if using Anthropic                      |
| `EMBEDDER`           | `ollama/nomic-embed-text`          | Patterns embedder (`<provider>/<model>`)     |
| `MAX_INPUT_CHARS`    | `4000`                             | Hard cap on user input length                |
| `MAX_OUTPUT_TOKENS`  | `2048`                             | Hard cap on LLM output length                |

## Production deployment (optional)

If you want to deploy the backend with Docker:

```bash
docker build -t tangram-backend .
docker run -p 8000:8000 --env-file .env tangram-backend
```

The image is built on `python:3.12-slim` and runs Uvicorn on port 8000.

## Status

This README documents the runtime as defined in `openspec/changes/establish-mvp-foundations/`. Several items in that proposal's `tasks.md` are still open (the `data/` directory auto-creation, the schema parity test, etc.) — see the proposal for the up-to-date checklist.
