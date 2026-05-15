## Why

The patterns library landed as plain markdown plus a loader. Today any caller has to iterate `load_patterns()` and pick relevant ones by hand. That doesn't scale: with five patterns it's fine, with fifty it's nonsense to feed the LLM every one.

Retrieval-augmented generation (RAG) over the bundled corpus solves this: embed every pattern once, embed the user query, ask Chroma for the top-k most similar. The LLM sees a small, relevant slice on every call. Token cost stays bounded as the corpus grows; signal-to-noise improves; the user gets sharper answers.

This proposal lands that retrieval layer. The corpus already exists. The embedder factory already exists. What's missing is the Chroma collection, the index build/rebuild logic, and the `retrieve_patterns(query, k)` public function.

## What Changes

- Add `backend/app/schemas/retrieval.py` with `PatternMatch` (Pattern + similarity score).
- Add `backend/app/services/retrieval/` package:
  - `store.py` — Chroma client construction and collection management.
  - `builder.py` — corpus fingerprinting and `build_if_needed()`. Rebuilds the index when patterns change on disk or when the configured embedder changes (dimension mismatch).
  - `retriever.py` — `retrieve_patterns(query, k=3)` and `force_rebuild()`.
  - `__init__.py` — public re-exports.
  - `README.md` — how retrieval works, when the index rebuilds, what fails gracefully.
- Index location: `<CHROMA_PATH>/` (already configured via the `CHROMA_PATH` env var).
- Lazy build: on first `retrieve_patterns(...)` call, check fingerprint and embedder dimension; rebuild if needed. Boot stays fast.
- Graceful degradation: if Chroma or the embedder errors at retrieval time, return an empty list and log a warning. Calling code must tolerate empty results.
- Tests under `backend/tests/`:
  - Fake embedder + ephemeral Chroma client so tests run with no network and no on-disk state.
  - Schema round-trip for `PatternMatch`.
  - Builder rebuilds on fingerprint change.
  - Retriever returns top-k in score order.

This proposal does **not**:
- Wire retrieval into any LLM endpoint. `/generate`, `/analyze`, and tutor mode consume `retrieve_patterns()` in their own proposals.
- Ship a `tangram seed` CLI for explicit rebuilds. The auto-build covers the common case; the explicit script is a future proposal.
- Add UI for "explore the patterns library by similarity". Phase 2.

## Capabilities

### New Capabilities

- `pattern-retrieval`: A similarity-based retrieval layer over the `patterns/` corpus. Defines a `PatternMatch` wire shape (pattern + score), a Chroma-backed index that auto-builds and rebuilds based on a corpus fingerprint, and a single async function `retrieve_patterns(query, k)` returning the top-k matches. Embedder is whatever `EMBEDDER` selects in `Settings`. Failure modes (Chroma down, embedder unavailable, dimension mismatch) degrade gracefully to empty results.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `backend/app/services/retrieval/` package, new `backend/app/schemas/retrieval.py`, new tests.
- **Dependencies**: none new. Chroma was added in `establish-mvp-foundations`; the embedders ship with `add-llm-provider-abstraction`.
- **Configuration**: no new env vars. Uses the existing `EMBEDDER` and `CHROMA_PATH`.
- **Documentation**: `backend/app/services/retrieval/README.md` (new); short section in `backend/README.md` pointing at it.
- **Future proposals unblocked**: `add-tutor-mode`, `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint` — each composes a prompt that includes the top-k retrieved patterns plus the static metadata from `components/`.
- **Operational cost**: first call after a pattern edit pays the cost of embedding all patterns. With Ollama local + 5 patterns this is single-digit seconds. With cloud BYOK, the user pays a few cents per rebuild. Re-embedding only happens on content change.
