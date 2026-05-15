## 1. Mode schema and loader

- [x] 1.1 Add `app/schemas/mode.py` with `Mode` (id, title, summary, system_prompt) and non-empty validators
- [x] 1.2 Round-trip test `tests/test_mode_schema.py`
- [x] 1.3 Add `app/services/modes/__init__.py` and `app/services/modes/loader.py` with `load_modes()`, `get_mode()`, `reset_for_tests()`, `ModeNotFoundError`
- [x] 1.4 Enforce filename-equals-id and required-body invariants
- [x] 1.5 Tests `tests/test_mode_loader.py`

## 2. Tutor mode content

- [x] 2.1 Add `modes/tutor.md` with frontmatter + curated system prompt body
- [x] 2.2 Add `modes/README.md` describing the format and tone guidance

## 3. Prompt composer

- [x] 3.1 Add `app/services/prompts/__init__.py` and `app/services/prompts/composer.py`
- [x] 3.2 Implement `compose_prompt(user_request, diagram=None, mode_id="tutor", k_patterns=3)`
- [x] 3.3 Private helpers: `_component_vocabulary_block_safe()`, `_patterns_block_safe()`, `_findings_block_safe()`
- [x] 3.4 Wrap retrieval / rules / components calls in try/except with warning logs

## 4. Tests

- [x] 4.1 `tests/test_prompt_composer.py` — without diagram returns 2 messages with expected sections
- [x] 4.2 With diagram includes user-message diagram + system findings section
- [x] 4.3 Empty retrieval is tolerated
- [x] 4.4 Unknown mode raises `ModeNotFoundError`
- [x] 4.5 Retrieval failure does not break the call (graceful degradation)

## 5. Documentation

- [x] 5.1 Add `modes/README.md`
- [x] 5.2 Add a "Modes and prompt composition" section to `backend/README.md`

## 6. Verification

- [x] 6.1 `ruff format --check` clean
- [x] 6.2 `ruff check` clean
- [x] 6.3 `pytest` clean (96 prior + 16 new = 112 total, all passing)
- [x] 6.4 `openspec validate add-tutor-mode --strict`
