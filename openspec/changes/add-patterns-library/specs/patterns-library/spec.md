## ADDED Requirements

### Requirement: Pattern files use frontmatter + markdown

Each pattern file under `patterns/` SHALL be a markdown file with a YAML frontmatter block at the top and a markdown body. The frontmatter SHALL declare `id` (string), `title` (string), `complexity` (one of `beginner`, `intermediate`, `advanced`), `tags` (list of strings, may be empty), and `component_types` (list of values from the `NodeType` enum).

#### Scenario: A well-formed pattern parses cleanly

- **WHEN** the loader reads a `patterns/<id>.md` whose frontmatter declares the required fields and whose body has the required sections
- **THEN** the parse succeeds and produces a `Pattern` instance

#### Scenario: Filename stem must equal the declared id

- **WHEN** a pattern file at `patterns/crud-application.md` declares `id: something-else` in its frontmatter
- **THEN** the loader raises with a clear error pointing at the mismatch

#### Scenario: Unknown component type is rejected

- **WHEN** a pattern lists `component_types: [database, datbase]` (typo) in its frontmatter
- **THEN** the loader raises a validation error before returning

### Requirement: Required body sections

Every pattern body SHALL contain at least the following second-level headers (`##`), each at least once, case-insensitive on the header text: `What it is`, `When to use`, `When to avoid`, `Components involved`, `Common pitfalls`.

#### Scenario: Missing section fails the loader

- **WHEN** a pattern body omits one of the required headers
- **THEN** the loader raises an error naming the missing section and the file path

#### Scenario: Additional headers are allowed

- **WHEN** a pattern body contains the required headers plus additional ones (e.g. `## Variants`, `## Real-world examples`)
- **THEN** the loader accepts the file

### Requirement: Loader API

The backend SHALL expose `load_patterns()` returning `dict[str, Pattern]` keyed by pattern id, `get_pattern(pattern_id)` returning a single `Pattern`, and `reset_for_tests()` clearing the cache.

#### Scenario: load_patterns caches between calls

- **WHEN** `load_patterns()` is called twice in the same process
- **THEN** the two return values are the same object

#### Scenario: get_pattern returns the requested pattern

- **WHEN** `get_pattern("crud-application")` is called and `patterns/crud-application.md` is present
- **THEN** the return value is a `Pattern` whose `id` field equals `crud-application`

#### Scenario: get_pattern raises on unknown id

- **WHEN** `get_pattern("nonexistent")` is called
- **THEN** a `PatternNotFoundError` (subclass of `KeyError`) is raised

#### Scenario: reset_for_tests clears the cache

- **WHEN** a test calls `reset_for_tests()` after a `load_patterns()` call
- **THEN** the next `load_patterns()` call returns a freshly built dict (not the previously cached one)

### Requirement: Seed patterns ship with the repository

The repository SHALL include the following pattern files in `patterns/` on initial release: `crud-application.md`, `jamstack.md`, `background-worker.md`, `realtime-chat.md`, `event-driven.md`.

#### Scenario: All seed patterns load cleanly

- **WHEN** `load_patterns()` is called on a freshly cloned repo
- **THEN** the returned dict contains five entries with the ids `crud-application`, `jamstack`, `background-worker`, `realtime-chat`, `event-driven`
- **AND** every entry has a non-empty body

### Requirement: Documentation surface

The repository SHALL include `patterns/README.md` documenting the frontmatter schema, the required body sections, tone guidance, and the workflow for adding a new pattern.

#### Scenario: A contributor follows the README to add a pattern

- **WHEN** a new contributor reads `patterns/README.md` and follows the documented steps
- **THEN** they can add a new pattern without reading Python source
- **AND** the documented steps include running the loader / tests to verify the new file
