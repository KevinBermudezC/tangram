"""Rule: no-direct-frontend-to-storage."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.schemas.finding import Severity
from app.services.rules.rules.no_direct_frontend_to_storage import (
    NoDirectFrontendToStorage,
)
from tests._diagram_factories import make_diagram, make_edge, make_node

rule = NoDirectFrontendToStorage()


def test_direct_edge_fires() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("s3", NodeType.STORAGE),
        ],
        edges=[make_edge("e1", "front", "s3")],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1
    assert findings[0].severity == Severity.ERROR
    assert set(findings[0].node_ids) == {"front", "s3"}


def test_indirect_via_backend_does_not_fire() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("s3", NodeType.STORAGE),
        ],
        edges=[
            make_edge("e1", "front", "api"),
            make_edge("e2", "api", "s3"),
        ],
    )
    assert rule.check(diagram) == []


def test_no_storage_no_finding() -> None:
    diagram = make_diagram(
        nodes=[make_node("front", NodeType.FRONTEND)],
        edges=[],
    )
    assert rule.check(diagram) == []
