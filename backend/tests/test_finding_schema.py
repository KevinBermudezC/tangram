"""Finding shape round-trips."""

from __future__ import annotations

from app.schemas.finding import Finding, Severity


def test_finding_round_trip() -> None:
    f = Finding(
        rule_id="some-rule",
        severity=Severity.ERROR,
        message="bad",
        rationale="because",
        node_ids=["n1", "n2"],
        edge_ids=["e1"],
    )
    reparsed = Finding.model_validate_json(f.model_dump_json())
    assert reparsed == f


def test_finding_defaults_for_optional_lists() -> None:
    f = Finding(
        rule_id="r",
        severity=Severity.INFO,
        message="m",
        rationale="r",
    )
    assert f.node_ids == []
    assert f.edge_ids == []
