"""strip_markdown_fence helper — defensive parsing for chatty LLMs."""

from __future__ import annotations

from app.services.llm.base import strip_markdown_fence


def test_no_fence_is_unchanged() -> None:
    text = '{"a": 1}'
    assert strip_markdown_fence(text) == text


def test_json_fence_is_stripped() -> None:
    text = '```json\n{"a": 1}\n```'
    assert strip_markdown_fence(text) == '{"a": 1}'


def test_plain_fence_is_stripped() -> None:
    text = '```\n{"a": 1}\n```'
    assert strip_markdown_fence(text) == '{"a": 1}'


def test_fence_with_trailing_blank_lines() -> None:
    text = '```json\n{"a": 1}\n```\n\n'
    assert strip_markdown_fence(text) == '{"a": 1}'


def test_leading_whitespace_then_fence() -> None:
    text = '   \n```json\n{"a": 1}\n```'
    assert strip_markdown_fence(text) == '{"a": 1}'


def test_multiline_payload_is_preserved() -> None:
    text = '```json\n{\n  "a": 1,\n  "b": [1, 2]\n}\n```'
    expected = '{\n  "a": 1,\n  "b": [1, 2]\n}'
    assert strip_markdown_fence(text) == expected


def test_partial_fence_at_start_only_no_close() -> None:
    # Some models forget to close the fence. We still strip the opener.
    text = '```json\n{"a": 1}'
    assert strip_markdown_fence(text) == '{"a": 1}'


def test_text_starts_with_backticks_but_not_a_fence() -> None:
    # Single line, no newline -> can't be a proper fence wrapper.
    text = "```not a fence"
    assert strip_markdown_fence(text) == text
