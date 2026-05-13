"""Component metadata library — public re-exports."""

from app.services.components.loader import (
    ComponentNotFoundError,
    get_component,
    load_components,
    reset_for_tests,
)

__all__ = [
    "ComponentNotFoundError",
    "get_component",
    "load_components",
    "reset_for_tests",
]
