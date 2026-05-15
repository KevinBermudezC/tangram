"""Schemas for the pattern retrieval layer.

`PatternMatch` is what retrieval returns: a Pattern instance and a similarity
score. Score semantics: lower means closer (cosine distance, Chroma's default).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.pattern import Pattern


class PatternMatch(BaseModel):
    """One retrieved pattern with its similarity score.

    Score is cosine distance (lower = more similar) as returned by Chroma.
    """

    pattern: Pattern
    score: float = Field(description="Cosine distance from the query. Lower = more similar.")
