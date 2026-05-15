"""Read, validate, and cache the patterns library.

The source of truth is `patterns/*.md` at the repo root. Each file has YAML
frontmatter (parsed into Pattern metadata) and a markdown body. The body must
contain a known set of section headers; the loader enforces this.

Cached via `lru_cache`. Tests clear it via `reset_for_tests()`.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from app.schemas.pattern import Pattern


class PatternNotFoundError(KeyError):
    """Raised when a caller asks for a pattern id that has no loaded file."""


REQUIRED_SECTIONS = (
    "What it is",
    "When to use",
    "When to avoid",
    "Components involved",
    "Common pitfalls",
)


def _patterns_dir() -> Path:
    """Resolve `<repo>/patterns/` from this file's location.

    `backend/app/services/patterns/loader.py` -> ../../../../patterns
    """
    return Path(__file__).resolve().parents[3].parent / "patterns"


def _normalize_header(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def _missing_sections(body: str) -> list[str]:
    found: set[str] = set()
    for line in body.splitlines():
        # Match a level-2 header: "## Header text"
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            found.add(_normalize_header(match.group(1)))
    required_norm = {_normalize_header(s) for s in REQUIRED_SECTIONS}
    missing_norm = required_norm - found
    # Return original-cased section names so the error is readable.
    return [s for s in REQUIRED_SECTIONS if _normalize_header(s) in missing_norm]


@lru_cache
def load_patterns() -> dict[str, Pattern]:
    """Walk `patterns/`, parse each `.md`, validate, return id-keyed dict."""
    directory = _patterns_dir()
    if not directory.is_dir():
        raise FileNotFoundError(f"Patterns directory not found: {directory}")

    result: dict[str, Pattern] = {}
    for path in sorted(directory.glob("*.md")):
        # Skip the README — it's documentation, not a pattern.
        if path.name.lower() == "readme.md":
            continue

        try:
            doc = frontmatter.load(path)
        except Exception as e:
            raise ValueError(f"Could not parse frontmatter at {path}: {e}") from None

        metadata = dict(doc.metadata)
        body = doc.content

        if not metadata:
            raise ValueError(f"{path.name}: missing frontmatter block")

        # The Pattern model gets the body as a field, not from frontmatter.
        metadata["body"] = body

        try:
            pattern = Pattern.model_validate(metadata)
        except ValidationError as e:
            raise ValueError(f"Pattern validation failed for {path.name}: {e}") from None

        if pattern.id != path.stem:
            raise ValueError(f"{path.name}: declares id={pattern.id!r}; filename stem must match")

        missing = _missing_sections(body)
        if missing:
            raise ValueError(f"{path.name}: missing required section(s): {', '.join(missing)}")

        result[pattern.id] = pattern

    return result


def get_pattern(pattern_id: str) -> Pattern:
    """Return one Pattern by id. Raises PatternNotFoundError on unknown id."""
    patterns = load_patterns()
    if pattern_id not in patterns:
        raise PatternNotFoundError(
            f"No pattern with id {pattern_id!r}. Available: {sorted(patterns)}"
        )
    return patterns[pattern_id]


def reset_for_tests() -> None:
    """Drop the cached load. Tests call this between cases."""
    load_patterns.cache_clear()
