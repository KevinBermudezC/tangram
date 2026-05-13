## Why

Tangram's value proposition rests on the LLM giving *pedagogically useful*, *domain-specific* advice — not generic ChatGPT responses. Today the backend has the LLM provider abstraction in place but nothing tells the model what a `database` node *is*, what its typical implementations are, or what anti-patterns surround it. Without that knowledge, the model is forced to invent it on every call.

Three downstream proposals depend on having a structured component-metadata layer:

- `add-anti-pattern-rules` needs to know the canonical tradeoffs and pairings of each component type to encode rules that catch their violations.
- `add-patterns-library-and-rag` composes prompts that include relevant component metadata alongside retrieved patterns.
- `add-diagram-generation-endpoint` and `add-diagram-analysis-endpoint` pass component metadata to the LLM as part of the system context.

This proposal creates that layer.

## What Changes

- Add a top-level `components/` directory in the repo containing one YAML file per `NodeType` enum value (8 files: `frontend`, `backend`, `database`, `auth`, `storage`, `external_service`, `queue`, `cache`).
- Add `backend/app/schemas/component.py` defining the Pydantic schema each YAML must conform to.
- Add `backend/app/services/components/loader.py` exposing `load_components()` and `get_component(node_type)` — reads YAML files once, validates each against the schema, caches in memory.
- Add `pyyaml` to runtime dependencies in `backend/pyproject.toml`.
- Add tests under `backend/tests/`:
  - Every `NodeType` value has a corresponding YAML file (parity test, prevents silent omission when a new component is added to the enum).
  - Every YAML validates against the Pydantic schema.
  - Loader caches results (does not re-read disk on repeated calls).
- Document the format in `components/README.md` so contributors know how to add or edit components.

This proposal does **not** add any LLM call that consumes the metadata — that integration ships with `add-diagram-generation-endpoint`. We are establishing the asset; subsequent proposals consume it.

## Capabilities

### New Capabilities

- `component-metadata`: A curated, version-controlled library of architectural-component descriptions, one YAML file per node type. Defines the schema each file must satisfy (label, description, typical implementations, common pairings, tradeoffs, anti-patterns, learning resources). Exposes a Python loader that reads, validates, and caches them. Treated as a community asset — contributing a new field or refining existing entries is a first-class PR.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `components/` directory at repo root; new `app/schemas/component.py`, `app/services/components/`; new tests.
- **Dependencies**: adds `pyyaml>=6.0` to runtime deps.
- **Configuration**: no new env vars. The components directory location is hard-coded relative to the repo root (a path Settings does not need to know about, since the loader resolves it from `__file__`).
- **Documentation**: `components/README.md` explaining the YAML schema and contribution workflow. `backend/README.md` gains a short section pointing at the components folder.
- **Future proposals unblocked**: `add-anti-pattern-rules`, `add-patterns-library-and-rag`, `add-tutor-mode`, `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint`.
- **OSS contribution surface**: editing or adding a `components/*.yaml` is the lowest-friction way to contribute to Tangram — no code knowledge required. Good first issue material.
