"""Every patterns/*.md file is well-formed and has the required sections."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.patterns import load_patterns, reset_for_tests
from app.services.patterns.loader import REQUIRED_SECTIONS

SEED_IDS = frozenset(
    {
        "crud-application",
        "jamstack",
        "background-worker",
        "realtime-chat",
        "event-driven",
    }
)


def _patterns_dir() -> Path:
    # tests/ -> backend/ -> repo root
    return Path(__file__).resolve().parents[2] / "patterns"


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_for_tests()
    yield
    reset_for_tests()


def test_seed_patterns_all_present() -> None:
    files = {p.stem for p in _patterns_dir().glob("*.md") if p.name.lower() != "readme.md"}
    missing = SEED_IDS - files
    assert not missing, f"Missing seed patterns: {sorted(missing)}"


def test_load_patterns_returns_at_least_seeds() -> None:
    loaded = load_patterns()
    for seed in SEED_IDS:
        assert seed in loaded, f"Loader missed seed pattern: {seed}"


def test_every_pattern_has_required_sections() -> None:
    for pattern in load_patterns().values():
        body_lower = pattern.body.lower()
        for required in REQUIRED_SECTIONS:
            assert required.lower() in body_lower, (
                f"Pattern {pattern.id} missing section {required!r}"
            )


def test_every_pattern_filename_matches_id() -> None:
    for path in _patterns_dir().glob("*.md"):
        if path.name.lower() == "readme.md":
            continue
        # The loader already enforces this; we double-check at the integration level.
        pattern = load_patterns().get(path.stem)
        assert pattern is not None, f"Loader didn't pick up {path.name}"
        assert pattern.id == path.stem


def test_every_pattern_has_non_empty_body() -> None:
    for pattern in load_patterns().values():
        assert pattern.body.strip(), f"{pattern.id} has empty body"
