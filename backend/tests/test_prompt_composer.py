"""compose_prompt assembles the right messages for the LLM."""

from __future__ import annotations

import chromadb
import pytest

from app.schemas.diagram import NodeType
from app.services.modes import ModeNotFoundError
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.prompts import compose_prompt
from app.services.retrieval import store
from tests._diagram_factories import make_diagram, make_edge, make_node
from tests._fake_embedder import FakeEmbedder


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each test gets in-memory Chroma + fake embedder + fresh caches."""
    store.set_client_for_tests(chromadb.EphemeralClient())
    store.delete_collection()
    fake = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake)
    reset_patterns()
    reset_modes()
    yield
    store.delete_collection()
    store.set_client_for_tests(None)
    reset_patterns()
    reset_modes()


@pytest.mark.asyncio
async def test_without_diagram_returns_two_messages() -> None:
    messages = await compose_prompt("I want to build a delivery app")
    assert len(messages) == 2
    assert messages[0].role == "system"
    assert messages[1].role == "user"
    assert "delivery app" in messages[1].content


@pytest.mark.asyncio
async def test_system_message_starts_with_mode_prompt() -> None:
    messages = await compose_prompt("anything")
    # First non-empty stripped section should be the tutor system prompt content.
    system = messages[0].content
    # Tutor mode starts with "You are Tangram, a system-design tutor."
    assert system.lstrip().startswith("You are Tangram")


@pytest.mark.asyncio
async def test_system_message_includes_every_node_type() -> None:
    messages = await compose_prompt("anything")
    system = messages[0].content
    for nt in NodeType:
        assert nt.value in system, f"Node type {nt.value} missing from prompt"


@pytest.mark.asyncio
async def test_with_diagram_includes_diagram_in_user_message() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
        ],
        edges=[make_edge("e1", "front", "api")],
    )
    messages = await compose_prompt("review this", diagram=diagram)
    user_content = messages[1].content
    assert "review this" in user_content
    # The serialized diagram should be present (look for one of the node IDs).
    assert "front" in user_content


@pytest.mark.asyncio
async def test_with_diagram_includes_findings_section() -> None:
    # A diagram that triggers the no-direct-frontend-to-database rule.
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )
    messages = await compose_prompt("look at this", diagram=diagram)
    system = messages[0].content
    assert "Static analysis findings" in system
    assert "no-direct-frontend-to-database" in system


@pytest.mark.asyncio
async def test_clean_diagram_findings_section_says_no_issues() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
            make_node("auth", NodeType.AUTH),
        ],
        edges=[
            make_edge("e1", "front", "api"),
            make_edge("e2", "api", "db"),
            make_edge("e3", "front", "auth"),
            make_edge("e4", "api", "auth"),
        ],
    )
    messages = await compose_prompt("ok now what", diagram=diagram)
    system = messages[0].content
    assert "Static analysis findings" in system
    assert "No structural issues" in system


@pytest.mark.asyncio
async def test_unknown_mode_raises() -> None:
    with pytest.raises(ModeNotFoundError):
        await compose_prompt("hello", mode_id="not-a-real-mode")


@pytest.mark.asyncio
async def test_retrieval_failure_degrades_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    class ExplodingEmbedder:
        async def embed(self, texts: list[str]) -> list[list[float]]:
            raise RuntimeError("simulated retrieval failure")

    exploder = ExplodingEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: exploder)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: exploder)

    # Should not raise; should still produce the two messages.
    messages = await compose_prompt("anything")
    assert len(messages) == 2
    assert messages[0].role == "system"
    # The patterns section will be missing, but the mode + components are still there.
    assert "You are Tangram" in messages[0].content
