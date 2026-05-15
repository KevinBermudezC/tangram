"""GenerateRequest and GeneratedDiagramContent round-trips."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.diagram import NodeType
from app.schemas.generate import (
    GeneratedDiagramContent,
    GeneratedEdge,
    GeneratedNode,
    GenerateRequest,
)


def test_generate_request_round_trip() -> None:
    r = GenerateRequest(prompt="delivery app")
    assert GenerateRequest.model_validate_json(r.model_dump_json()) == r


def test_empty_prompt_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="")


def test_whitespace_only_prompt_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="   \n\t  ")


def test_generated_diagram_content_round_trip() -> None:
    content = GeneratedDiagramContent(
        name="Delivery app",
        description="An example",
        nodes=[
            GeneratedNode(id="n1", type=NodeType.FRONTEND, label="App"),
            GeneratedNode(id="n2", type=NodeType.BACKEND, label="API"),
        ],
        edges=[GeneratedEdge(id="e1", source="n1", target="n2")],
    )
    reparsed = GeneratedDiagramContent.model_validate_json(content.model_dump_json())
    assert reparsed == content


def test_generated_diagram_requires_at_least_one_node() -> None:
    with pytest.raises(ValidationError):
        GeneratedDiagramContent(name="x", nodes=[], edges=[])
