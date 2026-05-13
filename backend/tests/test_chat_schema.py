"""Round-trip tests for the ChatMessage schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatMessage


def test_chat_message_round_trip() -> None:
    msg = ChatMessage(role="user", content="hello")
    dumped = msg.model_dump()
    reparsed = ChatMessage.model_validate(dumped)
    assert reparsed == msg


def test_chat_message_accepts_three_roles() -> None:
    for role in ("system", "user", "assistant"):
        ChatMessage(role=role, content="x")


def test_chat_message_rejects_unknown_role() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role="tool", content="x")  # type: ignore[arg-type]


def test_chat_message_requires_content() -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role="user")  # type: ignore[call-arg]
