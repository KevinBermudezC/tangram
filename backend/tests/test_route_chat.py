"""POST /chat — UI Message Stream + inspect tools."""

from __future__ import annotations

import json

import chromadb
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.chat import ChatStreamPart
from app.schemas.diagram import NodeType
from app.services.chat import NO_DIAGRAM_REPLY
from app.services.llm import (
    LLMConfigError,
    LLMInputTooLarge,
    LLMRateLimited,
    LLMTimeoutError,
)
from app.services.modes import reset_for_tests as reset_modes
from app.services.patterns import reset_for_tests as reset_patterns
from app.services.retrieval import store
from app.services.storage import save_diagram
from tests._diagram_factories import make_diagram, make_edge, make_node
from tests._fake_embedder import FakeEmbedder
from tests._fake_llm import FakeLLMProvider


def _sse_events(body: str) -> list[dict]:
    events: list[dict] = []
    for line in body.splitlines():
        if not line.startswith("data: ") or line == "data: [DONE]":
            continue
        events.append(json.loads(line[len("data: ") :]))
    return events


def _sse_text(body: str) -> str:
    return "".join(e.get("delta") or "" for e in _sse_events(body) if e.get("type") == "text-delta")


def _tool_names(body: str) -> list[str]:
    return [e["toolName"] for e in _sse_events(body) if e.get("type") == "tool-input-available"]


def _queue_payload() -> dict:
    diagram = make_diagram(
        nodes=[
            make_node("api", NodeType.BACKEND, "API"),
            make_node("orders", NodeType.QUEUE, "Orders"),
            make_node("worker", NodeType.BACKEND, "Worker"),
        ],
        edges=[
            make_edge("e1", "api", "orders"),
            make_edge("e2", "orders", "worker"),
        ],
        name="Delivery",
    )
    return diagram.model_dump(by_alias=True, mode="json")


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    store.set_client_for_tests(chromadb.EphemeralClient())
    store.delete_collection()
    fake_emb = FakeEmbedder()
    monkeypatch.setattr("app.services.retrieval.builder.get_embedder", lambda: fake_emb)
    monkeypatch.setattr("app.services.retrieval.retriever.get_embedder", lambda: fake_emb)
    reset_patterns()
    reset_modes()
    yield TestClient(app)
    store.delete_collection()
    store.set_client_for_tests(None)
    reset_patterns()
    reset_modes()


def test_inspect_node_stream_names_the_selected_queue(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(
        stream_script=[
            [
                ChatStreamPart(
                    type="tool-call",
                    tool_call_id="call_1",
                    tool_name="inspect_node",
                    arguments='{"node_id":"orders"}',
                )
            ],
            [
                ChatStreamPart(
                    type="text",
                    text=(
                        "The **Orders** queue sits between API and Worker so "
                        "checkout spikes don't block the API."
                    ),
                )
            ],
        ]
    )
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)

    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "why is there a queue here?"}],
            "diagram": _queue_payload(),
            "selected_node_id": "orders",
        },
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert response.headers.get("x-vercel-ai-ui-message-stream") == "v1"
    assert _tool_names(response.text) == ["inspect_node"]
    text = _sse_text(response.text)
    assert "Orders" in text
    assert "API" in text
    assert "Worker" in text
    # First LLM call must not have been fed the diagram dump / label.
    first_blob = "\n".join(m.content for m in fake_llm.calls[0][0])
    assert "Current diagram (JSON)" not in first_blob
    assert "Orders" not in first_blob
    # Tool result on the second call carries the label.
    second_blob = "\n".join(m.content for m in fake_llm.calls[1][0])
    assert "Orders" in second_blob
    tool_names = {t["function"]["name"] for t in (fake_llm.stream_tools or [])}
    assert tool_names == {"inspect_diagram", "inspect_node"}


def test_no_diagram_refuses_without_llm(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(text_response="I invented a cache")
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)

    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": "why this cache?"}]},
    )
    assert response.status_code == 200
    assert _sse_text(response.text) == NO_DIAGRAM_REPLY
    assert fake_llm.calls == []
    assert "won't invent" in _sse_text(response.text).lower()


def test_empty_messages_returns_422(client: TestClient) -> None:
    response = client.post("/chat", json={"messages": []})
    assert response.status_code == 422


def test_unknown_diagram_id_returns_404(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    fake_llm = FakeLLMProvider(text_response="nope")
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)

    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "diagram_id": "01HZZZZZZZZZZZZZZZZZZZZZZZ",
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "diagram_not_found"
    assert fake_llm.calls == []


def test_oversized_payload_returns_413(client: TestClient) -> None:
    from app.core.config import get_settings

    settings = get_settings()
    oversize = "x" * (settings.max_input_chars + 1)
    response = client.post(
        "/chat",
        json={"messages": [{"role": "user", "content": oversize}]},
    )
    assert response.status_code == 413
    assert response.json()["code"] == "chat_input_too_large"


def test_llm_config_error_returns_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMConfigError("missing key"))
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "diagram": _queue_payload(),
        },
    )
    assert response.status_code == 503
    assert response.json()["code"] == "llm_config_error"


def test_llm_timeout_returns_504(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMTimeoutError("timed out"))
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "diagram": _queue_payload(),
        },
    )
    assert response.status_code == 504
    assert response.json()["code"] == "llm_timeout"


def test_llm_rate_limited_returns_429(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMRateLimited("slow down"))
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "diagram": _queue_payload(),
        },
    )
    assert response.status_code == 429
    assert response.json()["code"] == "llm_rate_limited"


def test_llm_input_too_large_returns_413(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(structured_error=LLMInputTooLarge("too big"))
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "hello"}],
            "diagram": _queue_payload(),
        },
    )
    assert response.status_code == 413
    assert response.json()["code"] == "llm_input_too_large"


def test_chat_does_not_write_storage(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_llm = FakeLLMProvider(text_response="ok")
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)

    def _boom(*args: object, **kwargs: object) -> None:
        raise AssertionError("chat must not write to storage")

    monkeypatch.setattr("app.services.storage.repository.save_diagram", _boom)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "explain"}],
            "diagram": _queue_payload(),
        },
    )
    assert response.status_code == 200


def test_unsaved_canvas_omits_diagram_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(text_response="The Orders queue absorbs spikes.")
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "why this queue?"}],
            "diagram": _queue_payload(),
            "selected_node_id": "orders",
        },
    )
    assert response.status_code == 200
    assert _sse_text(response.text)


def test_loads_diagram_id_from_storage(
    client: TestClient, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app.core.config import get_settings

    get_settings.cache_clear()
    fake_llm = FakeLLMProvider(
        stream_script=[
            [
                ChatStreamPart(
                    type="tool-call",
                    tool_call_id="call_d",
                    tool_name="inspect_diagram",
                    arguments="{}",
                )
            ],
            [ChatStreamPart(type="text", text="Postgres is the store.")],
        ]
    )
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    to_save = make_diagram(
        nodes=[make_node("db", NodeType.DATABASE, "Postgres")], edges=[], name="Disk"
    )
    to_save.id = ""
    saved = save_diagram(to_save)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "what is stored?"}],
            "diagram_id": saved.id,
        },
    )
    assert response.status_code == 200
    assert "inspect_diagram" in _tool_names(response.text)
    second = "\n".join(m.content for m in fake_llm.calls[1][0])
    assert "Postgres" in second


def test_unknown_node_is_a_structured_miss(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_llm = FakeLLMProvider(
        stream_script=[
            [
                ChatStreamPart(
                    type="tool-call",
                    tool_call_id="call_miss",
                    tool_name="inspect_node",
                    arguments='{"node_id":"ghost"}',
                )
            ],
            [
                ChatStreamPart(
                    type="text",
                    text="That id is not on the canvas. Click a node so I can inspect it.",
                )
            ],
        ]
    )
    monkeypatch.setattr("app.services.chat.service.get_llm", lambda: fake_llm)
    response = client.post(
        "/chat",
        json={
            "messages": [{"role": "user", "content": "why this ghost?"}],
            "diagram": _queue_payload(),
            "selected_node_id": "ghost",
        },
    )
    assert response.status_code == 200
    events = _sse_events(response.text)
    outputs = [e for e in events if e.get("type") == "tool-output-available"]
    assert outputs
    assert outputs[0]["output"] == {"error": "unknown_node", "node_id": "ghost"}
    assert "not on the canvas" in _sse_text(response.text)
    assert fake_llm.calls  # stream continued after the miss
