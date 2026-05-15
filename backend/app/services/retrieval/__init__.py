"""Pattern retrieval — public re-exports.

Callers should import only from this module. Internals (Chroma store, builder,
fingerprint) are not part of the public surface.
"""

from app.schemas.retrieval import PatternMatch
from app.services.retrieval.retriever import force_rebuild, retrieve_patterns

__all__ = [
    "PatternMatch",
    "force_rebuild",
    "retrieve_patterns",
]
