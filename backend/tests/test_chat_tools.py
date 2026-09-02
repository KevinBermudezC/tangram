"""inspect_diagram / inspect_node execute against a snapshot."""

from __future__ import annotations

import json

from app.schemas.diagram import NodeType
from app.services.chat.tools import (
    CHAT_TOOLS,
    INSPECT_DIAGRAM,
    INSPECT_NODE,
    execute_chat_tool,
    inspect_diagram,
    inspect_node,
)
from tests._diagram_factories import make_diagram, make_edge, make_node


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
        name="Delivery",
    )


def test_only_two_chat_tools_registered() -> None:
    names = {t["function"]["name"] for t in CHAT_TOOLS}
    assert names == {INSPECT_DIAGRAM, INSPECT_NODE}


def test_inspect_diagram_lists_nodes_and_edges() -> None:
    result = inspect_diagram(_queue_diagram())
    assert {n["id"] for n in result["nodes"]} == {"api", "orders", "worker"}
    assert {e["id"] for e in result["edges"]} == {"e1", "e2"}


def test_inspect_diagram_no_snapshot() -> None:
    assert inspect_diagram(None) == {"error": "no_diagram"}


def test_inspect_node_returns_incident_edges() -> None:
    result = inspect_node(_queue_diagram(), "orders")
    assert result["id"] == "orders"
    assert result["type"] == "queue"
    assert result["label"] == "Orders"
    assert {e["id"] for e in result["edges"]} == {"e1", "e2"}


def test_inspect_node_unknown() -> None:
    result = inspect_node(_queue_diagram(), "missing")
    assert result == {"error": "unknown_node", "node_id": "missing"}


def test_execute_inspect_node_parses_arguments() -> None:
    result = execute_chat_tool(INSPECT_NODE, '{"node_id": "orders"}', _queue_diagram())
    assert result["label"] == "Orders"


def test_chat_tools_do_not_call_analyze_or_generate() -> None:
    blob = json.dumps(CHAT_TOOLS)
    assert "/analyze" not in blob
    assert "/generate" not in blob
    assert "analyzeDiagram" not in blob
    assert "analyze_diagram" not in blob
