## ADDED Requirements

### Requirement: Public composer function

The backend SHALL expose `compose_prompt(user_request: str, diagram: Diagram | None = None, mode_id: str = "tutor", k_patterns: int = 3) -> list[ChatMessage]`. Every backend caller that talks to an LLM SHALL use this function (or a thin wrapper over it).

#### Scenario: Without a diagram

- **WHEN** `compose_prompt("I want to build a delivery app")` is called
- **THEN** the return value is a list of exactly two `ChatMessage`s
- **AND** the first has `role="system"` with the assembled context
- **AND** the second has `role="user"` and its content includes the original user_request

#### Scenario: With a diagram

- **WHEN** `compose_prompt("review my design", diagram=some_diagram)` is called
- **THEN** the return value is a list of exactly two `ChatMessage`s
- **AND** the user message includes both the request and a serialization of the diagram
- **AND** the system message includes a section with rule findings (which may be empty)

### Requirement: Mode persona is the first section of the system message

The composer SHALL place the mode's `system_prompt` at the start of the system message, before any injected vocabulary, patterns, or findings.

#### Scenario: Tutor persona appears first

- **WHEN** the composer runs with `mode_id="tutor"`
- **THEN** the system message starts with the body of `modes/tutor.md`
- **AND** subsequent sections come after, separated by `---` lines

### Requirement: Component vocabulary always injected

The composer SHALL include a compact summary of every component type from `app.services.components.load_components()` in the system message, regardless of whether a diagram is supplied.

#### Scenario: All 8 component labels present

- **WHEN** `compose_prompt(...)` is called
- **THEN** the system message references every component-type value of the `NodeType` enum at least once

### Requirement: Retrieved patterns appended

The composer SHALL call `retrieve_patterns(user_request, k=k_patterns)` and include the returned patterns in the system message under a `# Relevant patterns` (or equivalent) section.

#### Scenario: Retrieved patterns appear in the system message

- **WHEN** retrieval returns 3 PatternMatches with ids A, B, C
- **THEN** the system message includes those three pattern titles, in the order returned

#### Scenario: Empty retrieval result is tolerated

- **WHEN** `retrieve_patterns(...)` returns an empty list
- **THEN** `compose_prompt(...)` still returns a valid two-message list
- **AND** the system message does not crash; it may omit the patterns section or include a placeholder

### Requirement: Rule findings included when a diagram is supplied

The composer SHALL run `check_all(diagram)` when `diagram is not None` and include the findings in the system message as a structured prose block.

#### Scenario: Findings present when violations exist

- **WHEN** a diagram with a `frontend → database` edge is supplied
- **THEN** the system message contains a block with the `no-direct-frontend-to-database` finding

#### Scenario: Findings section omitted or empty for clean diagrams

- **WHEN** a clean diagram is supplied
- **THEN** the system message either omits the findings section or marks it as "no findings"

### Requirement: Unknown mode raises

The composer SHALL raise `ModeNotFoundError` when called with a `mode_id` that has no corresponding file in `modes/`.

#### Scenario: Bad mode_id surfaces a clear error

- **WHEN** `compose_prompt("hello", mode_id="not-a-mode")` is called
- **THEN** the function raises `ModeNotFoundError`

### Requirement: Graceful sub-system failures

The composer SHALL NOT raise when retrieval, the rules engine, or the component loader raises an unexpected error. Instead, it SHALL log a warning and continue with the remaining sections.

#### Scenario: Retrieval failure does not break the call

- **WHEN** `retrieve_patterns` raises during composition
- **THEN** the composer logs a warning and returns a valid two-message list (without the patterns section)
