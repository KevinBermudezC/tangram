"""Rule: frontend-with-db-needs-auth."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.schemas.finding import Severity
from app.services.rules.rules.frontend_with_db_needs_auth import (
    FrontendWithDbNeedsAuth,
)
from tests._diagram_factories import make_diagram, make_node

rule = FrontendWithDbNeedsAuth()


def test_missing_auth_fires() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[],
    )
    findings = rule.check(diagram)
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARNING


def test_auth_present_silences_rule() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
            make_node("auth", NodeType.AUTH),
        ],
        edges=[],
    )
    assert rule.check(diagram) == []


def test_no_database_no_finding() -> None:
    diagram = make_diagram(
        nodes=[make_node("front", NodeType.FRONTEND)],
        edges=[],
    )
    assert rule.check(diagram) == []


def test_no_frontend_no_finding() -> None:
    diagram = make_diagram(
        nodes=[
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[],
    )
    assert rule.check(diagram) == []
