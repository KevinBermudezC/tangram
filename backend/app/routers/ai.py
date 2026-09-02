"""AI-driven endpoints: /generate, /analyze, and /chat.

Wires the public HTTP shape to the generator, analyzer, and chat services. The
error-mapping in this module is the contract the frontend will branch on:
every internal LLMError subclass becomes a typed HTTP response with a stable
top-level `code` field. All three routes share the same mapping via
`_raise_for_llm_error` so they can never silently diverge.

Error responses are emitted via `TangramHTTPError`, which the app-level
exception handler (registered in app.main) serializes as a flat
`{"detail": str, "code": str}` body. We avoid raising raw FastAPI
HTTPExceptions for typed errors because FastAPI wraps their detail under
an extra `"detail"` key, which would nest `code` one level too deep.
"""

from __future__ import annotations

import logging
from typing import NoReturn

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.config import get_settings
from app.errors import TangramHTTPError
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.schemas.chat import ChatRequest
from app.schemas.diagram import Diagram
from app.schemas.generate import GenerateRequest
from app.services.analysis import analyze_diagram
from app.services.chat import (
    UI_MESSAGE_STREAM_HEADERS,
    DiagramNotFoundError,
    iter_ui_message_stream,
    stream_chat,
)
from app.services.generation import generate_diagram
from app.services.llm import (
    LLMConfigError,
    LLMError,
    LLMInputTooLarge,
    LLMInvalidResponse,
    LLMRateLimited,
    LLMTimeoutError,
)
from app.services.modes import ModeNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ai"])


class ErrorBody(BaseModel):
    """Flat error body the frontend can branch on."""

    detail: str
    code: str


# Maps the LLM error families to (HTTP status, stable `code`). Shared by every
# AI route. `LLMError` is the catch-all and is handled last.
_LLM_ERROR_MAP: list[tuple[type[LLMError], int, str]] = [
    (LLMInputTooLarge, status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "llm_input_too_large"),
    (LLMRateLimited, status.HTTP_429_TOO_MANY_REQUESTS, "llm_rate_limited"),
    (LLMTimeoutError, status.HTTP_504_GATEWAY_TIMEOUT, "llm_timeout"),
    (LLMInvalidResponse, status.HTTP_502_BAD_GATEWAY, "llm_invalid_response"),
    (LLMConfigError, status.HTTP_503_SERVICE_UNAVAILABLE, "llm_config_error"),
]


def _raise_for_llm_error(exc: LLMError) -> NoReturn:
    """Translate any LLMError into the shared typed HTTP response.

    Every AI route funnels its LLM failures through here so the status/code
    contract stays identical across endpoints.
    """
    for err_type, status_code, code in _LLM_ERROR_MAP:
        if isinstance(exc, err_type):
            log = logger.error if status_code >= 500 else logger.warning
            log("LLM error (%s): %s", code, exc)
            raise TangramHTTPError(
                status_code=status_code,
                detail=str(exc),
                code=code,
            ) from None

    # Unclassified LLMError → 500.
    logger.exception("Unexpected LLM error")
    raise TangramHTTPError(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=str(exc) or "Unexpected LLM error",
        code="llm_error",
    ) from None


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
    except LLMError as e:
        _raise_for_llm_error(e)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        413: {"model": ErrorBody, "description": "Diagram too large"},
        422: {"description": "Invalid request body or unknown mode"},
        429: {"model": ErrorBody, "description": "LLM provider rate-limited the request"},
        500: {"model": ErrorBody, "description": "Unexpected error"},
        502: {"model": ErrorBody, "description": "LLM returned an invalid response"},
        503: {"model": ErrorBody, "description": "LLM provider misconfigured or unavailable"},
        504: {"model": ErrorBody, "description": "LLM provider timed out"},
    },
)
async def post_analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze a Diagram: deterministic rule findings plus LLM prose feedback.

    Read-only: the diagram is never mutated or persisted. `findings` come from
    the rules engine and are returned even when empty; `feedback` is the
    tutor's narrative. If the LLM call fails the whole request fails with the
    mapped status — we do not return a findings-only partial success.
    """
    settings = get_settings()
    serialized_len = len(request.diagram.model_dump_json(by_alias=True))
    if serialized_len > settings.max_input_chars:
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Diagram exceeds the configured input length cap "
                f"({serialized_len} > {settings.max_input_chars})."
            ),
            code="diagram_too_large",
        )

    try:
        return await analyze_diagram(request.diagram, mode_id=request.mode_id)
    except ModeNotFoundError:
        logger.warning("Unknown mode requested: %r", request.mode_id)
        raise TangramHTTPError(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown mode: {request.mode_id!r}",
            code="unknown_mode",
        ) from None
    except LLMError as e:
        _raise_for_llm_error(e)


@router.post(
    "/chat",
    responses={
        404: {"model": ErrorBody, "description": "diagram_id not found in storage"},
        413: {"model": ErrorBody, "description": "Chat payload too long"},
        422: {"description": "Invalid request body (FastAPI default shape)"},
        429: {"model": ErrorBody, "description": "LLM provider rate-limited the request"},
        500: {"model": ErrorBody, "description": "Unexpected error"},
        502: {"model": ErrorBody, "description": "LLM returned an invalid response"},
        503: {"model": ErrorBody, "description": "LLM provider misconfigured or unavailable"},
        504: {"model": ErrorBody, "description": "LLM provider timed out"},
    },
)
async def post_chat(request: ChatRequest) -> StreamingResponse:
    """Stream a tutor reply about the current diagram.

    SSE body is the UI Message Stream protocol (`text-*` and tool parts) so
    `useChat` on the rail can render it. The Next.js `/api/chat` route
    proxies this stream; inference and inspect tools stay here.
    """
    settings = get_settings()
    serialized_len = len(request.model_dump_json(by_alias=True))
    if serialized_len > settings.max_input_chars:
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                "Chat payload exceeds the configured input length cap "
                f"({serialized_len} > {settings.max_input_chars})."
            ),
            code="chat_input_too_large",
        )

    parts = stream_chat(request)
    first = None
    try:
        first = await anext(parts)
    except StopAsyncIteration:
        first = None
    except DiagramNotFoundError:
        logger.warning("Chat requested unknown diagram_id=%r", request.diagram_id)
        raise TangramHTTPError(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagram with id {request.diagram_id}.",
            code="diagram_not_found",
        ) from None
    except LLMError as e:
        _raise_for_llm_error(e)

    async def _with_first():
        if first is not None:
            yield first
        async for part in parts:
            yield part

    async def body():
        try:
            async for event in iter_ui_message_stream(_with_first()):
                yield event
        except LLMError as exc:
            logger.error("LLM error after chat stream started: %s", exc)
            return

    return StreamingResponse(
        body(),
        media_type="text/event-stream",
        headers=UI_MESSAGE_STREAM_HEADERS,
    )
