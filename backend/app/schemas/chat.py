from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.diagram import Diagram


class ChatMessage(BaseModel):
    """A single message in an LLM chat exchange.

    This is intentionally separate from `app.schemas.diagram.Message`, which is
    the conversation entry embedded inside a Diagram document. ChatMessage is
    the wire shape used to talk to LLM providers; it has system/user/assistant
    roles plus `tool` for native tool-result turns. Diagram.Message has
    user/assistant only.
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ChatStreamPart(BaseModel):
    """One piece of a chat stream.

    Providers emit `text` and `tool-call`. The chat service also emits
    `tool-output` after executing `inspect_diagram` / `inspect_node`.
    """

    type: Literal["text", "tool-call", "tool-output"]
    text: str | None = None
    tool_call_id: str | None = None
    tool_name: str | None = None
    arguments: str | None = None
    output: Any | None = None


class ChatRequestMessage(BaseModel):
    """A turn on POST /chat."""

    model_config = ConfigDict(extra="ignore")

    role: Literal["system", "user", "assistant", "tool"]
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


class ChatRequest(BaseModel):
    """Request body for POST /chat.

    Public contract: messages plus an optional live snapshot and selection.
    `diagram_id` is optional; unsaved canvases send `diagram` only.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    messages: list[ChatRequestMessage] = Field(min_length=1)
    diagram_id: str | None = Field(default=None, alias="diagramId")
    selected_node_id: str | None = Field(default=None, alias="selectedNodeId")
    diagram: Diagram | None = None
