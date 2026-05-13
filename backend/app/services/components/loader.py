"""Read, validate, and cache the component metadata library.

The source of truth is `components/*.yaml` at the repo root (one file per
NodeType). On first call, the loader walks that directory, parses each YAML,
validates against `ComponentMetadata`, and returns a dict keyed by NodeType.

Results are cached via `lru_cache`. Tests can clear it via `reset_for_tests()`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.schemas.component import ComponentMetadata
from app.schemas.diagram import NodeType


class ComponentNotFoundError(KeyError):
    """Raised when a caller asks for a NodeType that has no loaded metadata."""


def _components_dir() -> Path:
    """Resolve `<repo>/components/` from this file's location.

    `backend/app/services/components/loader.py` → ../../../../components
    """
    return Path(__file__).resolve().parents[3].parent / "components"


@lru_cache
def load_components() -> dict[NodeType, ComponentMetadata]:
    """Load every YAML under `components/` into validated ComponentMetadata."""
    directory = _components_dir()
    if not directory.is_dir():
        raise FileNotFoundError(f"Components directory not found: {directory}")

    result: dict[NodeType, ComponentMetadata] = {}
    for path in sorted(directory.glob("*.yaml")):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            raise ValueError(f"Could not parse YAML at {path}: {e}") from None

        if not isinstance(raw, dict):
            raise ValueError(
                f"Top-level YAML in {path} must be a mapping, got {type(raw).__name__}"
            )

        try:
            component = ComponentMetadata.model_validate(raw)
        except ValidationError as e:
            raise ValidationError.from_exception_data(
                title=f"ComponentMetadata validation failed for {path.name}",
                line_errors=e.errors(include_url=False),
            ) from None

        # Cross-check: filename stem must equal the declared `type`
        if component.type.value != path.stem:
            raise ValueError(
                f"Component file {path.name} declares type={component.type.value!r}; "
                f"filename stem must match the declared type."
            )

        result[component.type] = component

    return result


def get_component(node_type: NodeType) -> ComponentMetadata:
    """Return the ComponentMetadata for a single NodeType.

    Raises ComponentNotFoundError if no YAML defines that type.
    """
    components = load_components()
    if node_type not in components:
        raise ComponentNotFoundError(
            f"No component metadata for {node_type.value!r}. Add components/{node_type.value}.yaml."
        )
    return components[node_type]


def reset_for_tests() -> None:
    """Drop the cached load. Tests call this between cases."""
    load_components.cache_clear()
