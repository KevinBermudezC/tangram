"""AnalyzeRequest and AnalyzeResponse round-trips."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.schemas.diagram import NodeType
from app.schemas.finding import Finding, Severity
from tests._diagram_factories import make_diagram, make_edge, make_node


def _diagram():
    return make_diagram(
        nodes=[
            make_node("front", NodeType.FRONTEND),
            make_node("db", NodeType.DATABASE),
        ],
        edges=[make_edge("e1", "front", "db")],
    )


def test_analyze_request_round_trip() -> None:
    r = AnalyzeRequest(diagram=_diagram())
    assert AnalyzeRequest.model_validate_json(r.model_dump_json(by_alias=True)) == r


def test_mode_id_defaults_to_tutor() -> None:
    r = AnalyzeRequest(diagram=_diagram())
    assert r.mode_id == "tutor"


def test_mode_id_accepts_alias_and_field_name() -> None:
    diagram = _diagram().model_dump(by_alias=True)
    by_alias = AnalyzeRequest.model_validate({"diagram": diagram, "modeId": "senior"})
    by_name = AnalyzeRequest.model_validate({"diagram": diagram, "mode_id": "senior"})
    assert by_alias.mode_id == by_name.mode_id == "senior"


def test_missing_diagram_rejected() -> None:
    with pytest.raises(ValidationError):
        AnalyzeRequest.model_validate({"mode_id": "tutor"})


def test_analyze_response_round_trip() -> None:
    resp = AnalyzeResponse(
        findings=[
            Finding(
                rule_id="no-direct-frontend-to-database",
                severity=Severity.ERROR,
                message="Frontend talks to the database directly.",
                rationale="Put an API between them.",
                node_ids=["front", "db"],
                edge_ids=["e1"],
            )
        ],
        feedback="Your frontend reaches the database directly; add a backend layer.",
    )
    assert AnalyzeResponse.model_validate_json(resp.model_dump_json()) == resp


def test_analyze_response_allows_empty_findings() -> None:
    resp = AnalyzeResponse(findings=[], feedback="Looks clean.")
    assert resp.findings == []
    assert resp.feedback
