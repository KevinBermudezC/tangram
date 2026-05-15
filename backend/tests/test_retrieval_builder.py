"""Fingerprint logic + build_if_needed semantics."""

from __future__ import annotations

import chromadb
import pytest

from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import builder, store
from tests._fake_embedder import FakeEmbedder


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test gets a fresh in-memory Chroma client and a fake embedder.

    Note: we patch `get_embedder` at the call sites (builder + retriever),
    not at the factory module. `from x import y` creates a local binding
    that a patch on `x.y` does not reach.
    """
    store.set_client_for_tests(chromadb.EphemeralClient())
    fake = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake)
    reset_patterns()
    yield
    store.set_client_for_tests(None)
    reset_patterns()


def test_corpus_fingerprint_is_stable() -> None:
    a = builder.corpus_fingerprint()
    b = builder.corpus_fingerprint()
    assert a == b


def test_version_key_includes_embedder() -> None:
    key = builder.version_key()
    assert "::" in key
    # Left side is the embedder identifier from Settings; right is the fp.
    left, _, right = key.partition("::")
    assert left  # non-empty
    assert right  # non-empty


@pytest.mark.asyncio
async def test_build_if_needed_creates_collection_on_first_call() -> None:
    assert store.get_collection_if_exists() is None
    await builder.build_if_needed()
    collection = store.get_collection_if_exists()
    assert collection is not None
    # Five seed patterns expected.
    assert collection.count() == 5


@pytest.mark.asyncio
async def test_build_if_needed_skips_when_version_matches() -> None:
    await builder.build_if_needed()
    collection_before = store.get_collection_if_exists()
    assert collection_before is not None
    count_before = collection_before.count()

    # Second call: same version key, should not rebuild. We verify by checking
    # that the collection id is stable (rebuild creates a new internal id).
    collection_id_before = collection_before.id

    await builder.build_if_needed()
    collection_after = store.get_collection_if_exists()
    assert collection_after is not None
    assert collection_after.count() == count_before
    assert collection_after.id == collection_id_before


@pytest.mark.asyncio
async def test_force_rebuild_replaces_collection() -> None:
    await builder.build_if_needed()
    before = store.get_collection_if_exists()
    assert before is not None
    before_id = before.id

    await builder.force_rebuild()

    after = store.get_collection_if_exists()
    assert after is not None
    assert after.id != before_id
