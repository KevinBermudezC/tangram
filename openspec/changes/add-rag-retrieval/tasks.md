## 1. Schema

- [x] 1.1 Add `app/schemas/retrieval.py` with `PatternMatch` (pattern: Pattern, score: float)
- [x] 1.2 Round-trip test in `tests/test_retrieval_schema.py`

## 2. Chroma store wrapper

- [x] 2.1 Add `app/services/retrieval/store.py` with `get_client()` (cached PersistentClient pointed at `<CHROMA_PATH>`) and `get_or_create_collection(version_key)` that creates / gets the `patterns` collection and stores the version_key in its metadata
- [x] 2.2 Add a small helper to delete the collection cleanly when rebuilding

## 3. Fingerprint + index builder

- [x] 3.1 Add `app/services/retrieval/builder.py` with `corpus_fingerprint()` (sha256 over sorted filename+bytes of every `patterns/*.md` excluding README)
- [x] 3.2 Implement `version_key()` combining the fingerprint with the configured embedder identifier
- [x] 3.3 Implement `build_if_needed()` (async) that checks the collection's stored version_key against the current one and rebuilds if needed
- [x] 3.4 Implement `_rebuild()` (async) that loads patterns, embeds each title+body, upserts into Chroma

## 4. Public retrieval API

- [x] 4.1 Add `app/services/retrieval/retriever.py` with `retrieve_patterns(query, k=3)` and `force_rebuild()`
- [x] 4.2 Wrap all Chroma / embedder operations in try/except; log warnings; return `[]` on failure
- [x] 4.3 Add `app/services/retrieval/__init__.py` re-exporting only `PatternMatch`, `retrieve_patterns`, `force_rebuild`

## 5. Tests

- [x] 5.1 `tests/test_retrieval_schema.py` — PatternMatch round-trip
- [x] 5.2 Add a `FakeEmbedder` test helper in `tests/_fake_embedder.py` returning deterministic vectors keyed by text content
- [x] 5.3 `tests/test_retrieval_builder.py` — fingerprint changes when files change; build_if_needed rebuilds on mismatch and skips on match; uses ephemeral Chroma client
- [x] 5.4 `tests/test_retrieval_retriever.py` — retrieve_patterns returns top-k in order; respects k > corpus size; force_rebuild works; Chroma error returns empty list with warning

## 6. Documentation

- [x] 6.1 Add `backend/app/services/retrieval/README.md` — how retrieval works, when rebuilds happen, failure modes, force_rebuild usage
- [x] 6.2 Add a "Pattern retrieval" section to `backend/README.md` with a usage snippet

## 7. Verification

- [x] 7.1 `ruff format --check` clean
- [x] 7.2 `ruff check` clean
- [x] 7.3 `pytest` clean (83 prior + 13 new = 96 total, all passing)
- [x] 7.4 `openspec validate add-rag-retrieval --strict`
