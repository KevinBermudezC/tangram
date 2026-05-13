"""Registry exposes built-in rules and runs them all."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.services.rules.registry import all_rules, check_all
from tests._diagram_factories import make_diagram, make_edge, make_node


def test_registry_returns_five_rules() -> None:
    rules = all_rules()
    assert len(rules) == 5
    ids = {r.id for r in rules}
    assert ids == {
        "no-direct-frontend-to-database",
        "no-direct-frontend-to-storage",
        "frontend-with-db-needs-auth",
        "isolated-node",
        "cycle-detected",
    }


def test_check_all_aggregates_findings() -> None:
    # Triggers two rules at once: no-direct-frontend-to-database AND missing-auth.
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )
    findings = check_all(diagram)
    rule_ids = {f.rule_id for f in findings}
    assert "no-direct-frontend-to-database" in rule_ids
    assert "frontend-with-db-needs-auth" in rule_ids


def test_check_all_clean_diagram() -> None:
    # Healthy: frontend -> backend -> database, with auth present, no cycles.
    diagram = make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("api", NodeType.BACKEND),
            make_node("db", NodeType.DATABASE),
            make_node("auth", NodeType.AUTH),
        ],
        edges=[
            make_edge("e1", "front", "api"),
            make_edge("e2", "api", "db"),
            make_edge("e3", "front", "auth"),
            make_edge("e4", "api", "auth"),
        ],
    )
    assert check_all(diagram) == []
