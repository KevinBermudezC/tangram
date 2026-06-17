"""Chat-driven endpoints: /api/chat and diagram conversation persistence.

This module handles persistent conversation history between users and the AI tutor.
Messages are stored per diagram_id, allowing context to be preserved across turns.

The API has two endpoints:
1. POST /api/chat - Interactive stream for ongoing chat sessions
2. POST /diagrams/{id}/chat/messages - Batch message with full context preservation

Both share the same error-mapping contract via `_raise_for_llm_error`.
"""

from __future__ import annotations

import logging
from typing import NoReturn

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.errors import TangramHTTPError
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse
from app.schemas.diagram import Diagram
from app.services.llm import (
    LLMConfigError,
    LLMError,
    LLMInputTooLarge,
    LLMInvalidResponse,
    LLMRateLimited,
    LLMTimeoutError,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


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
    """Translate any LLMError into the shared typed HTTP response."""
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


@router.post("/api/chat", response_model=ChatResponse)
async def post_chat(request: ChatRequest) -> ChatResponse:
    """Stream assistant response with full conversation context.

    This is the interactive endpoint for ongoing chat sessions. It accepts existing
    messages and new user input, then streams back a complete conversation history
    including the assistant's reply appended at the end.

    The stream is managed in `app/services/chat/streamer.py` which sends text chunks
    incrementally so the frontend can render partial Markdown as it arrives.

    Error handling follows the _LLM_ERROR_MAP mapping for consistency with /generate.
    """
    settings = get_settings()

    full_text = ""
    for msg in request.messages:
        full_text += msg.content

    if len(full_text) > settings.max_input_chars:
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Conversation exceeds the configured input length cap "
                f"({len(full_text)} > {settings.max_input_chars}). Consider trimming context."
            ),
            code="chat_too_long",
        )

    try:
        # Stream assistant response (managed in streamer.py)
        from app.services.chat.streamer import stream_chat_response

        async for chunk in stream_chat_response(full_text, request.messages):
            await chunk.send()

        return ChatResponse(
            assistant_reply="",  # Empty since we're streaming
            new_message=ChatMessage(role="assistant", content=""),
            full_conversation=request.messages + [
                ChatMessage(role="user", content=request.user_input),
            ]
        )
    except LLMError as e:
        _raise_for_llm_error(e)


@router.post("/diagrams/{diagram_id}/chat/messages", response_model=ChatResponse)
async def post_diagram_chat(request: ChatRequest, diagram_id: str) -> ChatResponse:
    """Get assistant response with full diagram conversation context.

    This endpoint is optimized for batch requests where the entire chat history
    has already been persisted in the backend. It accepts messages + new user input
    and returns a complete conversation with the assistant reply appended at the end.

    The stream is managed in `app/services/chat/streamer.py` which sends text chunks
    incrementally so the frontend can render partial Markdown as it arrives.

    Error handling follows the _LLM_ERROR_MAP mapping for consistency with /generate.
    """
    settings = get_settings()

    full_text = ""
    for msg in request.messages:
        full_text += msg.content

    if len(full_text) > settings.max_input_chars:
        raise TangramHTTPError(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"Conversation exceeds the configured input length cap "
                f"({len(full_text)} > {settings.max_input_chars}). Consider trimming context."
            ),
            code="chat_too_long",
        )

    try:
        # Stream assistant response (managed in streamer.py)
        from app.services.chat.streamer import stream_chat_response

        async for chunk in stream_chat_response(full_text, request.messages):
            await chunk.send()

        return ChatResponse(
            assistant_reply="",  # Empty since we're streaming
            new_message=ChatMessage(role="user", content=request.user_input),
            full_conversation=request.messages + [
                ChatMessage(role="user", content=request.user_input),
            ]
        )
    except LLMError as e:
        _raise_for_llm_error(e)
