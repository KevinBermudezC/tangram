## ADDED Requirements

### Requirement: Streaming parts can include native tool calls

The `LLMProvider` protocol SHALL expose `stream_parts(messages, *, tools=None, max_tokens=None, temperature=0.7)` as an async iterator of parts. A part is either text (`type="text"`, non-empty `text`) or a tool call (`type="tool-call"`, `tool_call_id`, `tool_name`, `arguments` JSON string). When `tools` is omitted or empty, `stream_parts` SHALL yield only text parts whose concatenation matches `stream()`. Existing `stream()`, `generate()`, and `generate_structured()` SHALL remain text/structured-only so `/generate` and `/analyze` are unaffected.

#### Scenario: Text-only stream_parts matches stream()

- **WHEN** a caller iterates `stream_parts(messages)` with no tools
- **THEN** every part has `type="text"`
- **AND** concatenating `text` equals concatenating `stream(messages)`

#### Scenario: Tools may produce tool-call parts

- **WHEN** a caller iterates `stream_parts(messages, tools=[...])` and the model invokes a tool
- **THEN** the iterator yields at least one part with `type="tool-call"`
- **AND** that part includes `tool_call_id`, `tool_name`, and an `arguments` JSON string

#### Scenario: Callers still depend on the protocol

- **WHEN** the chat service needs streaming with tools
- **THEN** it obtains the provider via `get_llm()` and calls `stream_parts`
- **AND** it does not import a concrete provider SDK
