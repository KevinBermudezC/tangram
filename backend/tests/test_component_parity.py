"""Every NodeType has a matching YAML; no extras."""

from __future__ import annotations

from pathlib import Path

from app.schemas.diagram import NodeType
from app.services.components import load_components, reset_for_tests


def _components_dir() -> Path:
    # tests live in backend/tests/; components/ is at repo root
    return Path(__file__).resolve().parents[2] / "components"


def test_every_node_type_has_a_yaml_file() -> None:
    files = {p.stem for p in _components_dir().glob("*.yaml")}
    enum_values = {nt.value for nt in NodeType}
    missing = enum_values - files
    extra = files - enum_values
    assert not missing, f"NodeType values without a YAML: {sorted(missing)}"
    assert not extra, f"YAML files without a NodeType: {sorted(extra)}"


def test_load_components_returns_one_per_type() -> None:
    reset_for_tests()
    loaded = load_components()
    assert set(loaded.keys()) == set(NodeType)
    reset_for_tests()
