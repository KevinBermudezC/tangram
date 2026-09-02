"""Chat-about-diagram service — public re-exports."""

from app.services.chat.service import (
    NO_DIAGRAM_REPLY,
    DiagramNotFoundError,
    compose_chat_messages,
    resolve_diagram,
    stream_chat,
)
from app.services.chat.tools import (
    CHAT_TOOLS,
    INSPECT_DIAGRAM,
    INSPECT_NODE,
    execute_chat_tool,
    inspect_diagram,
    inspect_node,
)
from app.services.chat.ui_stream import UI_MESSAGE_STREAM_HEADERS, iter_ui_message_stream

__all__ = [
    "CHAT_TOOLS",
    "INSPECT_DIAGRAM",
    "INSPECT_NODE",
    "NO_DIAGRAM_REPLY",
    "UI_MESSAGE_STREAM_HEADERS",
    "DiagramNotFoundError",
    "compose_chat_messages",
    "execute_chat_tool",
    "inspect_diagram",
    "inspect_node",
    "iter_ui_message_stream",
    "resolve_diagram",
    "stream_chat",
]
