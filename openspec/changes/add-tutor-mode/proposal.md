## Why

We now have all the ingredients for a real LLM call: the provider abstraction, structured outputs, the component-metadata library, the patterns library with similarity retrieval, and a rules engine. What's missing is the **glue** — the piece that takes a user request and a (possibly empty) diagram, and produces the message list the LLM actually sees.

Without this layer, every endpoint (`/generate`, `/analyze`, future reactive mode) would build its own prompt from scratch, in inconsistent ways, with inevitable drift on tone and structure. We want a single composer that any caller uses.

The mode also defines the **persona**. For MVP we ship one: `tutor` — patient, second-person, explains why before what. Future modes (`senior`, `brainstorm`) plug into the same machinery in their own proposals.

## What Changes

- Add a top-level `modes/` directory and a single seed mode `modes/tutor.md` with frontmatter + a curated system prompt.
- Add `backend/app/schemas/mode.py` with `Mode` Pydantic model.
- Add `backend/app/services/modes/` package with a loader mirroring `patterns/`: `load_modes()`, `get_mode(id)`, `reset_for_tests()`.
- Add `backend/app/services/prompts/composer.py` with `compose_prompt(user_request, diagram=None, mode_id="tutor", k_patterns=3)` returning `list[ChatMessage]`.
- Composition assembles:
  1. The mode's system prompt.
  2. A compact summary of every component type (always — gives the LLM the full vocabulary).
  3. Top-k patterns retrieved via similarity over the user request.
  4. If a diagram is provided, the rule findings from `check_all(diagram)`.
  5. The user message (request, plus serialized diagram when present).
- Add `modes/README.md` for contributors.
- Add tests covering the loader, the schema, and the composer (with mocked retrieval).

This proposal does **not** add any HTTP endpoint. `POST /generate` and `POST /analyze` consume `compose_prompt` in their own proposals.

## Capabilities

### New Capabilities

- `tutor-mode`: The pedagogical persona that the LLM adopts in MVP. Defined by `modes/tutor.md` (system prompt + frontmatter metadata) and exposed through `get_mode("tutor")`.
- `prompt-composition`: A single function that builds the `list[ChatMessage]` for an LLM call by composing the active mode's system prompt, component summaries, retrieved patterns, optional rule findings, and the user request.

### Modified Capabilities

<!-- None. -->

## Impact

- **Code**: new `modes/` directory at the repo root; new `app/schemas/mode.py`; new `app/services/modes/` and `app/services/prompts/` packages; new tests.
- **Dependencies**: none new. Reuses `python-frontmatter`, the patterns loader, the rules engine, the retrieval layer, and the LLM provider abstraction.
- **Configuration**: no new env vars.
- **Documentation**: `modes/README.md` (new); short section in `backend/README.md`.
- **Future proposals unblocked**: `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint`, `add-ai-explanation-panel`. All three consume `compose_prompt`.
- **OSS contribution surface**: contributors can iterate on the system prompt with a markdown PR, no Python required. Future modes (senior, brainstorm) follow the same pattern.
