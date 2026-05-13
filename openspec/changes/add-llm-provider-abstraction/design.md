## Context

Three providers, four operations (chat, structured chat, streaming, embedding), and zero tolerance for malformed `Diagram` JSON downstream. Each provider implements the same operations but with different SDK conventions and different mechanisms for forcing structured outputs:

| Provider  | Chat                              | Structured                                                | Streaming                            | Embeddings                         |
| --------- | --------------------------------- | --------------------------------------------------------- | ------------------------------------ | ---------------------------------- |
| Ollama    | `ollama.chat()` async             | `format=<json_schema>` (1.x+) + Pydantic validation       | `stream=True` async generator        | `ollama.embed()` async             |
| OpenAI    | `client.chat.completions.create`  | `response_format={"type":"json_schema", "json_schema":…}` | `stream=True`                        | `client.embeddings.create`         |
| Anthropic | `client.messages.create`          | Tool use: schema as a single tool, force `tool_choice`    | `stream=True`                        | (no first-party embedding API yet) |

The abstraction's job is to make all of this look the same to callers, and to enforce the guardrails the rest of the system relies on.

## Goals / Non-Goals

**Goals:**

- One Python protocol (`LLMProvider`) that callers depend on. Three concrete adapters that implement it. A factory that returns the right one based on `Settings`.
- Structured outputs are physically impossible to break: every adapter's `generate_structured()` returns an instance of the requested Pydantic model or raises.
- Operational guardrails (input cap, output cap, retry, key non-leakage) live in the base class, not in every adapter.
- Embeddings have their own protocol (`Embedder`) and own factory entry point. The `EMBEDDER` setting (`<provider>/<model>`) can route to a different provider than chat — common case: local Ollama embeddings + cloud chat.

**Non-Goals:**

- HTTP endpoints. `POST /generate` and `POST /analyze` live in other proposals; they will be the first callers of this abstraction.
- Prompt composition / RAG / mode selection. Callers pass already-composed `messages` lists; this layer does not look inside the prose.
- Caching of responses. Prompt caching with Anthropic/OpenAI is a Phase 2 optimization once we have traffic to optimize.
- Multi-provider orchestration ("ask three models, pick the best"). Phase 3.
- Real-time provider health checks. Validation is lazy: first call fails with a clear error if a credential is missing or wrong.
- Anthropic embeddings — they do not yet ship a first-party embedding API, so Anthropic implements `LLMProvider` only. The `Embedder` protocol is fulfilled by Ollama or OpenAI.

## Decisions

### Async-only

All methods are `async`. FastAPI is async-native; LLM calls are I/O-bound; streaming requires async generators. A sync surface would just be `asyncio.run` boilerplate everywhere.

**Alternatives considered:** dual sync/async API (rejected — twice the surface to test, twice the bugs).

### Two protocols, not one mega-interface

`LLMProvider` and `Embedder` are separate. Anthropic implements only the former; Ollama and OpenAI implement both. Splitting them lets us route the two concerns independently via `LLM_PROVIDER` and `EMBEDDER`.

**Alternatives considered:** one `Provider` interface with optional methods (rejected — type signature lies about what each provider actually does). 

### Structured-output strategy is per-adapter

- **Ollama**: pass the Pydantic schema via `format=<json_schema>` (supported in current Ollama versions). Validate the response with the same schema on receipt. On `ValidationError`, retry once with a stricter system message ("you must return JSON matching this schema"). Fail after that.
- **OpenAI**: `response_format={"type": "json_schema", "json_schema": {"name": cls.__name__, "schema": cls.model_json_schema(), "strict": True}}`. OpenAI guarantees a syntactically valid JSON that matches the schema. We still validate with Pydantic for our own type safety.
- **Anthropic**: define a single tool whose `input_schema` is the Pydantic schema; set `tool_choice={"type": "tool", "name": tool_name}`. Anthropic forces the model to call that tool, with arguments matching the schema. We extract and validate.

These mechanisms are not interchangeable, but the protocol method signature is the same. Callers do not see the differences.

**Alternatives considered:** universal "instruction-only" approach where we just ask in the prompt and validate after (rejected — too unreliable for our use case; we use structured outputs to make malformed responses *impossible*, not "unlikely").

### No streaming for `generate_structured`

Streaming a structured output is awkward — JSON is not parseable mid-stream without specialized partial parsers, and we do not want to ship one. `generate_structured` returns the full validated object. `stream` is for prose.

**Alternatives considered:** stream structured outputs and parse partials (rejected — adds a partial-JSON parser dependency, defers `ValidationError` to mid-render, complicates the UX for marginal gain).

### Provider model is configured separately from provider

The provider (Ollama / OpenAI / Anthropic) is set globally via `LLM_PROVIDER`. The model used for chat is configurable separately via three env vars added on this proposal:

- `OLLAMA_CHAT_MODEL` (default: `qwen3:4b-instruct` — small, runs comfortably on consumer hardware; user can override)
- `OPENAI_CHAT_MODEL` (default: `gpt-4o-mini`)
- `ANTHROPIC_CHAT_MODEL` (default: `claude-haiku-4-5`)

Each adapter reads its own. Cross-provider model name normalization is not attempted — model names are intrinsically vendor-specific.

**Alternatives considered:** single `LLM_MODEL` setting (rejected — switching providers would silently apply a meaningless model name; explicit per-provider model is safer).

### Guardrails enforced in the base class

`LLMProviderBase` (the parent class for the three adapters) implements:

- A `_check_input` method that rejects messages exceeding `MAX_INPUT_CHARS` total.
- A `_apply_caps` method that clamps `max_tokens` to `MAX_OUTPUT_TOKENS`.
- A `_one_retry` async helper that retries on `httpx.HTTPStatusError` 5xx and on `ValidationError` (for `generate_structured`).
- A `_redact` method that ensures API keys never appear in raised exceptions.

Adapters inherit and call these. Callers do not have to remember to enforce caps.

**Alternatives considered:** middleware-style decorators per call site (rejected — easy to forget on a new call site, defeating the purpose).

### Factory returns a cached singleton per provider

`get_llm()` and `get_embedder()` are `@lru_cache`-d. The factory builds the adapter once (loading keys and base URLs from `Settings`) and reuses it. Reconnection on transient error is the adapter's responsibility.

**Alternatives considered:** new client per request (rejected — wasteful, and `httpx` clients are designed to be long-lived for connection pooling).

### Error model

Adapter errors normalize to a small set of typed exceptions:

```
class LLMError(Exception):           # base
class LLMConfigError(LLMError):      # missing key, bad base URL
class LLMTimeoutError(LLMError):     # exceeded provider timeout
class LLMInvalidResponse(LLMError):  # malformed JSON after retry
class LLMRateLimited(LLMError):      # 429
```

Routers catch `LLMError` and translate to HTTP 5xx/429 with a stable shape. The provider's raw exception is logged (without keys) for debugging.

## Risks / Trade-offs

- **Risk**: provider SDK breaking changes (Anthropic and OpenAI iterate quickly) → **Mitigation**: pin lower bounds in `pyproject.toml`, run contract tests on each adapter that catch missing methods; treat SDK upgrades as deliberate PRs.
- **Risk**: Ollama Cloud auth shape may evolve (early-stage product) → **Mitigation**: keep the `OLLAMA_API_KEY` path well-isolated; only the Ollama adapter cares about it.
- **Risk**: `nomic-embed-text-v2-moe` embeddings have a different dimension than v1 (likely 768 vs the existing 768; needs verification) → **Mitigation**: the patterns vector store is rebuilt on every `tangram seed`; dimension mismatches surface immediately with a clean error, not data corruption. We document this in `add-patterns-library-and-rag`.
- **Risk**: structured output retry loop hides intermittent provider misbehavior → **Mitigation**: every retry is logged with `level=warning`; if retries become routine we will surface them as a metric and tune.
- **Trade-off**: three adapters from day one is more code than "one adapter, add the others later." We accept this because the proposal-level interface only stabilizes once all three have informed it — late-bound adapters tend to find ugly corners in the interface.

## Migration Plan

No migration. This is a new package. Rollback = revert the PR.

## Open Questions

- **Should `generate` and `generate_structured` accept a `tools` parameter for future tool use?** Probably yes in Phase 2 once the reactive mode wants the model to "call" anti-pattern rules as tools. Out of scope here.
- **Embeddings: should we cache (text → vector) to avoid re-embedding identical strings?** Useful when `tangram seed` re-runs incrementally. Defer until we have evidence of repeated calls.
- **Should the factory accept overrides for tests?** Currently `lru_cache`-d. Tests will use `cache_clear()` between cases. If this gets noisy, we add a `reset_for_tests()` helper.
