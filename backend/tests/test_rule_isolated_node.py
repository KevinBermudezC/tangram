"""Rule: isolated-node."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.services.rules.rules.isolated_node import IsolatedNode
from tests._diagram_factories import make_diagram, make_edge, make_node

rule = IsolatedNode()


def test_isolated_node_fires() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("a", NodeType.FRONTEND),
            make_node("b", NodeType.BACKEND),
            make_node("c", NodeType.QUEUE),  # isolated
        ],
        edges=[make_edge("e1", "a", "b")],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1
    assert findings[0].node_ids == ["c"]


def test_connected_nodes_are_clean() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("a", NodeType.FRONTEND),
            make_node("b", NodeType.BACKEND),
        ],
        edges=[make_edge("e1", "a", "b")],
    )
    assert rule.check(diagram) == []


def test_single_node_diagram_fires() -> None:
    diagram = make_diagram(
        nodes=[make_node("only", NodeType.FRONTEND)],
        edges=[],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1
    assert findings[0].node_ids == ["only"]
