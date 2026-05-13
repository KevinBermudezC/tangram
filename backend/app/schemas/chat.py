from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    """A single message in an LLM chat exchange.

    This is intentionally separate from `app.schemas.diagram.Message`, which is
    the conversation entry embedded inside a Diagram document. ChatMessage is
    the wire shape used to talk to LLM providers; it has system/user/assistant
    roles. Diagram.Message has user/assistant only.
    """

    role: Literal["system", "user", "assistant"]
    content: str
