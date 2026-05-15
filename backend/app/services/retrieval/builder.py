"""Corpus fingerprinting and index build / rebuild.

The version key combines:
  - a sha256 over every patterns/*.md file's name and bytes
  - the currently configured embedder identifier

When the version key on disk (stored as collection metadata) differs from the
current one, we rebuild the index. Triggers: pattern edits, pattern adds,
pattern deletes, or embedder swap.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from app.core.config import get_settings
from app.services.llm import get_embedder
from app.services.patterns import load_patterns
from app.services.patterns.loader import _patterns_dir
from app.services.retrieval.store import (
    delete_collection,
    get_collection_if_exists,
    get_or_create_collection,
)

logger = logging.getLogger(__name__)


def corpus_fingerprint() -> str:
    """sha256 over every pattern file's name + bytes (sorted)."""
    h = hashlib.sha256()
    paths = sorted(_patterns_dir().glob("*.md"))
    for path in paths:
        if path.name.lower() == "readme.md":
            continue
        h.update(path.name.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def version_key() -> str:
    """Combine corpus fingerprint with the embedder id."""
    return f"{get_settings().embedder}::{corpus_fingerprint()}"


def _embed_text_for(pattern_id: str, title: str, body: str) -> str:
    """The text we feed into the embedder for a pattern."""
    return f"{title}\n\n{body}"


async def build_if_needed() -> None:
    """Check the index's version against the current one; rebuild on mismatch."""
    current_key = version_key()
    existing = get_collection_if_exists()
    if existing is not None:
        stored_key = (existing.metadata or {}).get("version_key")
        if stored_key == current_key:
            return  # up to date

    logger.info("Rebuilding pattern index (version key changed).")
    await _rebuild(current_key)


async def _rebuild(version_key_value: str) -> None:
    """Drop and recreate the collection with current patterns."""
    delete_collection()
    collection = get_or_create_collection(version_key=version_key_value)

    patterns = load_patterns()
    if not patterns:
        return  # nothing to embed; empty index is fine

    embedder = get_embedder()
    pattern_list = list(patterns.values())
    texts = [_embed_text_for(p.id, p.title, p.body) for p in pattern_list]
    vectors = await embedder.embed(texts)

    collection.upsert(
        ids=[p.id for p in pattern_list],
        embeddings=vectors,
        metadatas=[
            {
                "title": p.title,
                "complexity": p.complexity.value,
            }
            for p in pattern_list
        ],
        documents=texts,
    )


async def force_rebuild() -> None:
    """Unconditionally drop the index and rebuild."""
    await _rebuild(version_key())


def _patterns_path_for_fingerprint() -> Path:
    """Exposed only for tests that need to point fingerprinting elsewhere."""
    return _patterns_dir()
