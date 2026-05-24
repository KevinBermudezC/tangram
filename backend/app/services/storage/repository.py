"""Filesystem-backed diagram storage.

One JSON file per diagram at ``<DATA_DIR>/diagrams/<id>.json``, per the
``persistence-layer`` spec. No relational database; the directory is created
on first write. Ids are ULIDs (lexicographically sortable by creation time),
so "newest first" is a plain reverse string sort with no extra index.

Writes are atomic (temp file + ``os.replace``) so a reader never observes a
half-written file. Listing tolerates a corrupt file by skipping it.
"""

from __future__ import annotations

import logging
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from ulid import ULID

from app.core.config import get_settings
from app.schemas.diagram import Diagram, DiagramSummary

logger = logging.getLogger(__name__)

# Crockford base32, 26 chars — the canonical ULID shape. Excludes I, L, O, U.
# Validating against this before any filesystem access prevents path traversal
# (an id with `/` or `..` can never match).
_ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")


def is_valid_diagram_id(diagram_id: str) -> bool:
    """True if ``diagram_id`` is a syntactically valid ULID."""
    return bool(_ULID_RE.match(diagram_id))


def _diagrams_dir() -> Path:
    return get_settings().data_dir / "diagrams"


def _path_for(diagram_id: str) -> Path:
    return _diagrams_dir() / f"{diagram_id}.json"


def save_diagram(diagram: Diagram) -> Diagram:
    """Persist ``diagram`` and return the stored form.

    Assigns a ULID when ``id`` is empty. Always sets ``updatedAt`` to now;
    preserves ``createdAt`` from an existing file, otherwise sets it to now.
    """
    now = datetime.now(UTC)
    diagram_id = diagram.id or str(ULID())
    path = _path_for(diagram_id)

    created_at = now
    if path.exists():
        try:
            existing = Diagram.model_validate_json(path.read_text(encoding="utf-8"))
            created_at = existing.metadata.created_at
        except Exception:  # noqa: BLE001 — corrupt prior file: fall back to now
            logger.warning("Existing diagram %s is unreadable; resetting createdAt", diagram_id)

    diagram.id = diagram_id
    diagram.metadata.created_at = created_at
    diagram.metadata.updated_at = now

    _atomic_write(path, diagram.model_dump_json(by_alias=True, indent=2))
    return diagram


def get_diagram(diagram_id: str) -> Diagram | None:
    """Return the stored diagram, or ``None`` if there is no file for the id."""
    if not is_valid_diagram_id(diagram_id):
        return None
    path = _path_for(diagram_id)
    if not path.exists():
        return None
    return Diagram.model_validate_json(path.read_text(encoding="utf-8"))


def list_diagrams() -> list[DiagramSummary]:
    """Return summaries for every stored diagram, newest first.

    A file that fails to parse is logged and skipped rather than failing the
    whole listing.
    """
    directory = _diagrams_dir()
    if not directory.exists():
        return []

    summaries: list[DiagramSummary] = []
    for path in directory.glob("*.json"):
        try:
            diagram = Diagram.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — skip corrupt/foreign files, keep listing
            logger.warning("Skipping unreadable diagram file: %s", path.name)
            continue
        summaries.append(DiagramSummary.from_diagram(diagram))

    # ULID ids sort lexicographically by creation time; reverse => newest first.
    summaries.sort(key=lambda s: s.id, reverse=True)
    return summaries


def delete_diagram(diagram_id: str) -> bool:
    """Delete the stored diagram. Return ``False`` if no file existed."""
    if not is_valid_diagram_id(diagram_id):
        return False
    path = _path_for(diagram_id)
    if not path.exists():
        return False
    path.unlink()
    return True


def _atomic_write(path: Path, content: str) -> None:
    """Write ``content`` to ``path`` atomically, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Temp file in the same directory so os.replace is an atomic rename.
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_name, path)
    except Exception:
        Path(tmp_name).unlink(missing_ok=True)
        raise
