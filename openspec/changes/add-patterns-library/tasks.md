## 1. Schema

- [x] 1.1 Add `app/schemas/pattern.py` with `PatternComplexity` (StrEnum) and `Pattern` (Pydantic: id, title, complexity, tags, component_types, body)
- [x] 1.2 Validate `component_types` entries against the `NodeType` enum
- [x] 1.3 Round-trip test for `Pattern` in `tests/test_pattern_schema.py`

## 2. Loader

- [x] 2.1 Add `app/services/patterns/__init__.py` and `app/services/patterns/loader.py`
- [x] 2.2 Implement `load_patterns()` that walks `patterns/`, parses frontmatter with `python-frontmatter`, validates against `Pattern`, returns `dict[str, Pattern]`
- [x] 2.3 Decorate with `@lru_cache`
- [x] 2.4 Implement `get_pattern(pattern_id: str) -> Pattern`
- [x] 2.5 Implement `PatternNotFoundError` (KeyError subclass)
- [x] 2.6 Implement `reset_for_tests()` that clears the cache
- [x] 2.7 Implement body-section validation: enforce presence of `What it is`, `When to use`, `When to avoid`, `Components involved`, `Common pitfalls`

## 3. Seed pattern files (one markdown per pattern at repo root under `patterns/`)

- [x] 3.1 `patterns/crud-application.md`
- [x] 3.2 `patterns/jamstack.md`
- [x] 3.3 `patterns/background-worker.md`
- [x] 3.4 `patterns/realtime-chat.md`
- [x] 3.5 `patterns/event-driven.md`

## 4. Dependency

- [x] 4.1 Add `python-frontmatter>=1.0` to `[project.dependencies]` in `backend/pyproject.toml`

## 5. Tests

- [x] 5.1 `tests/test_pattern_schema.py` — `Pattern` round-trips through JSON
- [x] 5.2 `tests/test_pattern_files.py` — every file under `patterns/` validates against the schema, has the required sections, filename matches id
- [x] 5.3 `tests/test_pattern_loader.py` — cache hits, `reset_for_tests` clears, `get_pattern` returns + raises correctly

## 6. Documentation

- [x] 6.1 Add `patterns/README.md` — frontmatter schema, required sections, tone, contribution workflow
- [x] 6.2 Add a "Patterns library" section to `backend/README.md` pointing at the patterns folder and the loader API

## 7. Verification

- [x] 7.1 `ruff format --check` clean
- [x] 7.2 `ruff check` clean
- [x] 7.3 `pytest` clean (67 prior + 16 new = 83 total, all passing)
- [x] 7.4 `openspec validate add-patterns-library --strict`
