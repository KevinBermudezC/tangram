## ADDED Requirements

### Requirement: PatternMatch shape

The backend SHALL expose a `PatternMatch` Pydantic model containing a `Pattern` instance and a `score: float` similarity score. Lower-is-closer or higher-is-closer is determined by the underlying distance metric; the public docstring states which one.

#### Scenario: PatternMatch round-trips through JSON

- **WHEN** a `PatternMatch` is serialized with `model_dump_json()` and re-parsed with `model_validate_json(...)`
- **THEN** the resulting model equals the original

### Requirement: Public retrieval API

The backend SHALL expose `retrieve_patterns(query: str, k: int = 3) -> list[PatternMatch]` and `force_rebuild() -> None` as the public surface of the retrieval layer. Callers SHALL NOT depend on any other internal symbol.

#### Scenario: Top-k retrieval

- **WHEN** `retrieve_patterns("I want to build a delivery app", k=3)` is called against a healthy index of five seed patterns
- **THEN** the return value is a list of at most three `PatternMatch` instances
- **AND** the list is ordered by relevance (most relevant first)

#### Scenario: k larger than the corpus

- **WHEN** `retrieve_patterns("...", k=100)` is called and the corpus has five patterns
- **THEN** the return value contains at most five `PatternMatch` instances

### Requirement: Lazy auto-build

The retrieval layer SHALL build the index on first use if the index is missing or stale. Subsequent calls SHALL hit the existing index without rebuilding, until the corpus or the embedder changes.

#### Scenario: First call builds the index

- **WHEN** `retrieve_patterns(...)` is called and no Chroma collection exists at `<CHROMA_PATH>`
- **THEN** the function builds the collection by embedding every pattern and inserting it
- **AND** the function returns valid matches

#### Scenario: Subsequent calls do not rebuild

- **WHEN** `retrieve_patterns(...)` is called twice in a row with no corpus change
- **THEN** the second call does not re-embed any pattern

### Requirement: Rebuild on corpus change

The retrieval layer SHALL detect content changes in `patterns/` and rebuild the index. Detection is by hashing the bytes of every pattern file plus the configured embedder identifier. The combined value is stored as collection metadata.

#### Scenario: Content change triggers rebuild

- **WHEN** a pattern file is edited and `retrieve_patterns(...)` is called afterwards
- **THEN** the layer detects the fingerprint mismatch and re-embeds every pattern before serving the query

#### Scenario: Embedder identifier change triggers rebuild

- **WHEN** `Settings.embedder` is changed (e.g. `ollama/...` → `openai/...`) and `retrieve_patterns(...)` is called
- **THEN** the layer detects the change and rebuilds the index with the new embedder

#### Scenario: Adding a new pattern triggers rebuild

- **WHEN** a new `patterns/<id>.md` file is added and `retrieve_patterns(...)` is called
- **THEN** the new pattern is included in the rebuilt index

### Requirement: Graceful degradation

The retrieval layer SHALL NOT propagate Chroma errors, embedder errors, or fingerprint errors to callers. Every such failure SHALL be logged at warning level and result in an empty return list.

#### Scenario: Chroma error returns empty

- **WHEN** Chroma raises during `retrieve_patterns(...)` (e.g. corrupted on-disk format)
- **THEN** the function returns an empty list
- **AND** a warning is logged with the underlying error

#### Scenario: Embedder error returns empty

- **WHEN** the embedder raises during the query (e.g. Ollama not running)
- **THEN** the function returns an empty list
- **AND** a warning is logged

### Requirement: Force-rebuild

The retrieval layer SHALL expose `force_rebuild()` that unconditionally deletes the existing collection and rebuilds it. Tests and future ops tooling will use this.

#### Scenario: Force rebuild from a healthy state

- **WHEN** the index is up to date and `force_rebuild()` is called
- **THEN** the existing collection is removed and a fresh one is built from the current patterns

### Requirement: No public dependency on Chroma types

Public callers SHALL receive `PatternMatch` instances; they SHALL NOT need to import any Chroma symbol to consume retrieval results.

#### Scenario: A router uses retrieval without importing chromadb

- **WHEN** a future router calls `retrieve_patterns(...)` and iterates the result
- **THEN** the router file does not need to import `chromadb` or any internal retrieval submodule

### Requirement: Documentation surface

The repository SHALL include `backend/app/services/retrieval/README.md` documenting the retrieval workflow, when the index rebuilds, and the failure modes.

#### Scenario: A contributor reads the README to understand the layer

- **WHEN** a contributor opens `backend/app/services/retrieval/README.md`
- **THEN** they learn how `retrieve_patterns` works, when the index auto-rebuilds, and what happens on failure
- **AND** they can use `force_rebuild()` for manual control without reading source files
