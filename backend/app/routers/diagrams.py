"""Diagram persistence routes: save, list, fetch, delete.

Storage is filesystem-backed (see app.services.storage). Errors follow the
same flat ``{"detail", "code"}`` contract as app.routers.ai: a missing
diagram is a typed 404 with ``code="diagram_not_found"`` so the frontend can
branch on a stable code.

The ``{id}`` path is constrained to the ULID shape at the routing layer, so a
traversal attempt (``..`` or ``/``) never reaches the storage service.
"""

from __future__ import annotations

from fastapi import APIRouter, Path, status
from pydantic import BaseModel

from app.errors import TangramHTTPError
from app.schemas.diagram import Diagram, DiagramSummary
from app.services import storage

router = APIRouter(prefix="/diagrams", tags=["diagrams"])

# Crockford base32, 26 chars. Mirrors storage.is_valid_diagram_id; enforced
# here so FastAPI rejects a malformed id with 422 before the handler runs.
_ULID_PATTERN = r"^[0-9A-HJKMNP-TV-Z]{26}$"

_IdPath = Path(pattern=_ULID_PATTERN, description="ULID of the diagram")


class ErrorBody(BaseModel):
    """Flat error body the frontend can branch on."""

    detail: str
    code: str


@router.post("", response_model=Diagram, status_code=status.HTTP_201_CREATED)
async def post_diagram(diagram: Diagram) -> Diagram:
    """Persist a diagram. Assigns a ULID when ``id`` is empty."""
    return storage.save_diagram(diagram)


@router.get("", response_model=list[DiagramSummary])
async def list_diagrams() -> list[DiagramSummary]:
    """List lightweight diagram summaries, newest first."""
    return storage.list_diagrams()


@router.get(
    "/{diagram_id}",
    response_model=Diagram,
    responses={404: {"model": ErrorBody, "description": "Diagram not found"}},
)
async def get_diagram(diagram_id: str = _IdPath) -> Diagram:
    """Fetch a full diagram by id."""
    diagram = storage.get_diagram(diagram_id)
    if diagram is None:
        raise TangramHTTPError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagram with id {diagram_id}.",
            code="diagram_not_found",
        )
    return diagram


@router.delete(
    "/{diagram_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorBody, "description": "Diagram not found"}},
)
async def delete_diagram(diagram_id: str = _IdPath) -> None:
    """Delete a diagram by id."""
    if not storage.delete_diagram(diagram_id):
        raise TangramHTTPError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagram with id {diagram_id}.",
            code="diagram_not_found",
        )
