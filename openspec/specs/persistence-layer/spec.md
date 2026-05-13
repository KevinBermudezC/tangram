# persistence-layer Specification

## Purpose
TBD - created by archiving change establish-mvp-foundations. Update Purpose after archive.
## Requirements
### Requirement: Filesystem layout for diagrams

Diagrams SHALL be persisted as one JSON file per diagram, with content matching the canonical `Diagram` schema (`docs/schema/diagram-v0.md`), under `<DATA_DIR>/diagrams/<id>.json` where `<DATA_DIR>` is configurable via the `DATA_DIR` environment variable (default `data`).

#### Scenario: Diagram file naming

- **WHEN** the backend is asked to persist a diagram with id `01HXYZ123ABCDEF`
- **THEN** the file is written to `<DATA_DIR>/diagrams/01HXYZ123ABCDEF.json`
- **AND** the file content is the result of `Diagram.model_dump_json(by_alias=True, indent=2)`

#### Scenario: Missing data directory is created

- **WHEN** a write is attempted and `<DATA_DIR>/diagrams/` does not exist
- **THEN** the directory is created automatically with the missing parents
- **AND** the write succeeds

#### Scenario: No DB driver is required

- **WHEN** the backend is started for local development
- **THEN** no database server (Postgres, MySQL, etc.) needs to be running
- **AND** no database driver beyond what is needed for Chroma is installed

### Requirement: Filesystem layout for the patterns vector store

The patterns library embeddings SHALL be persisted in a Chroma file-based collection at `<CHROMA_PATH>` (default `data/patterns.chroma/`), configurable via the `CHROMA_PATH` environment variable.

#### Scenario: Default path resolution

- **WHEN** no `CHROMA_PATH` is set in the environment
- **THEN** the backend uses `data/patterns.chroma/` relative to the working directory

#### Scenario: Chroma store is portable

- **WHEN** the contents of `<CHROMA_PATH>` are copied to a new machine and the backend is started there with the same Chroma version
- **THEN** the store loads successfully and retrieval queries return the same results

### Requirement: Embeddings produced by a configurable embedder

The backend SHALL expose an `EMBEDDER` configuration value of the form `<provider>/<model>` (default `ollama/nomic-embed-text`) that determines which model embeds the patterns. The same embedder SHALL be used for any retrieval query.

#### Scenario: Embedder selection at boot

- **WHEN** `EMBEDDER=openai/text-embedding-3-small` is set
- **THEN** the patterns store is queried using that model
- **AND** if the existing Chroma store was embedded with a different model, the backend logs a warning suggesting `tangram seed` to re-embed

### Requirement: No relational database in MVP

The backend SHALL NOT require a relational database (Postgres, MySQL, SQLite, etc.) to function in MVP scope. Adding one SHALL be a deliberate, ADR-documented decision in a future proposal.

#### Scenario: Boot without any DB

- **WHEN** the backend is started in a clean environment with no DB running
- **THEN** the backend boots and serves `/health` successfully

