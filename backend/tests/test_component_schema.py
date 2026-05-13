"""Every YAML under components/ validates and has non-empty required fields."""

from __future__ import annotations

import pytest

from app.schemas.diagram import NodeType
from app.services.components import load_components, reset_for_tests


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_for_tests()
    yield
    reset_for_tests()


def test_all_components_validate() -> None:
    loaded = load_components()
    assert len(loaded) == len(list(NodeType))


def test_required_string_fields_are_non_empty() -> None:
    for component in load_components().values():
        assert component.label.strip(), f"empty label on {component.type}"
        assert component.description.strip(), f"empty description on {component.type}"


def test_required_list_fields_are_non_empty() -> None:
    for component in load_components().values():
        assert component.typical_implementations, (
            f"empty typical_implementations on {component.type}"
        )
        assert component.common_pairings, f"empty common_pairings on {component.type}"
        assert component.tradeoffs, f"empty tradeoffs on {component.type}"
        assert component.anti_patterns, f"empty anti_patterns on {component.type}"


def test_common_pairings_only_reference_known_types() -> None:
    known = set(NodeType)
    for component in load_components().values():
        for pairing in component.common_pairings:
            assert pairing in known, (
                f"{component.type}.common_pairings references unknown type {pairing!r}"
            )


def test_type_field_matches_filename() -> None:
    """Loader cross-checks this, but we assert again at the integration level."""
    for node_type, component in load_components().items():
        assert component.type == node_type
