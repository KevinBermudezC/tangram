"""End-to-end retrieval behavior with fake embedder + in-memory Chroma."""

from __future__ import annotations

import chromadb
import pytest

from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import retrieve_patterns, store
from tests._fake_embedder import FakeEmbedder


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    store.set_client_for_tests(chromadb.EphemeralClient())
    fake = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake)
    reset_patterns()
    yield
    store.set_client_for_tests(None)
    reset_patterns()


@pytest.mark.asyncio
async def test_returns_at_most_k_results() -> None:
    matches = await retrieve_patterns("anything", k=3)
    assert 0 <= len(matches) <= 3


@pytest.mark.asyncio
async def test_k_larger_than_corpus_returns_all() -> None:
    matches = await retrieve_patterns("anything", k=100)
    # 5 seed patterns, can't return more.
    assert len(matches) == 5


@pytest.mark.asyncio
async def test_zero_or_negative_k_returns_empty() -> None:
    assert await retrieve_patterns("q", k=0) == []
    assert await retrieve_patterns("q", k=-1) == []


@pytest.mark.asyncio
async def test_each_match_has_a_pattern_and_score() -> None:
    matches = await retrieve_patterns("delivery app", k=3)
    for m in matches:
        assert m.pattern is not None
        assert m.pattern.id
        assert isinstance(m.score, float)


@pytest.mark.asyncio
async def test_results_are_ordered_by_score_ascending() -> None:
    """Cosine distance: lower is more similar, so results should be ascending."""
    matches = await retrieve_patterns("anything", k=5)
    if len(matches) < 2:
        pytest.skip("need at least 2 matches to test ordering")
    scores = [m.score for m in matches]
    assert scores == sorted(scores)


@pytest.mark.asyncio
async def test_embedder_failure_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    class ExplodingEmbedder:
        async def embed(self, texts: list[str]) -> list[list[float]]:
            raise RuntimeError("simulated embedder failure")

    exploder = ExplodingEmbedder()
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: exploder)
    result = await retrieve_patterns("anything", k=3)
    assert result == []
