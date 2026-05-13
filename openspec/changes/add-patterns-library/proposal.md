## Why

The `components/` library covers what each individual component type is. That's necessary but not sufficient. Real architectural insight lives at the level of *combinations*: CQRS, event-driven, JAMstack, "background worker behind a web app". A junior dev who knows what a database and a queue are still has to learn how they fit together to make a delivery app or a chat service.

A patterns library is where that combinatorial knowledge lives. Each pattern is a longer-form markdown document with a clear shape: when to use it, when to avoid it, which components it involves, common pitfalls. The LLM consults relevant patterns at generation and analysis time, and contributors can grow the library without writing any Python.

This proposal lands the **library and its loader**, not retrieval. Retrieval (Chroma + embeddings + top-k search) ships in the follow-up proposal `add-rag-retrieval`. Keeping them separate lets us ship the corpus content sooner, exercise the format with real patterns, and isolate the retrieval design decisions in their own PR.

## What Changes

- Add a top-level `patterns/` directory with five seed patterns as markdown files:
  - `crud-application.md` — the baseline web app pattern (frontend + backend + database, possibly auth).
  - `jamstack.md` — static frontend + serverless backend / external services.
  - `background-worker.md` — backend + queue + worker for slow side effects.
  - `realtime-chat.md` — frontend + backend + queue + (often) external push service.
  - `event-driven.md` — services communicating via events rather than direct calls.
- Each `.md` file uses YAML frontmatter for structured metadata (id, title, complexity, tags, component_types) and a markdown body with required sections (`## What it is`, `## When to use`, `## When to avoid`, `## Components involved`, `## Common pitfalls`).
- Add `backend/app/schemas/pattern.py` defining `PatternComplexity` (StrEnum) and `Pattern` (Pydantic model: metadata fields + parsed body + raw markdown).
- Add `backend/app/services/patterns/loader.py` exposing `load_patterns()` (returns `dict[str, Pattern]` keyed by id), `get_pattern(pattern_id)`, and `reset_for_tests()`. Decorated with `lru_cache`.
- Add `python-frontmatter>=1.0` to runtime dependencies.
- Add `patterns/README.md` describing the format, the required body sections, the tone guidance, and the contribution workflow.
- Add tests under `backend/tests/`:
  - Every `.md` under `patterns/` validates against the schema.
  - Every `.md` has the required body sections.
  - Loader caches and `get_pattern` works.

This proposal does **not**:
- Compute embeddings.
- Add Chroma or any vector store.
- Implement any kind of search / retrieval. Callers will iterate `load_patterns()` and filter by hand until `add-rag-retrieval` lands.
- Wire patterns into the LLM prompt path. That happens with the endpoints (`/generate`, `/analyze`) in their own proposals.

## Capabilities

### New Capabilities

- `patterns-library`: A curated, version-controlled library of architectural patterns as markdown documents with structured frontmatter. Defines the on-disk format every pattern file must satisfy (frontmatter fields, required body sections), the Python schema (`Pattern`), and the loader API (`load_patterns`, `get_pattern`). Treated as a community asset — adding a new pattern is a markdown PR, no Python knowledge required.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `patterns/` directory at repo root; new `app/schemas/pattern.py`; new `app/services/patterns/` package; new tests.
- **Dependencies**: adds `python-frontmatter>=1.0` (lightweight, pure Python, well-maintained).
- **Configuration**: no new env vars. The patterns directory location is resolved relative to the repo root.
- **Documentation**: `patterns/README.md` (new); short "Patterns library" section in `backend/README.md`.
- **Future proposals unblocked**: `add-rag-retrieval` (the retrieval layer over this corpus), `add-tutor-mode` (composes patterns into prompts), `add-diagram-generation-endpoint` and `add-diagram-analysis-endpoint` (consume retrieved patterns as LLM context).
- **OSS contribution surface**: writing a new pattern markdown is one of the highest-leverage zero-Python contributions to the project, alongside `components/`.
