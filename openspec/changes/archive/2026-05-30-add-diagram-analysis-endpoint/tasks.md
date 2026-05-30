## 1. Schemas

- [x] 1.1 Add `app/schemas/analyze.py` with `AnalyzeRequest` (`diagram: Diagram`, `mode_id: str = "tutor"`) and `AnalyzeResponse` (`findings: list[Finding]`, `feedback: str`)
- [x] 1.2 Round-trip tests `tests/test_analyze_schema.py`

## 2. Analyzer service

- [x] 2.1 Add `app/services/analysis/__init__.py` (re-export `analyze_diagram`) and `app/services/analysis/analyzer.py`
- [x] 2.2 Implement `analyze_diagram(diagram: Diagram, mode_id: str = "tutor") -> AnalyzeResponse` — run `check_all(diagram)` for findings, `compose_prompt(<fixed review instruction>, diagram=diagram, mode_id=mode_id)`, call `LLMProvider.generate(messages)` for prose feedback, return both
- [x] 2.3 Use the plain-text `generate` method (not `generate_structured`) — feedback is human-readable prose
- [x] 2.4 Tests `tests/test_analyzer.py` with FakeLLMProvider — findings come from `check_all`, feedback from the LLM, findings identical across two different mocked responses

## 3. HTTP router

- [x] 3.1 Factor the `LLMError` → HTTP status mapping out of `post_generate` into a shared helper (e.g. `_raise_for_llm_error`) in `app/routers/ai.py`; update `/generate` to use it (no behaviour change)
- [x] 3.2 Add `POST /analyze` to `app/routers/ai.py` returning `AnalyzeResponse`
- [x] 3.3 Guard serialized diagram size against `MAX_INPUT_CHARS` before composing; return 413 `code: diagram_too_large`
- [x] 3.4 Map `ModeNotFoundError` to 422 `code: unknown_mode`
- [x] 3.5 Reuse the shared `LLMError` mapping (413/429/500/502/503/504 with stable `code`s)
- [x] 3.6 Declare `responses={...}` on the route so the OpenAPI doc lists every error shape (mirrors `/generate`)

## 4. Tests

- [x] 4.1 `tests/test_route_analyze.py` via TestClient + dependency override: happy path (findings + feedback), clean diagram (empty findings, non-empty feedback), violating diagram (matching `rule_id`)
- [x] 4.2 Oversized diagram → 413 `diagram_too_large`, no LLM call
- [x] 4.3 Malformed body → 422; unknown `mode_id` → 422 `unknown_mode`
- [x] 4.4 Each `LLMError` subclass → correct status + `code` (shared with `/generate`, assert no regression on `/generate`)
- [x] 4.5 Read-only: assert no storage write occurs during analysis

## 5. Documentation

- [x] 5.1 Add "Analysis endpoint" section to `backend/README.md` with a curl example (diagram in, findings + feedback out)

## 6. Verification

- [x] 6.1 `ruff format --check` clean
- [x] 6.2 `ruff check` clean
- [x] 6.3 `pytest` clean (165 prior + 25 new = 190 total, all passing)
- [x] 6.4 `openspec validate add-diagram-analysis-endpoint --strict`
