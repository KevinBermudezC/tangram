## Why

Tangram needs to talk to LLMs to do its actual job (generate diagrams, analyze them, explain components, embed patterns). We have three constraints:

1. **Provider-agnostic** — users must be able to choose Ollama (local or cloud), OpenAI, or Anthropic without code changes. BYOK or zero cost.
2. **Structured outputs** — `/generate` must return a validated `Diagram`, never a malformed blob. The guardrail layer in [ADR-0001](../../../docs/architecture/0001-guardrails-strategy.md) depends on this being a *hard* guarantee at the provider layer.
3. **Single seam** — all of `routers/`, future RAG retrieval, future reactive mode go through the same interface. Adding a fourth provider should not require touching any caller.

Without this abstraction, every route would reinvent provider plumbing, structured-output enforcement, and error handling. We want it built once, correctly, here.

## What Changes

- Add `backend/app/services/llm/base.py` with two protocols: `LLMProvider` (chat, structured chat, streaming) and `Embedder` (text → vectors).
- Add `backend/app/services/llm/factory.py` exposing `get_llm()` and `get_embedder()`, picking the implementation from `Settings`.
- Add three adapters under `backend/app/services/llm/providers/`:
  - `ollama.py` — talks to local Ollama (`OLLAMA_BASE_URL`) or Ollama Cloud (same URL, with `OLLAMA_API_KEY`).
  - `openai.py` — uses `response_format` with JSON Schema for structured outputs.
  - `anthropic.py` — forces structured outputs via tool use.
- Add a shared `ChatMessage` model (`role: system | user | assistant`, `content: str`) under `backend/app/schemas/chat.py`. Distinct from `schemas.diagram.Message` (which is the conversation history embedded in a diagram).
- Enforce operational guardrails at the provider layer:
  - Input length capped at `MAX_INPUT_CHARS` before any provider call.
  - Output capped at `MAX_OUTPUT_TOKENS` via each provider's native `max_tokens`.
  - One retry on transient errors; clean error to caller otherwise.
- API keys never logged. The factory loads them from `Settings` once at construction; they do not appear in any log line, exception message, or error response.
- Tests under `backend/tests/`:
  - `test_llm_factory.py` — factory wires the right adapter for each `LLM_PROVIDER` value.
  - `test_llm_contract.py` — every adapter implements the protocol's full surface (no missing methods).
  - `test_chat_schema.py` — `ChatMessage` round-trips.

This proposal does **not** add any HTTP endpoint that calls the LLM. Routes that use the providers (`POST /generate`, `POST /analyze`) ship in their own proposals.

## Capabilities

### New Capabilities

- `llm-providers`: A single interface (`LLMProvider`, `Embedder`) implemented by Ollama, OpenAI, and Anthropic adapters. Defines the contract for chat completion, structured chat, streaming, and embeddings. Encodes operational guardrails (input/output caps, no-leak key handling, retry policy). Every future caller in the backend depends on this interface, not on any concrete provider SDK.

### Modified Capabilities

<!-- None. The diagram schema (docs/schema/diagram-v0.md) is the only previously
     accepted contract; this change does not modify it. -->

## Impact

- **Code**: new `backend/app/services/llm/` package; new `backend/app/schemas/chat.py`; new tests.
- **Dependencies**: no new packages — `ollama`, `openai`, `anthropic`, `httpx` are already declared in `pyproject.toml` from the foundations proposal.
- **Configuration**: no new env vars. `LLM_PROVIDER`, `OLLAMA_BASE_URL`, `OLLAMA_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `EMBEDDER`, `MAX_INPUT_CHARS`, `MAX_OUTPUT_TOKENS` all already exist on `Settings`.
- **Future proposals unblocked**: `add-diagram-generation-endpoint`, `add-diagram-analysis-endpoint`, `add-patterns-library-and-rag`, `add-ai-explanation-panel`, and the reactive AI mode in Phase 2.
- **Risk**: misconfigured adapter (wrong key, wrong base URL) is a failure mode users *will* hit. We address it by validating credentials lazily on first call with a clear error, not at boot.
