"""Mode loader behavior + tutor mode is on disk."""

from __future__ import annotations

import pytest

from app.services.modes import (
    ModeNotFoundError,
    get_mode,
    load_modes,
    reset_for_tests,
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_for_tests()
    yield
    reset_for_tests()


def test_tutor_mode_loads() -> None:
    mode = get_mode("tutor")
    assert mode.id == "tutor"
    assert mode.title
    assert mode.summary
    assert mode.system_prompt.strip()


def test_load_modes_caches() -> None:
    first = load_modes()
    second = load_modes()
    assert first is second


def test_reset_for_tests_clears_cache() -> None:
    first = load_modes()
    reset_for_tests()
    second = load_modes()
    assert first is not second


def test_unknown_mode_raises() -> None:
    with pytest.raises(ModeNotFoundError):
        get_mode("does-not-exist")
