"""Mode schema round-trip and validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.mode import Mode


def _valid() -> dict:
    return {
        "id": "tutor",
        "title": "Tutor",
        "summary": "Pedagogical persona.",
        "system_prompt": "You are Tangram.",
    }


def test_round_trip() -> None:
    m = Mode.model_validate(_valid())
    assert Mode.model_validate_json(m.model_dump_json()) == m


def test_empty_prompt_rejected() -> None:
    bad = _valid()
    bad["system_prompt"] = "   "
    with pytest.raises(ValidationError):
        Mode.model_validate(bad)


def test_non_kebab_id_rejected() -> None:
    bad = _valid()
    bad["id"] = "Tutor_Mode"
    with pytest.raises(ValidationError):
        Mode.model_validate(bad)


def test_empty_summary_rejected() -> None:
    bad = _valid()
    bad["summary"] = ""
    with pytest.raises(ValidationError):
        Mode.model_validate(bad)
