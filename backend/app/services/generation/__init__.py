"""Generation service — public re-exports."""

from app.services.generation.generator import generate_diagram
from app.services.generation.layout import auto_layout

__all__ = ["auto_layout", "generate_diagram"]
