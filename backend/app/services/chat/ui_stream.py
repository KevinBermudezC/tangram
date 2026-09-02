"""Encode chat parts as the AI SDK UI Message Stream the rail already consumes."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from app.schemas.chat import ChatStreamPart

UI_MESSAGE_STREAM_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "x-vercel-ai-ui-message-stream": "v1",
    "x-accel-buffering": "no",
}


def _data(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def iter_ui_message_stream(
    parts: AsyncIterator[ChatStreamPart],
) -> AsyncIterator[str]:
    """Yield SSE lines for start/text/tool/finish plus the [DONE] sentinel."""
    yield _data({"type": "start"})
    text_id = "0"
    text_open = False
    async for part in parts:
        if part.type == "text":
            if not text_open:
                yield _data({"type": "text-start", "id": text_id})
                text_open = True
            yield _data({"type": "text-delta", "id": text_id, "delta": part.text or ""})
        elif part.type == "tool-call":
            if text_open:
                yield _data({"type": "text-end", "id": text_id})
                text_open = False
            try:
                tool_input = json.loads(part.arguments or "{}")
            except json.JSONDecodeError:
                tool_input = {"raw": part.arguments or ""}
            call_id = part.tool_call_id or "call_0"
            yield _data(
                {
                    "type": "tool-input-start",
                    "toolCallId": call_id,
                    "toolName": part.tool_name or "",
                }
            )
            yield _data(
                {
                    "type": "tool-input-available",
                    "toolCallId": call_id,
                    "toolName": part.tool_name or "",
                    "input": tool_input,
                }
            )
        elif part.type == "tool-output":
            yield _data(
                {
                    "type": "tool-output-available",
                    "toolCallId": part.tool_call_id or "call_0",
                    "output": part.output,
                }
            )
        else:
            _never = part.type
            raise RuntimeError(f"unhandled chat stream part: {_never}")
    if text_open:
        yield _data({"type": "text-end", "id": text_id})
    yield _data({"type": "finish"})
    yield "data: [DONE]\n\n"
