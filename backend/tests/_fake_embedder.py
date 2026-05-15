"""Deterministic in-memory embedder for tests.

We need vectors that are:
- the same across runs (so tests are stable)
- numerically distinct for different inputs (so similarity ranking makes sense)
- cheap to compute (no real model)

The strategy: hash the text into a fixed-dimension float vector using sha256
bytes. Same input -> same vector; different input -> different vector.
"""

from __future__ import annotations

import hashlib
import struct

DIM = 16


class FakeEmbedder:
    """Async embedder protocol-compatible stand-in for tests."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [_hash_to_vector(t) for t in texts]


def _hash_to_vector(text: str) -> list[float]:
    """Map a string to a deterministic 16-float vector via repeated sha256."""
    out: list[float] = []
    seed = text.encode("utf-8")
    counter = 0
    while len(out) < DIM:
        digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
        # Unpack as little-endian floats; sha256 gives us 32 bytes -> 8 floats.
        floats = struct.unpack("<8f", digest[:32])
        for f in floats:
            # Tame extreme values so distances stay reasonable.
            if not (-1e6 < f < 1e6):
                f = 0.0
            out.append(float(f))
            if len(out) >= DIM:
                break
        counter += 1
    return out
