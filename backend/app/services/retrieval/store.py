"""Chroma client + collection management.

Wraps Chroma so the rest of the retrieval layer doesn't import chromadb
directly. Production uses a persistent client at `<CHROMA_PATH>`; tests
override via `set_client_for_tests()` with an in-memory client.
"""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

import chromadb

from app.core.config import get_settings

if TYPE_CHECKING:
    from chromadb.api import ClientAPI
    from chromadb.api.models.Collection import Collection


COLLECTION_NAME = "patterns"

_client_override: Any = None  # set by tests via set_client_for_tests


def _build_persistent_client() -> ClientAPI:
    settings = get_settings()
    path = settings.chroma_path
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def get_client() -> ClientAPI:
    """Return the Chroma client. Honors test overrides."""
    if _client_override is not None:
        return _client_override
    return _build_persistent_client()


def set_client_for_tests(client: Any | None) -> None:
    """Replace the client for testing. Pass None to clear the override."""
    global _client_override
    _client_override = client


def get_or_create_collection(version_key: str) -> Collection:
    """Return the patterns collection, creating it (with version metadata) if needed."""
    client = get_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"version_key": version_key},
    )


def get_collection_if_exists() -> Collection | None:
    """Return the collection without creating it. None if it doesn't exist."""
    client = get_client()
    try:
        return client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return None


def delete_collection() -> None:
    """Delete the collection. Idempotent."""
    client = get_client()
    # Collection didn't exist or already gone -> nothing to do.
    with contextlib.suppress(Exception):
        client.delete_collection(name=COLLECTION_NAME)
