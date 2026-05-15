"""PatternMatch schema round-trip."""

from __future__ import annotations

from app.schemas.diagram import NodeType
from app.schemas.pattern import Pattern, PatternComplexity
from app.schemas.retrieval import PatternMatch


def _make_pattern() -> Pattern:
    return Pattern(
        id="x-test",
        title="X Test",
        complexity=PatternComplexity.BEGINNER,
        tags=[],
        component_types=[NodeType.FRONTEND],
        body="body",
    )


def test_pattern_match_round_trip() -> None:
    m = PatternMatch(pattern=_make_pattern(), score=0.42)
    reparsed = PatternMatch.model_validate_json(m.model_dump_json())
    assert reparsed == m


def test_pattern_match_carries_score_as_float() -> None:
    m = PatternMatch(pattern=_make_pattern(), score=1)
    assert isinstance(m.score, float)
