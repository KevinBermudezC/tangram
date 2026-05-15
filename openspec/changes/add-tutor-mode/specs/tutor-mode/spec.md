## ADDED Requirements

### Requirement: Tutor mode file ships with the repo

The repository SHALL include `modes/tutor.md` with YAML frontmatter (`id`, `title`, `summary`) and a non-empty markdown body containing the system prompt the LLM will use under the tutor persona.

#### Scenario: Tutor mode loads from a fresh clone

- **WHEN** `get_mode("tutor")` is called on a freshly cloned repo
- **THEN** it returns a `Mode` instance whose `id` is `"tutor"`
- **AND** the `system_prompt` field is a non-empty string

### Requirement: Mode schema

The backend SHALL expose a `Mode` Pydantic model with fields `id` (kebab-case string), `title` (non-empty string), `summary` (non-empty string), `system_prompt` (non-empty string, parsed from the markdown body).

#### Scenario: Mode round-trips through JSON

- **WHEN** a `Mode` instance is dumped with `model_dump_json()` and re-parsed with `model_validate_json(...)`
- **THEN** the result equals the original

#### Scenario: Empty system_prompt is rejected

- **WHEN** a mode file has a blank body after the frontmatter
- **THEN** the loader raises with a clear error

### Requirement: Mode loader API

The backend SHALL expose `load_modes()` returning `dict[str, Mode]` keyed by mode id, `get_mode(mode_id)` returning a single Mode (raising `ModeNotFoundError` on unknown id), and `reset_for_tests()` clearing the cache.

#### Scenario: load_modes caches between calls

- **WHEN** `load_modes()` is called twice in the same process
- **THEN** the two return values are the same object

#### Scenario: get_mode unknown id raises

- **WHEN** `get_mode("does-not-exist")` is called
- **THEN** a `ModeNotFoundError` (subclass of `KeyError`) is raised

### Requirement: Filename equals id

Each mode file's stem SHALL equal the `id` declared in its frontmatter. Mismatch SHALL be a loader error.

#### Scenario: Mismatch fails the loader

- **WHEN** `modes/tutor.md` declares `id: senior` in its frontmatter
- **THEN** the loader raises with a clear error naming the file and the mismatch
