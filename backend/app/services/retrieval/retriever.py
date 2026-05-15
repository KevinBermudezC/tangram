"""Public retrieval API.

`retrieve_patterns(query, k)` is the only function most callers should use.
Every error path here logs a warning and returns an empty list — the LLM
endpoints should keep working even if the retrieval layer is broken.
"""

from __future__ import annotations

import logging

from app.schemas.retrieval import PatternMatch
from app.services.llm import get_embedder
from app.services.patterns import load_patterns
from app.services.retrieval.builder import build_if_needed
from app.services.retrieval.builder import force_rebuild as _force_rebuild
from app.services.retrieval.store import get_collection_if_exists

logger = logging.getLogger(__name__)


async def retrieve_patterns(query: str, k: int = 3) -> list[PatternMatch]:
    """Return up to k patterns most similar to the query, in best-first order.

    On any underlying failure (Chroma down, embedder unavailable, corrupted
    index), returns an empty list and logs a warning. Callers must tolerate
    empty results.
    """
    if k <= 0:
        return []

    try:
        await build_if_needed()
    except Exception as e:
        logger.warning("Retrieval index build failed; returning empty: %s", e)
        return []

    collection = get_collection_if_exists()
    if collection is None:
        logger.warning("Retrieval collection missing after build; returning empty.")
        return []

    try:
        embedder = get_embedder()
        query_vec = await embedder.embed([query])
    except Exception as e:
        logger.warning("Embedder failed during retrieval; returning empty: %s", e)
        return []

    try:
        results = collection.query(query_embeddings=query_vec, n_results=k)
    except Exception as e:
        logger.warning("Chroma query failed; returning empty: %s", e)
        return []

    return _materialize_results(results)


def _materialize_results(results: dict) -> list[PatternMatch]:
    """Translate Chroma's response into a list of PatternMatch."""
    ids_groups = results.get("ids") or []
    distances_groups = results.get("distances") or []
    if not ids_groups or not distances_groups:
        return []

    ids = ids_groups[0]
    distances = distances_groups[0]
    patterns = load_patterns()
    matches: list[PatternMatch] = []
    for pattern_id, distance in zip(ids, distances, strict=False):
        pattern = patterns.get(pattern_id)
        if pattern is None:
            # Index referenced a pattern that no longer exists on disk.
            # Could happen during a rebuild race; safe to skip.
            continue
        matches.append(PatternMatch(pattern=pattern, score=float(distance)))
    return matches


async def force_rebuild() -> None:
    """Unconditionally drop and rebuild the index. Useful for tests and tooling."""
    await _force_rebuild()
