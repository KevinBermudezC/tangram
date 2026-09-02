"""Chat-about-diagram: tutor + inspect tools + streamed parts."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from app.schemas.chat import ChatMessage, ChatRequest, ChatRequestMessage, ChatStreamPart
from app.schemas.diagram import Diagram
from app.services import storage
from app.services.chat.tools import CHAT_TOOLS, execute_chat_tool
from app.services.llm import get_llm
from app.services.prompts import compose_prompt

_SECTION_SEPARATOR = "\n\n---\n\n"
_MAX_TOOL_STEPS = 5

_TOOLS_HINT = """You have two tools and you must use them to see the canvas:

- `inspect_diagram` — list every node and edge.
- `inspect_node` — one node by id, plus the edges that touch it.

Do not invent nodes, types, or connections that a tool did not return.
When the user asks about a selected node ("this", "here", "why is there a
queue/cache"), call `inspect_node` with the selected id before answering.
Ground the answer in that node's label, type, and incident edges: what it
connects to, and what problem it solves *here*.
"""

NO_DIAGRAM_REPLY = (
    "I don't have a diagram to look at yet. Generate one from the home "
    "prompt or open a saved diagram, then click a node and ask me about it. "
    "I won't invent boxes that aren't on the canvas."
)


class DiagramNotFoundError(LookupError):
    """Raised when `diagram_id` is set, no live diagram was sent, and storage misses."""


async def stream_chat(request: ChatRequest) -> AsyncIterator[ChatStreamPart]:
    """Yield streamed parts. Does not write storage. Does not dump diagram JSON."""
    diagram = resolve_diagram(request)
    if diagram is None and not request.diagram_id:
        yield ChatStreamPart(type="text", text=NO_DIAGRAM_REPLY)
        return

    messages = await compose_chat_messages(request, diagram)
    llm = get_llm()
    for _ in range(_MAX_TOOL_STEPS):
        pending: list[ChatStreamPart] = []
        async for part in llm.stream_parts(messages, tools=CHAT_TOOLS):
            yield part
            if part.type == "tool-call":
                pending.append(part)
        if not pending:
            return
        tool_calls = [
            {
                "id": p.tool_call_id or f"call_{i}",
                "type": "function",
                "function": {
                    "name": p.tool_name or "",
                    "arguments": p.arguments or "{}",
                },
            }
            for i, p in enumerate(pending)
        ]
        messages.append(ChatMessage(role="assistant", content="", tool_calls=tool_calls))
        for part in pending:
            result = execute_chat_tool(part.tool_name or "", part.arguments or "{}", diagram)
            yield ChatStreamPart(
                type="tool-output",
                tool_call_id=part.tool_call_id or "call_0",
                tool_name=part.tool_name,
                output=result,
            )
            messages.append(
                ChatMessage(
                    role="tool",
                    content=json.dumps(result),
                    tool_call_id=part.tool_call_id or "call_0",
                )
            )


async def compose_chat_messages(
    request: ChatRequest, diagram: Diagram | None = None
) -> list[ChatMessage]:
    """Tutor + retrieval + tool instructions. Never injects the diagram JSON."""
    if diagram is None:
        diagram = resolve_diagram(request)
    last_user = _last_user_text(request) or "Let's talk about this architecture."
    # diagram=None on purpose: compose_prompt would otherwise dump the JSON.
    composed = await compose_prompt(last_user, diagram=None, mode_id="tutor")
    extras = [_TOOLS_HINT]
    extras.append(_selection_block(request.selected_node_id, has_diagram=diagram is not None))
    system = ChatMessage(
        role="system",
        content=composed[0].content + _SECTION_SEPARATOR + _SECTION_SEPARATOR.join(extras),
    )
    conversation = [_to_chat_message(m) for m in request.messages if m.role != "system"]
    return [system, *conversation]


def resolve_diagram(request: ChatRequest) -> Diagram | None:
    """Live `diagram` wins; otherwise load `diagram_id` from storage."""
    if request.diagram is not None:
        return request.diagram
    if not request.diagram_id:
        return None
    loaded = storage.get_diagram(request.diagram_id)
    if loaded is None:
        raise DiagramNotFoundError(request.diagram_id)
    return loaded


def _selection_block(node_id: str | None, *, has_diagram: bool) -> str:
    if not has_diagram:
        return (
            "There is no diagram in context. Do not invent nodes. "
            "Tell the user you need a diagram on the canvas."
        )
    if node_id:
        return (
            f"The editor reports selected_node_id=`{node_id}`. "
            "Call `inspect_node` with that id before answering about the "
            "selected component. Do not guess its name or type."
        )
    return (
        'No node is selected. If the user says "this" or "here", ask them '
        "to click a node. You may still call `inspect_diagram`. "
        "Never invent a node that tools did not return."
    )


def _last_user_text(request: ChatRequest) -> str:
    for msg in reversed(request.messages):
        if msg.role == "user" and msg.content:
            return msg.content
    return ""


def _to_chat_message(msg: ChatRequestMessage) -> ChatMessage:
    return ChatMessage(
        role=msg.role,
        content=msg.content or "",
        tool_call_id=msg.tool_call_id,
        tool_calls=msg.tool_calls,
    )
