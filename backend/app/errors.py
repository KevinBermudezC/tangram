"""Application-level error type plus its FastAPI exception handler.

We define a dedicated exception so we can produce a *flat*
`{"detail": str, "code": str}` response body. FastAPI's built-in
`HTTPException` always wraps `detail` under an outer `"detail"` key, which
would nest `code` one level deeper than we want.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class TangramHTTPError(Exception):
    """Raise to emit a flat `{detail, code}` JSON error response."""

    def __init__(self, *, status_code: int, detail: str, code: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.code = code


async def tangram_error_handler(
    request: Request,  # noqa: ARG001 — FastAPI signature
    exc: TangramHTTPError,
) -> JSONResponse:
    """Serialize TangramHTTPError as a flat top-level body."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )
