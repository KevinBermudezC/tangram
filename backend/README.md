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
text = await llm.generate(
    [
        ChatMessage(role="system", content="You are a system-design tutor."),
        ChatMessage(role="user", content="What is CQRS?"),
    ]
)

# Structured — physically cannot return a malformed Diagram
diagram = await llm.generate_structured(
    [
        ChatMessage(role="system", content="You produce Tangram diagrams."),
        ChatMessage(role="user", content="Design a delivery app."),
    ],
    schema=Diagram,
)

# Streaming
async for chunk in llm.stream(
    [
        ChatMessage(role="user", content="Explain microservices."),
    ]
):
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
catalog = load_components()  # dict[NodeType, ComponentMetadata]
print(catalog[NodeType.DATABASE].label)

# Or one at a time
db = get_component(NodeType.DATABASE)
print(db.tradeoffs)
```

Contributing to the metadata is one of the lowest-friction ways to help the project — see [`components/README.md`](../components/README.md).

## Patterns library

Longer-form architectural patterns live at the repo root in `patterns/<id>.md`. Each pattern describes when to use it, when to avoid it, the components involved, and the common pitfalls. The LLM consults them when explaining or generating diagrams.

```python
from app.services.patterns import get_pattern, load_patterns

# All patterns
catalog = load_patterns()  # dict[str, Pattern]
print(catalog["crud-application"].title)

# One at a time
p = get_pattern("realtime-chat")
print(p.body[:200])
```

Adding a new pattern is a markdown PR — no Python required. See [`patterns/README.md`](../patterns/README.md).

Retrieval (similarity search over this corpus) is available via `app.services.retrieval`; see the section below.

## Pattern retrieval

The retrieval layer ranks patterns by similarity to a user query using the configured embedder + Chroma.

```python
from app.services.retrieval import retrieve_patterns

matches = await retrieve_patterns("I want to build a chat app", k=3)
for m in matches:
    print(m.pattern.id, m.score)
```

The index auto-builds the first time you call `retrieve_patterns` and rebuilds whenever a pattern file changes or `EMBEDDER` is swapped. Failure modes (Chroma down, Ollama unavailable) return an empty list with a logged warning so the rest of the system keeps working.

See [`app/services/retrieval/README.md`](./app/services/retrieval/README.md) for details.

## Modes and prompt composition

A mode is the LLM's persona — how it talks and what it pays attention to. Modes live in markdown at the repo root in `modes/<id>.md`. MVP ships one: `tutor`.

The `compose_prompt` function is the single bridge between everything else and the LLM. It assembles the active mode's system prompt, a compact summary of every component type, the top-k patterns retrieved for the user's request, and the rule findings for a supplied diagram, then returns the `ChatMessage` list to send.

```python
from app.services.prompts import compose_prompt

# For a /generate call — no diagram yet
messages = await compose_prompt("I want to build a delivery app")

# For a /analyze call — diagram supplied
messages = await compose_prompt("what's wrong here?", diagram=my_diagram)

# Then send to the LLM
from app.services.llm import get_llm

result = await get_llm().generate(messages)
```

Sub-system failures (retrieval down, rules raising) degrade gracefully — the affected section is omitted with a warning, and composition continues. The only error `compose_prompt` propagates is `ModeNotFoundError` (bad `mode_id`).

Adding a new mode is a markdown PR. See [`modes/README.md`](../modes/README.md).

## Generation endpoint

`POST /generate` is Tangram's first end-to-end LLM endpoint. Send a text prompt, get back a fully validated `Diagram` with positions assigned.

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "I want to build a delivery app"}'
```

To actually run this against a real LLM, set up one of:

**Option A — Local Ollama (free, no key)**
```bash
ollama pull qwen3:4b-instruct
ollama serve   # often already running
# .env:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
```

**Option B — Ollama Cloud (managed, requires key)**
```bash
# .env:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=https://ollama.com
OLLAMA_API_KEY=<your-ollama-cloud-token>
```

**Option C — OpenAI (BYOK)**
```bash
# .env:
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

**Option D — Anthropic (BYOK)**
```bash
# .env:
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

If something is misconfigured, the endpoint returns a typed error (503 / 502 / 504 / 429 / 413) with a stable `code` field so the frontend can branch on it.

## Chat endpoint

`POST /chat` is the tutor talking about the open canvas. Send the conversation plus a live diagram snapshot (and the selected node). The handler streams the [UI Message Stream](https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol) the editor rail already consumes — including `inspect_diagram` / `inspect_node` tool parts. The diagram JSON is **not** stuffed into the prompt; the model has to inspect via those two tools. Chat does not persist the diagram or the thread.

```bash
curl -N -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "why is there a queue here?"}],
    "selected_node_id": "orders",
    "diagram": {
      "id": "demo",
      "metadata": {"name": "demo", "createdAt": "2026-01-01T00:00:00Z", "updatedAt": "2026-01-01T00:00:00Z"},
      "nodes": [
        {"id": "api", "type": "backend", "label": "API", "position": {"x": 0, "y": 0}},
        {"id": "orders", "type": "queue", "label": "Orders", "position": {"x": 200, "y": 0}},
        {"id": "worker", "type": "backend", "label": "Worker", "position": {"x": 400, "y": 0}}
      ],
      "edges": [
        {"id": "e1", "source": "api", "target": "orders"},
        {"id": "e2", "source": "orders", "target": "worker"}
      ]
    }
  }'
```

Unsaved canvases omit `diagram_id` and send `diagram` + `selected_node_id`. Saved ones may send `diagram_id` instead; a live `diagram` always wins.

If there is no snapshot and no loadable `diagram_id`, the stream is a short refusal (no LLM call) asking the user to generate or open a diagram. Analyze stays `POST /analyze` — it is not a chat tool.

The Next.js editor calls this through `/api/chat` (a passthrough). The same LLM setup (Options A–D above) applies, plus `413 chat_input_too_large` and `404 diagram_not_found`.

## Analysis endpoint

`POST /analyze` is the inverse of `/generate`: send an existing `Diagram`, get back the deterministic rule findings plus an LLM-generated prose critique. It is read-only — the diagram is never mutated or persisted.

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "diagram": {
      "id": "demo",
      "metadata": {"name": "demo", "createdAt": "2026-01-01T00:00:00Z", "updatedAt": "2026-01-01T00:00:00Z"},
      "nodes": [
        {"id": "front", "type": "frontend", "label": "Web", "position": {"x": 0, "y": 0}},
        {"id": "db", "type": "database", "label": "DB", "position": {"x": 200, "y": 0}}
      ],
      "edges": [{"id": "e1", "source": "front", "target": "db"}]
    }
  }'
```

The response shape is `{ "findings": Finding[], "feedback": str }`:

- `findings` comes straight from the rules engine — deterministic, independent of the LLM, returned even when empty.
- `feedback` is the tutor's narrative grounded in those findings.

Optionally pass `"modeId": "<mode>"` to pick the persona (defaults to `tutor`). The same LLM setup (Options A–D above) applies, and the same typed error contract — plus `413 diagram_too_large` for an oversized diagram and `422 unknown_mode` for an unknown mode.

## Anti-pattern rules

The rules engine inspects a `Diagram` and returns structured `Finding`s for known architectural mistakes. It runs in microseconds, never calls the LLM, and is deterministic.

```python
from app.services.rules import check_all

# diagram is an instance of app.schemas.diagram.Diagram
findings = check_all(diagram)
for f in findings:
    print(f.severity, f.message)
```

Five built-in rules ship today (direct frontend-to-DB, direct frontend-to-storage, missing auth, isolated nodes, cycles). Adding a rule is one file plus one registry entry — see [`app/services/rules/README.md`](./app/services/rules/README.md).

## Production deployment (optional)

If you want to deploy the backend with Docker:

```bash
docker build -t tangram-backend .
docker run -p 8000:8000 --env-file .env tangram-backend
```

The image is built on `python:3.12-slim` and runs Uvicorn on port 8000.

## Status

This README documents the runtime as defined in `openspec/changes/establish-mvp-foundations/`. Several items in that proposal's `tasks.md` are still open (the `data/` directory auto-creation, the schema parity test, etc.) — see the proposal for the up-to-date checklist.
