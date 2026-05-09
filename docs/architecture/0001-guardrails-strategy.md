# ADR-0001 — Guardrails strategy

**Status:** Accepted (MVP scope) · Revisit at Phase 2

**Date:** 2026-05-09

**Decision-makers:** Tangram core team

---

## Context

Tangram is an LLM-driven copilot that helps junior developers design software architectures. The model receives a free-text request from the user (e.g. *"I want to build a delivery app"*) and returns either (a) a structured `Diagram` JSON, or (b) prose feedback about an existing diagram.

Two failure modes worry us:

1. **Format failures** — the model returns malformed JSON, missing required fields, or invented enum values. This breaks the editor.
2. **Behavioral failures** — the model goes off-topic ("write me a poem"), hallucinates technologies that don't exist, lectures instead of teaching, or responds to jailbreak attempts.

We need a guardrails strategy that addresses both, balanced against three constraints:

- **Cost / latency:** users running BYOK pay per token; users running Ollama on modest hardware feel each extra call.
- **Self-host friction:** every dependency we add is one more thing a contributor or self-hoster has to install and configure.
- **Maturity:** we are pre-alpha. Over-engineering guardrails before we have real misuse data is a waste.

## Decision

We adopt a **layered, minimum-viable guardrails stack for MVP**, deferring heavier tooling (e.g. NVIDIA NeMo Guardrails) to Phase 2 once we have evals and real usage signals.

### MVP layer 1 — Format guardrails (HARD)

- All LLM calls that produce a `Diagram` use **structured outputs** (`response_format` with the JSON Schema derived from `Diagram.model_json_schema()`).
- All responses are re-validated with Pydantic on receipt. A `ValidationError` triggers one retry, then a clean error to the frontend.
- Provider adapters are responsible for translating "structured output" semantics across OpenAI / Anthropic / Ollama. Where a provider lacks native structured outputs (older Ollama models), we fall back to JSON mode + Pydantic validation + retry.

### MVP layer 2 — Behavioral guardrails via system prompt (SOFT)

A single, versioned `system_prompt.md` lives in `backend/app/services/llm/prompts/`. It enforces:

- **Role:** "You are Tangram, a system-design copilot for junior developers."
- **Tone:** explain the *why* before the *what*; ask before assuming.
- **Scope:** redirect off-topic requests politely.
- **Anti-hallucination:** if uncertain about a technology or trade-off, say so explicitly. Never invent product names.
- **Output discipline:** for diagram-generation calls, return only valid `Diagram` JSON; for chat calls, return prose.

The system prompt is treated as code: changes go through PR review with rationale.

### MVP layer 3 — Operational guardrails (HARD)

- `max_tokens` cap on every call.
- Input length limit (configurable; default 4 000 chars on the user message).
- Provider keys (when BYOK) are never sent to the frontend; all LLM traffic is server-side.
- Basic rate limiting on the public endpoints (`POST /generate`, `POST /analyze`) — even though Tangram is self-hosted, anyone deploying it publicly should not get nuked by a curl loop.

### Phase 2 — Re-evaluate NeMo Guardrails

We will evaluate **NVIDIA NeMo Guardrails** when *all* of the following are true:

1. The reactive AI mode (suggestions while editing, à la Cursor) ships, expanding the surface area of free-form conversation.
2. The patterns library + RAG (over our bundled, curated corpus — see ADR-0005) is online — at that point hallucinations become measurable and actionable.
3. We have an evals suite: without it, adding guardrails is unverifiable.
4. We see real misuse in the wild (jailbreak attempts, off-topic abuse) that the system-prompt layer is not catching.

If/when we adopt NeMo, the candidate features are:

- **Topic rails** via Colang flows (hard guarantee that off-topic queries don't reach the diagram-generation pipeline).
- **Hallucination rails** that fact-check generated rationale against the RAG corpus.
- **Jailbreak detection** on the input layer.

NeMo is multi-provider and open source, which aligns with our philosophy.

## Consequences

### Positive

- MVP stays cheap, fast, and self-hostable with no extra services.
- The structured-outputs + Pydantic combination gives us a *physical* guarantee of valid `Diagram` shapes — the largest UX risk is eliminated by construction, not by hope.
- Postponing NeMo avoids spending design budget on hypothetical risks.
- The system prompt is a single editable file — easy for contributors to iterate on.

### Negative

- The system-prompt layer is **soft** — adversarial users can bypass tone/scope rules. We accept this for MVP because (a) blast radius is low and (b) self-hosted means there is no shared multitenant attack surface.
- Without evals, we cannot quantitatively measure quality regressions when we change the prompt. We accept this for MVP and prioritize evals early in Phase 2.
- If reactive mode lands before NeMo evaluation, we'll have a brief window of less-defended free-form chat. The mitigation: ship reactive mode behind a feature flag (`TANGRAM_REACTIVE=1`) until guardrails catch up.

## Alternatives considered

### A. NeMo Guardrails from MVP

**Rejected** because:

- Adds an extra inference per request (latency + tokens).
- Colang DSL is a learning curve we don't want to impose on early contributors.
- Solves problems we don't yet have evidence of (off-topic abuse, jailbreaks at scale).
- Hallucination rails are weak without a RAG corpus to fact-check against — Phase 2 prerequisite.

### B. Guardrails-as-a-service (e.g. Lakera, Protect AI)

**Rejected** because:

- External SaaS dependency conflicts with our self-hosted, BYOK ethos.
- Adds an account/setup step for every self-hoster.
- Vendor lock-in we don't want this early.

### C. Roll our own regex/keyword-based guardrails

**Rejected** because:

- Brittle and easy to bypass.
- We get most of the value from Pydantic schema enforcement already.
- Maintenance burden grows with every edge case.

### D. Minimal guardrails (only Pydantic validation)

**Rejected** because:

- The system-prompt layer is cheap (one file) and meaningfully reduces tone/scope drift.
- Operational guardrails (`max_tokens`, input limits, key handling) are non-negotiable in any real deployment.

## References

- NVIDIA NeMo Guardrails — <https://developer.nvidia.com/nemo-guardrails>
- OpenAI structured outputs — <https://platform.openai.com/docs/guides/structured-outputs>
- Anthropic tool use / structured outputs — <https://docs.claude.com/en/docs/build-with-claude/tool-use>
- Ollama JSON mode — <https://github.com/ollama/ollama/blob/main/docs/api.md>
