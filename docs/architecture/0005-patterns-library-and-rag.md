# ADR-0005 — Patterns library architecture (RAG over a bundled corpus)

**Status:** Accepted

**Date:** 2026-05-09

**Decision-makers:** Tangram core team

**Related:** [ADR-0001 — Guardrails strategy](./0001-guardrails-strategy.md), [ADR-0003 — Stack choice](./0003-stack-choice.md), [ADR-0004 — Persistence](./0004-persistence.md)

---

## Context

The simplest version of an LLM-driven design tool is "user types a prompt, we send it to an LLM with a system prompt that says 'be helpful', we render the response." That product is indistinguishable from a thin wrapper around ChatGPT/Claude/Ollama.

Tangram's differentiation, beyond the visual editor itself, is meant to come from a **curated body of architectural knowledge**:

- Patterns (CQRS, event-driven, microservices vs. monolith, JAMstack, etc.).
- Anti-patterns and the rationale for avoiding them.
- Component-type metadata (when to use a queue, what tradeoffs come with each database family, etc.).
- Real-world architecture references.

Naïvely we could shove all of this into the system prompt. That fails on two axes:

1. **Token economics**: BYOK users pay per token; Ollama users wait per token. A 50-pattern corpus inline would dominate every call.
2. **Signal-to-noise**: stuffing irrelevant patterns into the context dilutes the model's attention. We want the model to see the *relevant* patterns for the user's request, not the union of all patterns.

This is precisely the problem RAG solves: retrieve the few documents most relevant to the query, then condition generation on those.

## Decision

Tangram ships with a **bundled, curated patterns corpus** and uses **RAG** to retrieve only the patterns relevant to each LLM call.

### Source of truth: `patterns/*.md`

The corpus lives at the top of the repo as a folder of markdown files. Each file documents one pattern with consistent sections (intent, when to use, when to avoid, components involved, common pitfalls, references). Maintainers and contributors edit these directly; PRs to `patterns/` are first-class contributions.

### Vector store: Chroma (file-based)

The corpus is embedded into a Chroma collection at `<CHROMA_PATH>` (see ADR-0004). Chroma is mature, file-based, and `pip install`-able — no server, no Docker.

### Pre-computed embeddings shipped in the repo

We pre-compute embeddings for the default embedder (`ollama/nomic-embed-text`) and commit the resulting Chroma directory. First-run is instant for users on the default embedder.

### `tangram seed` for non-default embedders

A script (Phase 2 deliverable) regenerates the Chroma store using a different embedder. Users running OpenAI for everything can re-embed once with `text-embedding-3-small`, and from then on retrieval is consistent.

### Retrieval at LLM call time

Each call to the LLM composes its prompt from:

1. **System prompt of the active mode** (e.g. `modes/tutor.md`) — small, always included.
2. **Component-type metadata** for the node types referenced in the current diagram — small, always relevant.
3. **Anti-pattern violations** detected by the static rules engine on the current diagram — code, not LLM. Findings are inserted as context.
4. **Top-k patterns** retrieved from Chroma using the user's request as the query, **k=3 by default**.
5. **The user's request** and **the current diagram** (as JSON).

The model never sees more than three pattern documents at a time. Token cost stays bounded as the corpus grows.

### What lives where

```
patterns/                  ← markdown source-of-truth, human-edited, PR-able
data/patterns.chroma/      ← Chroma collection, derived from patterns/
backend/app/services/retrieval/
                           ← the embedder + retrieval client + query interface
backend/app/services/llm/prompts/
                           ← prompt-composition logic
modes/                     ← per-mode system prompts (tutor, senior, brainstorm)
components/                ← per-node-type metadata (yaml)
rules/                     ← anti-pattern detection (Python code)
```

## Consequences

### Positive

- The product is demonstrably more than a wrapper: there is a curated, version-controlled, human-readable corpus that the LLM consults, plus a static rules engine, plus mode definitions, plus component metadata. Each is independently inspectable.
- Token cost scales sublinearly with corpus size — adding pattern #51 does not add cost to existing queries.
- Contributors have an obvious onboarding ramp: writing a new pattern is a markdown PR, no code knowledge required.
- The corpus becomes a community asset over time. A growing `patterns/` is a moat that any wrapper would have to build from scratch.
- We preserve the Phase 2 path to RAG over user data (e.g. their own architectural notes) — same retrieval primitives, different collection.

### Negative

- We commit to the discipline of curating the corpus. A neglected `patterns/` folder is worse than no patterns library at all because it implies expertise the project does not have.
- Pre-computed embeddings are model-locked. Users who change embedders pay a one-time `tangram seed` cost.
- Adding RAG complicates the prompt-composition path. Failure modes (Chroma errors, embedder unavailable) need to degrade gracefully — fall back to inlining a small fixed set of patterns rather than crashing.
- Repo size grows with the bundled embeddings. Currently in the low-MB range for ~50 patterns; if we ever add hundreds of patterns or higher-dimensional embeddings, we revisit (Git LFS, lazy download, etc.).

### Failure modes and mitigations

- **Chroma store corrupted** → backend logs a recoverable error and falls back to no-RAG mode (system prompt only). User sees a banner suggesting `tangram seed`.
- **Embedder unavailable** (e.g. Ollama not running and user is on the default embedder) → retrieval returns empty, prompt composition proceeds without retrieved patterns.
- **Embedder mismatch** (store was embedded with model A, runtime uses model B) → we detect this at boot via a metadata file in `<CHROMA_PATH>` and warn loudly with the suggested `tangram seed` command.

## Alternatives considered

### A. Inline all patterns in the system prompt

**Rejected.** Token cost is linear in corpus size; signal-to-noise gets worse with each addition. Works at <5 patterns, breaks badly at 30+.

### B. Cloud-hosted RAG service we operate

**Rejected.** Centralizing the corpus retrieval contradicts the self-hosted, BYOK ethos. Operational cost on us. Not viable for an OSS project at this stage.

### C. User brings their own RAG corpus

**Rejected.** Friction is too high. A junior dev cloning Tangram is not going to curate a corpus to make the tool useful. The point of a bundled corpus is that the tool is good out of the box.

### D. Pure prompt engineering, no RAG

**Considered.** A very rich system prompt with 5–10 patterns inline can carry the MVP. We may start there if the patterns proposal lands first as a non-RAG MVP and RAG comes later. **Open question** — see below.

## Open Questions

- **Default `k` for retrieval**: starting with 3. We may tune this based on actual corpus size and prompt-quality observations.
- **Embedder default**: `ollama/nomic-embed-text` is local and free, but quality is below proprietary embedders. Worth re-evaluating once we have an evals suite.
- **Whether to embed at the pattern level or at chunk level**: starting at pattern level (one embedding per `patterns/<name>.md`). If patterns grow long, chunking will become necessary.
- **Whether RAG ships in MVP or Phase 2**: the patterns library can land first as a non-RAG, inline subset (top 5 patterns inlined). RAG can follow as soon as the corpus exceeds ~10 patterns. Decision deferred to the first proposal that lands the corpus content (`add-patterns-library` or `add-patterns-library-and-rag`).

## References

- ADR-0001 — Guardrails strategy
- ADR-0003 — Stack choice
- ADR-0004 — Persistence
- Chroma documentation — <https://docs.trychroma.com/>
- The bundled corpus pattern in PrivateGPT, h2oGPT
