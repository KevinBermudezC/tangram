"""Pattern schema round-trip and validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.diagram import NodeType
from app.schemas.pattern import Pattern, PatternComplexity


def _valid_pattern_dict() -> dict:
    return {
        "id": "test-pattern",
        "title": "Test Pattern",
        "complexity": "beginner",
        "tags": ["example"],
        "component_types": [NodeType.FRONTEND, NodeType.BACKEND],
        "body": "## What it is\n\nA test.",
    }


def test_round_trip() -> None:
    pattern = Pattern.model_validate(_valid_pattern_dict())
    reparsed = Pattern.model_validate_json(pattern.model_dump_json())
    assert reparsed == pattern


def test_complexity_enum_is_closed() -> None:
    bad = _valid_pattern_dict()
    bad["complexity"] = "expert"  # not in the enum
    with pytest.raises(ValidationError):
        Pattern.model_validate(bad)


def test_unknown_component_type_rejected() -> None:
    bad = _valid_pattern_dict()
    bad["component_types"] = ["frontend", "blockchain"]
    with pytest.raises(ValidationError):
        Pattern.model_validate(bad)


def test_id_must_be_kebab_case() -> None:
    bad = _valid_pattern_dict()
    bad["id"] = "Test_Pattern"  # underscore + uppercase
    with pytest.raises(ValidationError):
        Pattern.model_validate(bad)


def test_empty_body_rejected() -> None:
    bad = _valid_pattern_dict()
    bad["body"] = "   "
    with pytest.raises(ValidationError):
        Pattern.model_validate(bad)


def test_no_component_types_rejected() -> None:
    bad = _valid_pattern_dict()
    bad["component_types"] = []
    with pytest.raises(ValidationError):
        Pattern.model_validate(bad)


def test_all_complexity_values_accepted() -> None:
    for c in PatternComplexity:
        data = _valid_pattern_dict()
        data["complexity"] = c.value
        Pattern.model_validate(data)
