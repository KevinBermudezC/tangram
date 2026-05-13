"""Rule: no-direct-frontend-to-database."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.schemas.finding import Severity
from app.services.rules.rules.no_direct_frontend_to_database import (
    NoDirectFrontendToDatabase,
)
from tests._diagram_factories import make_diagram, make_edge, make_node

rule = NoDirectFrontendToDatabase()


def test_direct_edge_fires() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1
    assert findings[0].severity == Severity.ERROR
    assert set(findings[0].node_ids) == {"front", "db"}
    assert findings[0].edge_ids == ["e1"]


def test_reverse_direction_also_fires() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "db", "front")],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1


def test_indirect_via_backend_does_not_fire() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[
            make_edge("e1", "front", "api"),
            make_edge("e2", "api", "db"),
        ],
    )
    assert rule.check(diagram) == []


def test_no_database_no_finding() -> None:
    diagram = make_diagram(
        nodes=[make_node("front", NodeType.FRONTEND)],
        edges=[],
    )
    assert rule.check(diagram) == []
