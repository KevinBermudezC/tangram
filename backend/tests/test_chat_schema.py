"""Round-trip tests for chat schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatMessage, ChatRequest, ChatStreamPart
from app.schemas.diagram import NodeType
from tests._diagram_factories import make_diagram, make_node


def test_chat_message_round_trip() -> None:
    msg = ChatMessage(role="user", content="hello")
    dumped = msg.model_dump()
    reparsed = ChatMessage.model_validate(dumped)
    assert reparsed == msg


def test_chat_message_accepts_four_roles() -> None:
    for role in ("system", "user", "assistant", "tool"):
        ChatMessage(role=role, content="x")


def test_chat_message_rejects_unknown_role() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role="function", content="x")  # type: ignore[arg-type]


def test_chat_message_content_defaults_empty() -> None:
    msg = ChatMessage(role="assistant", tool_calls=[{"id": "call_1"}])
    assert msg.content == ""


def test_chat_request_requires_messages() -> None:
    with pytest.raises(ValidationError):
        ChatRequest.model_validate({"messages": []})


def test_chat_request_accepts_diagram_aliases() -> None:
    diagram = make_diagram(nodes=[make_node("n1", NodeType.BACKEND)], edges=[])
    req = ChatRequest.model_validate(
        {
            "messages": [{"role": "user", "content": "why?"}],
            "diagramId": "01HZZZZZZZZZZZZZZZZZZZZZZZ",
            "selectedNodeId": "n1",
            "diagram": diagram.model_dump(by_alias=True, mode="json"),
        }
    )
    assert req.diagram_id == "01HZZZZZZZZZZZZZZZZZZZZZZZ"
    assert req.selected_node_id == "n1"
    assert req.diagram is not None
    assert req.diagram.nodes[0].id == "n1"


def test_chat_request_ignores_client_tools() -> None:
    req = ChatRequest.model_validate(
        {
            "messages": [{"role": "user", "content": "why?"}],
            "tools": [{"type": "function", "function": {"name": "hack"}}],
        }
    )
    assert "tools" not in req.model_fields_set


def test_chat_stream_part_text_and_tool_call() -> None:
    text = ChatStreamPart(type="text", text="hi")
    tool = ChatStreamPart(
        type="tool-call",
        tool_call_id="call_1",
        tool_name="inspect_node",
        arguments='{"node_id":"n1"}',
    )
    assert ChatStreamPart.model_validate(text.model_dump()) == text
    assert ChatStreamPart.model_validate(tool.model_dump()) == tool
