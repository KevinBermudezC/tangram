# ADR-0004 — Persistence: filesystem for diagrams, Chroma for embeddings

**Status:** Accepted

**Date:** 2026-05-09

**Decision-makers:** Tangram core team

**Related:** [ADR-0003 — Stack choice](./0003-stack-choice.md), [ADR-0005 — Patterns library architecture](./0005-patterns-library-and-rag.md)

---

## Context

Tangram needs to persist two distinct kinds of data:

1. **User-generated diagrams** — created and edited by the person running Tangram. These are document-shaped (a single JSON blob conforming to the `Diagram` schema). Reads/writes are infrequent (a few per minute at most), single-user, and always on the full document.
2. **Project-curated patterns library** — markdown files describing architectural patterns, with embeddings computed once per pattern. Read on every LLM call (top-k retrieval). Written rarely, only when maintainers update the corpus.

These two have different access patterns and lifecycles, and treating them as a single problem leads to the wrong tooling.

## Decision

We use **two separate, file-based stores**, both living under `<DATA_DIR>` (default `data/`) and both portable across machines:

### Diagrams

One JSON file per diagram, written under `<DATA_DIR>/diagrams/<id>.json` where `<id>` is a ULID generated at create time.

- File contents: `Diagram.model_dump_json(by_alias=True, indent=2)`.
- Reads: `Diagram.model_validate_json(path.read_text())`.
- Writes: atomic via temp file + rename.
- Listing: `os.listdir()` plus parsing the lightweight metadata (id, name, updated_at) — fine at our scale.
- Concurrency: not addressed; MVP is self-hosted single-user.

### Patterns embeddings

A single Chroma file-based collection at `<CHROMA_PATH>` (default `<DATA_DIR>/patterns.chroma/`).

- Source-of-truth corpus is `patterns/*.md` in the repo (curated, version-controlled, contribuible).
- Embeddings are produced by a configurable embedder (`EMBEDDER` env var, format `<provider>/<model>`).
- We pre-compute embeddings for the default embedder and ship the resulting Chroma directory inside the repo so first-run is instant.
- A `tangram seed` script (Phase 2) re-embeds when a contributor switches embedders.

## Consequences

### Positive

- **Zero infrastructure for local dev**: no DB server, no Docker, just files in `data/`.
- **User can inspect, backup, version their data with standard tools**: `cat data/diagrams/<id>.json`, `cp -r data/ backup/`, `git init` if they really want to.
- **Self-host ethos honored**: data lives where the user controls it, transparently.
- **Testing is trivial**: tests use `tmp_path` fixtures, no test DB to set up or tear down.
- **Diagrams as files maps cleanly to the schema's document-shape**: no impedance mismatch.

### Negative

- **No SQL queries across diagrams**: cross-document queries ("show me all diagrams that use the `auth` node type") require iterating files. At <1000 diagrams per user, fine. At larger scale, we'd index in memory or migrate.
- **Concurrent writers are not handled**: two processes writing the same diagram could lose data. Self-hosted single-user MVP makes this a non-issue today.
- **Chroma's on-disk format is internal**: if Chroma changes formats, users may need to rebuild. Pinning Chroma version mitigates.
- **Shipping pre-computed embeddings in the repo grows repo size**: with ~50 patterns and a small embedder, this is in the low-MB range. We accept it; Git LFS is not needed at this scale.

## Alternatives considered

### A. Postgres + JSONB for diagrams, pgvector for embeddings

**Rejected.** Adds Docker dependency (or local Postgres install). Buys nothing at our scale and breaks the no-Docker contract from ADR-0003. Reconsider when (a) we add multi-user collaboration, (b) the patterns corpus grows past Chroma's comfort zone, or (c) we want SQL queries across diagrams.

### B. SQLite + sqlite-vec for everything

**Rejected.** Cleaner one-file story than Chroma + filesystem, but sqlite-vec is too new (2024) for a project where contributors will need to troubleshoot edge cases via Google. Chroma + filesystem is the safer split today.

### C. Single Chroma collection holding both diagrams and patterns

**Rejected.** Chroma is a vector store. Storing diagrams there would require embedding them just to retrieve them by id — silly. Different access patterns deserve different tools.

### D. Diagrams in localStorage (browser only)

**Rejected.** Loses data when the browser cache clears or the user moves machines. Goes against the "your data is yours" positioning. Backend persistence on disk is the right answer.

## References

- ADR-0001 — Guardrails strategy
- ADR-0002 — OpenSpec for change proposals
- ADR-0003 — Stack choice
- ADR-0005 — Patterns library architecture
- `openspec/changes/establish-mvp-foundations/specs/persistence-layer/spec.md`
