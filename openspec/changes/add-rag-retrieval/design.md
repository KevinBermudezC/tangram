## Context

The patterns corpus is bundled, the Chroma library is a declared dependency, and the embedder factory returns a configured `OllamaEmbedder` or `OpenAIEmbedder`. The pieces exist; this proposal connects them.

The trickier-than-it-sounds part is **freshness**. Chroma persists embeddings on disk under `<CHROMA_PATH>`. The user can:

- Edit a pattern file → embeddings on disk are stale.
- Add a new pattern → on-disk collection is incomplete.
- Switch from `ollama/nomic-embed-text-v2-moe` to `openai/text-embedding-3-small` → dimensions don't match; queries fail.

The retrieval layer must detect each of these and respond correctly, ideally with no manual step from the user.

## Goals / Non-Goals

**Goals:**

- `retrieve_patterns(query, k=3)` is the only function callers need. Async, returns `list[PatternMatch]` ordered by relevance.
- Index auto-builds on first call. Subsequent calls hit the existing Chroma collection.
- Rebuilds happen when: corpus content changes (fingerprint mismatch), embedder identifier changes, or the collection is missing.
- Failures degrade to empty results plus a logged warning. No crash propagates to the HTTP layer.
- Tests run without touching the network or a real Chroma directory on disk.

**Non-Goals:**

- Hybrid retrieval (combining vector similarity with keyword/tag filtering). Phase 2.
- Per-user retrieval caching. Out of scope; trivial to add later if needed.
- Streaming partial results. Retrieval is fast enough that buffering the full top-k is fine.
- A manual `tangram seed` CLI. The auto-build path covers MVP. A separate proposal can add the CLI.
- Replicating the index across machines. Self-hosted, single-user; the `<CHROMA_PATH>` folder is the source of truth.

## Decisions

### Fingerprint over file mtimes

We detect content changes by hashing the (sorted by filename) bytes of every `.md` under `patterns/`. The hash plus the configured embedder identifier form the index's "version key". The version key is stored as collection metadata; on every retrieval call we compute the current key and compare.

**Why not mtimes**: mtimes are unreliable. A `git checkout` of a stale branch can reset mtimes to clone time. Hashing is slower but trustworthy.

**Why combine with the embedder id**: switching embedders changes the vector dimension. Without this in the version key, the first query after the switch would crash on a dimension mismatch. With it, we detect and rebuild.

**Alternatives considered**: per-file etags stored individually (rejected — more bookkeeping for no benefit at our scale of 5–50 files), no fingerprinting (rejected — silent staleness is a worse failure mode than a one-time rebuild).

### Lazy build on first call

`retrieve_patterns()` calls `build_if_needed()` internally. That function checks the version key and rebuilds the collection if necessary. The first user-facing request after a change pays the cost; subsequent requests are fast.

**Why not eager on app boot**: keeps `/health` fast, keeps tests cheap, keeps the failure mode local (rebuild errors during boot are worse than rebuild errors on first /analyze call).

**Alternatives considered**: explicit `tangram seed` only (rejected — adds a manual step on every clone-and-run), eager + opt-in lazy (rejected — extra config surface for marginal value).

### Embed `title + body`, not metadata

We embed the concatenation of the pattern's title, a newline, and the body. Tags and component types are useful for filtering but not for semantic similarity in the way the user query is likely to be phrased.

**Why**: users phrase queries like "I want to build a chat app", not "tag:realtime complexity:intermediate". The title and prose body capture that intent. Tags can be added to the embed text if retrieval quality proves weak; easy follow-up.

**Alternatives considered**: embed each section separately and average (rejected — more code, marginal gain), embed metadata as a key-value preamble (rejected — risks polluting the semantic signal with structured noise).

### One embedding per pattern (no chunking)

Patterns are ~400–800 words. Modern embedders (nomic v2, OpenAI text-embedding-3) handle that comfortably in one call. We do not chunk.

**Alternatives considered**: chunk per section (rejected — adds aggregation complexity; the prose is already organized around themes the embedder can capture).

### Graceful degradation as a hard requirement

Every error path in retrieval logs and returns `[]`. The HTTP layer must work without retrieval succeeding (we don't want a Chroma bug to block `/generate`).

The errors we catch and turn into empty results:
- Chroma client construction fails.
- Collection query raises.
- Embedder query raises (network down, key invalid, model not pulled).
- Fingerprint check raises (`patterns/` directory missing — only happens in misconfigured deploys).

**Alternatives considered**: bubble errors and let callers handle (rejected — every caller would need the same boilerplate, and a missing pattern is not worth a 500 to the user).

### Public surface is two functions

`retrieve_patterns(query, k=3)` for the common case. `force_rebuild()` for tests and for future "I edited a pattern and want to retry" UX. Nothing else is exported.

**Alternatives considered**: expose the Chroma collection (rejected — leaks an implementation detail; future Chroma replacement would break callers).

### Chroma in tests: ephemeral client + fake embedder

Tests use `chromadb.EphemeralClient()` (in-memory, no disk) and a `FakeEmbedder` that returns deterministic vectors keyed by text content. This means tests:
- Run in tens of milliseconds.
- Never touch the network.
- Never leave files behind.
- Don't depend on Ollama or any cloud provider being available.

**Alternatives considered**: hit a real local Ollama in tests (rejected — couples CI to model availability; not viable on GitHub Actions runners).

## Risks / Trade-offs

- **Risk**: Chroma's persistent format changes between versions and the on-disk index becomes unreadable. → **Mitigation**: catch the load error, treat as "missing collection", rebuild. The corpus is the source of truth; the index is derived data.
- **Risk**: First call after a pattern edit pays a multi-second rebuild cost, surprising the user. → **Mitigation**: log a clear "Rebuilding pattern index..." line. A future `tangram seed` CLI lets power users pre-build.
- **Risk**: A failing embedder silently empties results, hiding real configuration problems. → **Mitigation**: warning-level log every time retrieval returns empty due to a caught error. Future eval suite would surface persistent empties.
- **Trade-off**: hash-based fingerprinting reads every pattern file from disk on every retrieval call. At 5 files this is negligible; at 5000 it would matter. We accept this for MVP.

## Migration Plan

No migration. New package, derived data folder. Rollback = delete `<CHROMA_PATH>` and revert the PR.

## Open Questions

- **Should we include a configurable similarity threshold?** ("Only return results with score > 0.6"). Tempting but Chroma's scores are not normalized across embedders; a threshold meaningful for one model is meaningless for another. Skip for MVP; rely on top-k.
- **Should `force_rebuild()` be exposed via an HTTP route?** Useful for debugging. Probably yes in `add-diagram-analysis-endpoint` or a future ops endpoint. Out of scope here.
- **What if a contributor adds a pattern whose body is huge (5000 words)?** Most embedders truncate silently. We accept that for MVP and document the recommendation "400–800 words" in `patterns/README.md` (already there).
