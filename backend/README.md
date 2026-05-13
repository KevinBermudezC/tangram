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

## Continuous integration

Every pull request and every push to `main` triggers `.github/workflows/ci.yml`, which runs three jobs in parallel:

| Job        | Command                                          | Fails when                                  |
| ---------- | ------------------------------------------------ | ------------------------------------------- |
| `lint`     | `ruff format --check . && ruff check .`          | Code is unformatted or violates a lint rule |
| `test`     | `pytest`                                         | Any test fails                              |
| `openspec` | `openspec validate <change> --strict` for each   | Any active proposal is malformed            |

To reproduce locally before pushing:

```bash
# from backend/
ruff format --check .
ruff check .
pytest

# from repo root
for d in openspec/changes/*/; do
  name=$(basename "$d")
  [ "$name" = "archive" ] && continue
  openspec validate "$name" --strict
done
```

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
| `OLLAMA_API_KEY`     | (empty)                            | Bearer token for Ollama Cloud; empty = local |
| `OPENAI_API_KEY`     | (empty)                            | BYOK if using OpenAI                         |
| `ANTHROPIC_API_KEY`  | (empty)                            | BYOK if using Anthropic                      |
| `OLLAMA_CHAT_MODEL`  | `qwen3:4b-instruct`                | Model used when `LLM_PROVIDER=ollama`        |
| `OPENAI_CHAT_MODEL`  | `gpt-4o-mini`                      | Model used when `LLM_PROVIDER=openai`        |
| `ANTHROPIC_CHAT_MODEL` | `claude-haiku-4-5`               | Model used when `LLM_PROVIDER=anthropic`     |
| `EMBEDDER`           | `ollama/nomic-embed-text-v2-moe`   | Patterns embedder (`<provider>/<model>`)     |
| `MAX_INPUT_CHARS`    | `4000`                             | Hard cap on user input length                |
| `MAX_OUTPUT_TOKENS`  | `2048`                             | Hard cap on LLM output length                |

## Talking to LLMs

Every backend caller goes through the same interface, regardless of which provider is configured:

```python
from app.schemas.chat import ChatMessage
from app.schemas.diagram import Diagram
from app.services.llm import get_llm

llm = get_llm()

# Plain prose
text = await llm.generate([
    ChatMessage(role="system", content="You are a system-design tutor."),
    ChatMessage(role="user", content="What is CQRS?"),
])

# Structured — physically cannot return a malformed Diagram
diagram = await llm.generate_structured(
    [
        ChatMessage(role="system", content="You produce Tangram diagrams."),
        ChatMessage(role="user", content="Design a delivery app."),
    ],
    schema=Diagram,
)

# Streaming
async for chunk in llm.stream([
    ChatMessage(role="user", content="Explain microservices."),
]):
    print(chunk, end="")
```

Switching provider is a single env-var change: `LLM_PROVIDER=anthropic`. No code changes.

Embeddings have their own factory and can be routed to a different provider via `EMBEDDER=<provider>/<model>`:

```python
from app.services.llm import get_embedder

embedder = get_embedder()
vectors = await embedder.embed(["some text", "more text"])
```

See [ADR-0005](../docs/architecture/0005-patterns-library-and-rag.md) for how this plugs into the patterns library + RAG.

## Component metadata

The curated knowledge layer for the 8 node types lives at the repo root in `components/<type>.yaml`. Each file describes what the component is, when to use it, common tradeoffs, and anti-patterns. The LLM consults this metadata when reasoning about a diagram.

```python
from app.schemas.diagram import NodeType
from app.services.components import get_component, load_components

# All components at once
catalog = load_components()             # dict[NodeType, ComponentMetadata]
print(catalog[NodeType.DATABASE].label)

# Or one at a time
db = get_component(NodeType.DATABASE)
print(db.tradeoffs)
```

Contributing to the metadata is one of the lowest-friction ways to help the project — see [`components/README.md`](../components/README.md).

## Production deployment (optional)

If you want to deploy the backend with Docker:

```bash
docker build -t tangram-backend .
docker run -p 8000:8000 --env-file .env tangram-backend
```

The image is built on `python:3.12-slim` and runs Uvicorn on port 8000.

## Status

This README documents the runtime as defined in `openspec/changes/establish-mvp-foundations/`. Several items in that proposal's `tasks.md` are still open (the `data/` directory auto-creation, the schema parity test, etc.) — see the proposal for the up-to-date checklist.
