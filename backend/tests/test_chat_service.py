"""compose_chat_messages: tutor + tools, no secret diagram dump."""

from __future__ import annotations

import chromadb
import pytest

from app.schemas.chat import ChatRequest
from app.schemas.diagram import NodeType
from app.services.chat import DiagramNotFoundError, compose_chat_messages, resolve_diagram
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import store
from app.services.storage import save_diagram
from tests._diagram_factories import make_diagram, make_edge, make_node
from tests._fake_embedder import FakeEmbedder


@pytest.fixture
def retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
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


def _req(**kwargs: object) -> ChatRequest:
    base: dict = {"messages": [{"role": "user", "content": "why is there a queue here?"}]}
    base.update(kwargs)
    return ChatRequest.model_validate(base)


def _queue_diagram():
    return make_diagram(
        nodes=[
            make_node("api", NodeType.BACKEND, "API"),
            make_node("orders", NodeType.QUEUE, "Orders"),
            make_node("worker", NodeType.BACKEND, "Worker"),
        ],
        edges=[
            make_edge("e1", "api", "orders"),
            make_edge("e2", "orders", "worker"),
        ],
        name="Canvas",
    )


@pytest.mark.usefixtures("retrieval")
async def test_compose_uses_tutor_and_does_not_dump_diagram() -> None:
    diagram = _queue_diagram()
    messages = await compose_chat_messages(_req(diagram=diagram, selected_node_id="orders"))
    system = messages[0].content
    assert system.lstrip().startswith("You are Tangram")
    assert "inspect_node" in system
    assert "inspect_diagram" in system
    assert "selected_node_id=`orders`" in system
    assert "Current diagram (JSON)" not in system
    assert '"type": "queue"' not in system
    # Label must not leak before a tool call.
    assert "Orders" not in system
    blob = "\n".join(m.content for m in messages)
    assert "Current diagram (JSON)" not in blob


@pytest.mark.usefixtures("retrieval")
def test_live_diagram_wins_over_diagram_id(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    stored = make_diagram(nodes=[make_node("db", NodeType.DATABASE, "DB")], edges=[], name="Stored")
    stored.id = ""
    stored = save_diagram(stored)
    live = make_diagram(
        nodes=[make_node("front", NodeType.FRONTEND, "Web")], edges=[], name="Canvas"
    )
    resolved = resolve_diagram(_req(diagram=live, diagram_id=stored.id))
    assert resolved is not None
    assert resolved.metadata.name == "Canvas"


@pytest.mark.usefixtures("retrieval")
def test_unknown_diagram_id_raises(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    with pytest.raises(DiagramNotFoundError):
        resolve_diagram(_req(diagram_id="01HZZZZZZZZZZZZZZZZZZZZZZZ"))
