## 1. Shared types and schema

- [ ] 1.1 Add `app/schemas/chat.py` with `ChatMessage` (role: `system | user | assistant`, content: `str`)
- [ ] 1.2 Round-trip test for `ChatMessage` in `tests/test_chat_schema.py`

## 2. Provider configuration surface

- [ ] 2.1 Add `OLLAMA_CHAT_MODEL` (default `qwen3:4b-instruct`), `OPENAI_CHAT_MODEL` (default `gpt-4o-mini`), `ANTHROPIC_CHAT_MODEL` (default `claude-haiku-4-5`) fields to `app/core/config.py`
- [ ] 2.2 Mirror the new fields in `backend/.env.example` with their defaults and brief comments

## 3. Base interfaces and errors

- [ ] 3.1 Add `app/services/llm/base.py` with the `LLMProvider` and `Embedder` protocols
- [ ] 3.2 Define the typed error hierarchy: `LLMError`, `LLMConfigError`, `LLMTimeoutError`, `LLMInvalidResponse`, `LLMRateLimited`, `LLMInputTooLarge`
- [ ] 3.3 Add `LLMProviderBase` with the shared guardrail helpers (`_check_input`, `_apply_caps`, `_one_retry`, `_redact`)

## 4. Ollama adapter

- [ ] 4.1 Implement `app/services/llm/providers/ollama.py` with `OllamaProvider` (chat, structured chat via `format=<schema>`, streaming) and `OllamaEmbedder`
- [ ] 4.2 Honor `OLLAMA_BASE_URL` and `OLLAMA_API_KEY` — the latter is sent as a Bearer header for cloud usage
- [ ] 4.3 Validate the structured response against the requested Pydantic schema; retry once on `ValidationError`

## 5. OpenAI adapter

- [ ] 5.1 Implement `app/services/llm/providers/openai.py` with `OpenAIProvider` and `OpenAIEmbedder`
- [ ] 5.2 Use `response_format={"type": "json_schema", "json_schema": …, "strict": True}` for structured outputs
- [ ] 5.3 Map 429 to `LLMRateLimited`, network failures to `LLMTimeoutError`

## 6. Anthropic adapter

- [ ] 6.1 Implement `app/services/llm/providers/anthropic.py` with `AnthropicProvider` (chat, structured via tool use, streaming)
- [ ] 6.2 Do **not** implement an Anthropic embedder; the factory raises `LLMConfigError` if asked
- [ ] 6.3 Map Anthropic-specific errors into the typed hierarchy

## 7. Factory

- [ ] 7.1 Add `app/services/llm/factory.py` with `get_llm()` and `get_embedder()`, both `@lru_cache`-d
- [ ] 7.2 Parse `EMBEDDER` as `<provider>/<model>`; raise `LLMConfigError` on malformed values or unsupported providers
- [ ] 7.3 Re-export `get_llm`, `get_embedder`, `LLMProvider`, `Embedder`, `LLMError`, and concrete error classes from `app/services/llm/__init__.py`

## 8. Tests

- [ ] 8.1 `tests/test_llm_factory.py` — exhaustive test that each valid `LLM_PROVIDER` and each `EMBEDDER` pattern returns the right concrete class (no live LLM calls)
- [ ] 8.2 `tests/test_llm_contract.py` — assert that each adapter class implements the `LLMProvider` (or `Embedder`) protocol surface fully
- [ ] 8.3 `tests/test_llm_guardrails.py` — input exceeding `MAX_INPUT_CHARS` raises `LLMInputTooLarge` without a network call (patch the SDK client)
- [ ] 8.4 `tests/test_llm_key_redaction.py` — when a fake adapter raises an exception containing the API key, the resulting `LLMError` message and any logged line have the key redacted

## 9. Documentation

- [ ] 9.1 Update `backend/README.md` "Configuration reference" with the three new chat-model env vars
- [ ] 9.2 Add a short section to `backend/README.md` describing the provider abstraction, with a code snippet showing `get_llm().generate_structured(messages, Diagram)`

## 10. Verification

- [ ] 10.1 `ruff format` clean across `backend/`
- [ ] 10.2 `ruff check` clean across `backend/`
- [ ] 10.3 `pytest` clean across `backend/tests/`
- [ ] 10.4 `openspec validate add-llm-provider-abstraction --strict`
