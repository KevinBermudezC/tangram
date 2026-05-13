"""Loader caches results, reset_for_tests clears, get_component lookups work."""

from __future__ import annotations

import pytest

from app.schemas.diagram import NodeType
from app.services.components import (
    ComponentNotFoundError,
    get_component,
    load_components,
    reset_for_tests,
)
from app.services.components import loader as loader_module


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_for_tests()
    yield
    reset_for_tests()


def test_load_components_caches() -> None:
    first = load_components()
    second = load_components()
    assert first is second  # same object — cache hit


def test_reset_for_tests_clears_cache() -> None:
    first = load_components()
    reset_for_tests()
    second = load_components()
    assert first is not second  # different objects — cache was rebuilt


def test_get_component_returns_loaded_metadata() -> None:
    component = get_component(NodeType.DATABASE)
    assert component.type == NodeType.DATABASE
    assert component.label
    assert component.typical_implementations


def test_get_component_raises_for_unloaded_type(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate an enum value whose YAML is missing.

    All eight YAML files exist today, so we patch `load_components` to return
    a dict that's missing one. This exercises the KeyError path without
    deleting real fixtures.
    """
    monkeypatch.setattr(loader_module, "load_components", lambda: {})
    with pytest.raises(ComponentNotFoundError):
        get_component(NodeType.DATABASE)
