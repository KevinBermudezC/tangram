"""AI-driven endpoints: /generate now, /analyze later.

Wires the public HTTP shape to the generator service. The error-mapping in
this module is the contract the frontend will branch on: every internal
LLMError subclass becomes a typed HTTP response with a stable top-level
`code` field.

Error responses are emitted via `TangramHTTPError`, which the app-level
exception handler (registered in app.main) serializes as a flat
`{"detail": str, "code": str}` body. We avoid raising raw FastAPI
HTTPExceptions for typed errors because FastAPI wraps their detail under
an extra `"detail"` key, which would nest `code` one level too deep.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.errors import TangramHTTPError
from app.schemas.diagram import Diagram
from app.schemas.generate import GenerateRequest
from app.services.generation import generate_diagram
from app.services.llm import (
    LLMConfigError,
    LLMError,
    LLMInputTooLarge,
    LLMInvalidResponse,
    LLMRateLimited,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


class ErrorBody(BaseModel):
    """Flat error body the frontend can branch on."""

    detail: str
    code: str


@router.post(
    "/generate",
    response_model=Diagram,
    responses={
        413: {"model": ErrorBody, "description": "Prompt too long"},
        422: {"description": "Invalid request body (FastAPI default shape)"},
        429: {"model": ErrorBody, "description": "LLM provider rate-limited the request"},
        500: {"model": ErrorBody, "description": "Unexpected error"},
        502: {"model": ErrorBody, "description": "LLM returned an invalid response"},
        503: {"model": ErrorBody, "description": "LLM provider misconfigured or unavailable"},
        504: {"model": ErrorBody, "description": "LLM provider timed out"},
    },
)
async def post_generate(request: GenerateRequest) -> Diagram:
    """Generate a Diagram from a free-text prompt."""
    settings = get_settings()
    if len(request.prompt) > settings.max_input_chars:
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Prompt exceeds the configured input length cap "
                f"({len(request.prompt)} > {settings.max_input_chars})."
            ),
            code="prompt_too_long",
        )

    try:
        return await generate_diagram(request.prompt)
    except LLMInputTooLarge as e:
        # Defensive: prompt-length is already pre-checked above, but LLM input
        # also includes the composed system prompt. If it's still too long,
        # surface the same 413 contract.
        logger.warning("LLM input too large: %s", e)
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(e),
            code="llm_input_too_large",
        ) from None
    except LLMRateLimited as e:
        logger.warning("LLM rate limited: %s", e)
        raise TangramHTTPError(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
            code="llm_rate_limited",
        ) from None
    except LLMTimeoutError as e:
        logger.warning("LLM timed out: %s", e)
        raise TangramHTTPError(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(e),
            code="llm_timeout",
        ) from None
    except LLMInvalidResponse as e:
        logger.warning("LLM returned invalid response: %s", e)
        raise TangramHTTPError(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
            code="llm_invalid_response",
        ) from None
    except LLMConfigError as e:
        logger.error("LLM misconfigured: %s", e)
        raise TangramHTTPError(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
            code="llm_config_error",
        ) from None
    except LLMError as e:
        logger.exception("Unexpected LLM error")
        raise TangramHTTPError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or "Unexpected LLM error",
            code="llm_error",
        ) from None
