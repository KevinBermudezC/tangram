"""generate_diagram orchestration with FakeLLMProvider."""

from __future__ import annotations

import chromadb
import pytest

from app.schemas.diagram import NodeType
from app.schemas.generate import (
    GeneratedDiagramContent,
    GeneratedEdge,
    GeneratedNode,
)
from app.services.llm import LLMInvalidResponse
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import store
from tests._fake_embedder import FakeEmbedder
from tests._fake_llm import FakeLLMProvider


def _content(
    name: str = "test", nodes: list | None = None, edges: list | None = None
) -> GeneratedDiagramContent:
    return GeneratedDiagramContent(
        name=name,
        description=None,
        nodes=nodes
        or [
            GeneratedNode(id="front", type=NodeType.FRONTEND, label="App"),
            GeneratedNode(id="api", type=NodeType.BACKEND, label="API"),
        ],
        edges=edges or [GeneratedEdge(id="e1", source="front", target="api")],
    )


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test gets in-memory Chroma + fake embedder + fresh caches."""
    store.set_client_for_tests(chromadb.EphemeralClient())
    store.delete_collection()
    fake_emb = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake_emb)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake_emb)
    reset_patterns()
    reset_modes()
    yield
    store.delete_collection()
    store.set_client_for_tests(None)
    reset_patterns()
    reset_modes()


@pytest.mark.asyncio
async def test_generate_returns_full_diagram(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_response=_content())
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    from app.services.generation import generate_diagram

    diagram = await generate_diagram("delivery app")
    assert diagram.metadata.name == "test"
    assert len(diagram.nodes) == 2
    assert len(diagram.edges) == 1
    # Positions assigned by auto_layout
    assert diagram.nodes[0].position.x is not None


@pytest.mark.asyncio
async def test_generate_assigns_unique_id_per_call(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_response=_content())
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    from app.services.generation import generate_diagram

    d1 = await generate_diagram("a")
    d2 = await generate_diagram("a")
    assert d1.id != d2.id


@pytest.mark.asyncio
async def test_generate_rejects_orphan_edge(monkeypatch: pytest.MonkeyPatch) -> None:
    bad_content = _content(
        nodes=[GeneratedNode(id="front", type=NodeType.FRONTEND, label="App")],
        edges=[GeneratedEdge(id="e1", source="front", target="ghost")],
    )
    fake_llm = FakeLLMProvider(structured_response=bad_content)
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    from app.services.generation import generate_diagram

    with pytest.raises(LLMInvalidResponse):
        await generate_diagram("a")


@pytest.mark.asyncio
async def test_generate_rejects_duplicate_node_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    bad_content = _content(
        nodes=[
            GeneratedNode(id="dupe", type=NodeType.FRONTEND, label="A"),
            GeneratedNode(id="dupe", type=NodeType.BACKEND, label="B"),
        ],
        edges=[],
    )
    fake_llm = FakeLLMProvider(structured_response=bad_content)
    monkeypatch.setattr("app.services.generation.generator.get_llm", lambda: fake_llm)

    from app.services.generation import generate_diagram

    with pytest.raises(LLMInvalidResponse):
        await generate_diagram("a")
