## 1. Schemas

- [x] 1.1 Add `app/schemas/generate.py` with `GenerateRequest` (prompt: str, length-bounded) and `GeneratedDiagramContent` (name, description, nodes, edges — no id/timestamps/positions)
- [x] 1.2 Round-trip tests `tests/test_generate_schema.py`

## 2. Auto-layout

- [x] 2.1 Add `app/services/generation/layout.py` with `auto_layout(nodes_without_positions) -> list[Node]` (assigns Position by node type, stacks vertically within column)
- [x] 2.2 Tests `tests/test_layout.py` — deterministic, frontend left, database right, multi-node stacking

## 3. Generator service

- [x] 3.1 Add `app/services/generation/__init__.py` and `app/services/generation/generator.py`
- [x] 3.2 Implement `generate_diagram(prompt: str) -> Diagram` — composes prompt, calls `generate_structured(GeneratedDiagramContent)`, validates edge integrity, assigns positions, wraps in full Diagram with ULID + timestamps
- [x] 3.3 Add `python-ulid` to runtime deps (lightweight, pure Python)
- [x] 3.4 Validate edges reference existing node ids; raise `LLMInvalidResponse` on inconsistency
- [x] 3.5 Tests `tests/test_generator.py` with FakeLLMProvider

## 4. HTTP router

- [x] 4.1 Add `app/routers/ai.py` with `POST /generate`
- [x] 4.2 Map every `LLMError` subclass to its HTTP status with a `code` field in the body
- [x] 4.3 Validate prompt length at the Pydantic layer (422 + 413)
- [x] 4.4 Wire router in `app/main.py`
- [x] 4.5 Tests `tests/test_route_generate.py` using FastAPI TestClient + dependency override

## 5. Documentation

- [x] 5.1 Add "Generation endpoint" section to `backend/README.md` with a curl example and the local-Ollama vs Ollama-Cloud setup notes
- [x] 5.2 Add a comment on which OLLAMA model and OPENAI/ANTHROPIC chat models we recommend for first-time testing

## 6. Verification

- [x] 6.1 `ruff format --check` clean
- [x] 6.2 `ruff check` clean
- [x] 6.3 `pytest` clean (112 prior + 26 new = 138 total, all passing)
- [x] 6.4 `openspec validate add-diagram-generation-endpoint --strict`
