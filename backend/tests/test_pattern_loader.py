"""Loader caches results, get_pattern + reset_for_tests behave."""

from __future__ import annotations

import pytest

from app.services.patterns import (
    PatternNotFoundError,
    get_pattern,
    load_patterns,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_for_tests()
    yield
    reset_for_tests()


def test_load_patterns_caches() -> None:
    first = load_patterns()
    second = load_patterns()
    assert first is second


def test_reset_for_tests_clears_cache() -> None:
    first = load_patterns()
    reset_for_tests()
    second = load_patterns()
    assert first is not second


def test_get_pattern_returns_seed() -> None:
    pattern = get_pattern("crud-application")
    assert pattern.id == "crud-application"
    assert pattern.title


def test_get_pattern_unknown_raises() -> None:
    with pytest.raises(PatternNotFoundError):
        get_pattern("totally-not-a-real-pattern")
