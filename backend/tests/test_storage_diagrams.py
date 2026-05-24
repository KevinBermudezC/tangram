"""Unit tests for the filesystem-backed diagram storage service."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.schemas.diagram import Diagram, DiagramMetadata, Node, NodeType, Position
from app.services import storage


@pytest.fixture(autouse=True)
def _data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point DATA_DIR at an isolated tmp dir for every storage test."""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    return tmp_path


def _diagram(diagram_id: str = "", *, name: str = "Test", nodes: int = 1) -> Diagram:
    now = datetime.now(UTC)
    return Diagram(
        id=diagram_id,
        metadata=DiagramMetadata.model_validate(
            {"name": name, "description": None, "createdAt": now, "updatedAt": now}
        ),
        nodes=[
            Node(
                id=f"n{i}",
                type=NodeType.BACKEND,
                label=f"N{i}",
                position=Position(x=0, y=0),
            )
            for i in range(nodes)
        ],
        edges=[],
    )


def test_save_assigns_ulid_when_id_empty() -> None:
    saved = storage.save_diagram(_diagram(""))
    assert storage.is_valid_diagram_id(saved.id)


def test_save_then_get_round_trip(_data_dir: Path) -> None:
    saved = storage.save_diagram(_diagram("", name="Roundtrip", nodes=2))
    fetched = storage.get_diagram(saved.id)
    assert fetched is not None
    assert fetched.id == saved.id
    assert fetched.metadata.name == "Roundtrip"
    assert len(fetched.nodes) == 2
    # File lands under <DATA_DIR>/diagrams/<id>.json
    assert (_data_dir / "diagrams" / f"{saved.id}.json").exists()


def test_resave_preserves_created_at_and_bumps_updated_at() -> None:
    saved = storage.save_diagram(_diagram(""))
    original_created = saved.metadata.created_at
    original_updated = saved.metadata.updated_at

    # Mutate and re-save under the same id.
    saved.metadata.name = "Renamed"
    resaved = storage.save_diagram(saved)

    assert resaved.metadata.created_at == original_created
    assert resaved.metadata.updated_at >= original_updated
    assert resaved.metadata.name == "Renamed"


def test_get_missing_returns_none() -> None:
    assert storage.get_diagram("01HZZZZZZZZZZZZZZZZZZZZZZZ") is None


def test_get_invalid_id_returns_none() -> None:
    assert storage.get_diagram("../etc/passwd") is None


def test_list_empty_when_no_diagrams() -> None:
    assert storage.list_diagrams() == []


def test_list_is_newest_first() -> None:
    first = storage.save_diagram(_diagram(""))
    second = storage.save_diagram(_diagram(""))
    summaries = storage.list_diagrams()
    ids = [s.id for s in summaries]
    assert ids == sorted([first.id, second.id], reverse=True)


def test_list_summary_has_counts_and_no_nodes(_data_dir: Path) -> None:
    storage.save_diagram(_diagram("", nodes=3))
    summary = storage.list_diagrams()[0]
    dumped = summary.model_dump()
    assert dumped["node_count"] == 3
    assert dumped["edge_count"] == 0
    assert "nodes" not in dumped
    assert "edges" not in dumped


def test_list_summary_thumb_fits_viewbox(_data_dir: Path) -> None:
    storage.save_diagram(_diagram("", nodes=4))
    thumb = storage.list_diagrams()[0].thumb
    assert len(thumb.nodes) == 4
    for n in thumb.nodes:
        # Node rect stays inside the 200x120 viewBox.
        assert 0 <= n.x <= 200 - n.w
        assert 0 <= n.y <= 120 - n.h


def test_list_skips_corrupt_file(_data_dir: Path) -> None:
    good = storage.save_diagram(_diagram(""))
    # Drop a non-JSON file into the diagrams dir.
    (_data_dir / "diagrams" / "garbage.json").write_text("not json", encoding="utf-8")
    summaries = storage.list_diagrams()
    assert [s.id for s in summaries] == [good.id]


def test_delete_existing_returns_true(_data_dir: Path) -> None:
    saved = storage.save_diagram(_diagram(""))
    assert storage.delete_diagram(saved.id) is True
    assert storage.get_diagram(saved.id) is None


def test_delete_missing_returns_false() -> None:
    assert storage.delete_diagram("01HZZZZZZZZZZZZZZZZZZZZZZZ") is False


def test_delete_invalid_id_returns_false() -> None:
    assert storage.delete_diagram("../../boom") is False
