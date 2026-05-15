"""Read, validate, and cache the modes library.

Source of truth: `modes/*.md` at the repo root. Same pattern as the patterns
loader — frontmatter for metadata, markdown body for the system prompt.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import frontmatter
from pydantic import ValidationError

from app.schemas.mode import Mode


class ModeNotFoundError(KeyError):
    """Raised when a caller asks for a mode id that has no file."""


def _modes_dir() -> Path:
    """Resolve `<repo>/modes/` from this file's location."""
    return Path(__file__).resolve().parents[3].parent / "modes"


@lru_cache
def load_modes() -> dict[str, Mode]:
    """Walk `modes/`, parse each `.md`, validate, return id-keyed dict."""
    directory = _modes_dir()
    if not directory.is_dir():
        raise FileNotFoundError(f"Modes directory not found: {directory}")

    result: dict[str, Mode] = {}
    for path in sorted(directory.glob("*.md")):
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

        metadata["system_prompt"] = body

        try:
            mode = Mode.model_validate(metadata)
        except ValidationError as e:
            raise ValueError(f"Mode validation failed for {path.name}: {e}") from None

        if mode.id != path.stem:
            raise ValueError(f"{path.name}: declares id={mode.id!r}; filename stem must match")

        result[mode.id] = mode

    return result


def get_mode(mode_id: str) -> Mode:
    """Return one Mode by id. Raises ModeNotFoundError on unknown id."""
    modes = load_modes()
    if mode_id not in modes:
        raise ModeNotFoundError(f"No mode with id {mode_id!r}. Available: {sorted(modes)}")
    return modes[mode_id]


def reset_for_tests() -> None:
    """Drop the cached load. Tests call this between cases."""
    load_modes.cache_clear()
