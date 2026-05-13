"""Rule: cycle-detected."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.services.rules.rules.cycle_detected import CycleDetected
from tests._diagram_factories import make_diagram, make_edge, make_node

rule = CycleDetected()


def test_acyclic_is_clean() -> None:
    # a -> b -> c
    diagram = make_diagram(
        nodes=[
            make_node("a", NodeType.FRONTEND),
            make_node("b", NodeType.BACKEND),
            make_node("c", NodeType.DATABASE),
        ],
        edges=[
            make_edge("e1", "a", "b"),
            make_edge("e2", "b", "c"),
        ],
    )
    assert rule.check(diagram) == []


def test_two_node_cycle_fires() -> None:
    # a <-> b
    diagram = make_diagram(
        nodes=[
            make_node("a", NodeType.BACKEND),
            make_node("b", NodeType.BACKEND),
        ],
        edges=[
            make_edge("e1", "a", "b"),
            make_edge("e2", "b", "a"),
        ],
    )
    findings = rule.check(diagram)
    assert len(findings) >= 1
    cycle_nodes = set()
    for f in findings:
        cycle_nodes.update(f.node_ids)
    assert {"a", "b"}.issubset(cycle_nodes)


def test_self_loop_fires() -> None:
    diagram = make_diagram(
        nodes=[make_node("a", NodeType.BACKEND)],
        edges=[make_edge("e1", "a", "a")],
    )
    findings = rule.check(diagram)
    assert len(findings) >= 1
    assert "a" in findings[0].node_ids


def test_three_node_cycle_fires() -> None:
    # a -> b -> c -> a
    diagram = make_diagram(
        nodes=[
            make_node("a", NodeType.BACKEND),
            make_node("b", NodeType.BACKEND),
            make_node("c", NodeType.BACKEND),
        ],
        edges=[
            make_edge("e1", "a", "b"),
            make_edge("e2", "b", "c"),
            make_edge("e3", "c", "a"),
        ],
    )
    findings = rule.check(diagram)
    assert len(findings) >= 1
    cycle_nodes = set()
    for f in findings:
        cycle_nodes.update(f.node_ids)
    assert {"a", "b", "c"}.issubset(cycle_nodes)
