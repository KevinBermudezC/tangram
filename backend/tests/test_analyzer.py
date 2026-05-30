"""analyze_diagram orchestration with FakeLLMProvider."""

from __future__ import annotations

import chromadb
import pytest

from app.schemas.diagram import NodeType
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import store
from tests._diagram_factories import make_diagram, make_edge, make_node
from tests._fake_embedder import FakeEmbedder
from tests._fake_llm import FakeLLMProvider


def _violating_diagram():
    """Frontend wired straight to the database — trips one rule."""
    return make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )


def _clean_diagram():
    return make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
        ],
        edges=[make_edge("e1", "front", "api")],
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
async def test_returns_findings_and_feedback(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(text_response="Your frontend hits the DB directly.")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    from app.services.analysis import analyze_diagram

    result = await analyze_diagram(_violating_diagram())
    assert result.feedback == "Your frontend hits the DB directly."
    assert any(f.rule_id == "no-direct-frontend-to-database" for f in result.findings)


@pytest.mark.asyncio
async def test_findings_come_from_rules_not_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(text_response="anything at all")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    from app.services.analysis import analyze_diagram

    result = await analyze_diagram(_violating_diagram())
    offending = next(f for f in result.findings if f.rule_id == "no-direct-frontend-to-database")
    assert set(offending.node_ids) == {"front", "db"}


@pytest.mark.asyncio
async def test_clean_diagram_has_no_findings_but_has_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_llm = FakeLLMProvider(text_response="Solid little stack.")
    monkeypatch.setattr("app.services.analysis.analyzer.get_llm", lambda: fake_llm)

    from app.services.analysis import analyze_diagram

    result = await analyze_diagram(_clean_diagram())
    assert result.findings == []
    assert result.feedback == "Solid little stack."


@pytest.mark.asyncio
async def test_findings_independent_of_llm_response(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services.analysis import analyze_diagram

    diagram = _violating_diagram()

    monkeypatch.setattr(
        "app.services.analysis.analyzer.get_llm",
        lambda: FakeLLMProvider(text_response="response one"),
    )
    first = await analyze_diagram(diagram)

    monkeypatch.setattr(
        "app.services.analysis.analyzer.get_llm",
        lambda: FakeLLMProvider(text_response="totally different response two"),
    )
    second = await analyze_diagram(diagram)

    assert first.findings == second.findings
    assert first.feedback != second.feedback
