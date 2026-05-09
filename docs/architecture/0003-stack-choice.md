# ADR-0003 — Stack choice

**Status:** Accepted

**Date:** 2026-05-09

**Decision-makers:** Tangram core team

**Related:** [ADR-0004 — Persistence](./0004-persistence.md), [ADR-0005 — Patterns library architecture](./0005-patterns-library-and-rag.md)

---

## Context

Tangram is a self-hosted, open-source visual editor for system architectures with an LLM copilot. Two contributors (one with stronger AI/frontend background, one with stronger backend/infrastructure background) need a stack that:

- Minimizes setup friction for a contributor cloning the repo (we expect junior developers as primary users and contributors).
- Stays self-hosted by default — no required cloud services, no required SaaS dependencies.
- Lets the AI/frontend lead work in TypeScript/React and the backend lead work in Python without constant context-switching.
- Keeps options open for Phase 2 features (RAG, multi-user, observability) without re-platforming.
- Has well-known building blocks so contributors can ramp up quickly with public documentation.

## Decision

The MVP stack is:

| Layer            | Choice                                            |
| ---------------- | ------------------------------------------------- |
| Frontend         | Next.js + React Flow + TypeScript                 |
| Backend          | FastAPI + Pydantic v2 (Python 3.11+)              |
| Diagram storage  | Filesystem — JSON files under `<DATA_DIR>/diagrams/` |
| Patterns vector store | Chroma (file-based) under `<CHROMA_PATH>`     |
| LLM access       | Provider abstraction with adapters for Ollama (default), OpenAI, Anthropic. BYOK or local. |
| Local dev        | `pip install -e ".[dev]"` + `uvicorn`, `npm install` + `npm run dev`. **No Docker required.** |
| Production deploy | `Dockerfile` provided as opt-in; users can also run the backend bare-metal |

Each layer is justified below.

### Frontend: Next.js + React Flow + TypeScript

- **Next.js**: Tangram is a single application with a frontend and a small set of API client hooks. Next.js gives us file-based routing, easy deployment to most platforms, and is the default in the React ecosystem. App Router is fine.
- **React Flow**: purpose-built for editable node-and-edge graphs. The alternatives (D3 from scratch, Cytoscape, JointJS) require significantly more work for the same UX. The trade-off is React Flow's licensing and feature surface — we accept both.
- **TypeScript strict mode**: contracts on the wire come from the backend's auto-generated OpenAPI; TypeScript catches drift at compile time.

### Backend: FastAPI + Pydantic v2

- **FastAPI**: Pydantic-native, OpenAPI for free, async-friendly, mature.
- **Pydantic v2** as the source of truth for data shapes (see ADR-0001 and the schema-driven-development convention used throughout the project). `Diagram`, `Node`, `Edge`, etc., are Pydantic models. TypeScript types are auto-generated from the resulting OpenAPI.
- **No SQLModel in MVP**: with no relational DB in scope, we avoid pulling in SQLAlchemy + SQLModel just to keep options open. The `tables/` package exists for future use but is empty.

### Storage: filesystem + Chroma

The full reasoning lives in [ADR-0004](./0004-persistence.md). Summary: diagrams are documents written as JSON files; the patterns vector store is a file-based Chroma collection. No relational DB, no Docker dependency for local dev.

### LLM access: provider abstraction (Ollama / OpenAI / Anthropic)

- **Self-host friendly**: Ollama runs locally for free. No cloud account required to use Tangram.
- **BYOK**: users with OpenAI or Anthropic keys can plug them in. We never ship third-party API keys.
- **Provider abstraction**: a small adapter layer in `backend/app/services/llm/` so that a single switch (env var) routes calls to whichever provider the user picked.
- **Future-proof**: adding Mistral, Cohere, or Llama-via-other-runtimes is one adapter file.

### No Docker for MVP local development

- Docker remains available as a deployment mechanism (we ship a `Dockerfile`).
- For local development, we explicitly do not require it. The earlier plan to use Postgres + pgvector via docker-compose was abandoned once we realized the MVP storage needs are document-shaped (filesystem) and small-corpus (Chroma) — neither requires a database server.
- This decision is the single biggest reduction in onboarding friction for OSS contributors.

## Consequences

### Positive

- A contributor with Python 3.11+ and Node 20+ can clone, install, and run Tangram in two commands per service. No platform engineering is required to start contributing.
- The stack is boring in the best sense — every layer has years of production track record.
- The frontend/backend split lets each contributor work in the language they prefer with minimal cross-talk.
- Migrating any layer later is mechanical: filesystem → Postgres, Chroma → pgvector, Next.js → Remix, etc. We have not painted ourselves into corners.

### Negative

- We support three LLM providers from day one. Each new provider behavior (rate limits, structured-output quirks, streaming differences) is something we have to keep in sync. We accept this cost for the BYOK + local story.
- Chroma's on-disk format is not part of any open standard; if Chroma changes formats, contributors may need to rebuild their store. Mitigation: pin the Chroma version, document `tangram seed`.
- React Flow's node/edge model occasionally pushes us toward shapes we wouldn't have chosen otherwise. We accept this for the speed it gives us.
- The "no Docker required" story has to be enforced in PR review; it is easy for a contributor to add a Postgres dependency that breaks the local-dev contract. Mitigation: the developer-environment spec in the foundations proposal makes this explicit.

## Alternatives considered

### A. Postgres + pgvector via docker-compose

**Rejected.** The original plan. Pulled because (1) MVP has no relational requirements — diagrams are documents; (2) Docker as a hard dependency is real friction for junior-dev contributors; (3) the Phase-2 features that would justify Postgres (multi-user, large RAG corpus) are not on the near horizon. We will reconsider when one of those lands.

### B. SQLite + sqlite-vec for everything

**Rejected.** Cleaner than Postgres but sqlite-vec is a young project (released 2024) with a small community. Documentation and troubleshooting are thin. We prefer Chroma's larger ecosystem and pip-install-only setup. SQLite remains a viable fallback if Chroma disappoints.

### C. Django instead of FastAPI

**Rejected.** Django is excellent for full-stack monoliths with templates, admin, and ORM at the center. Tangram has none of those needs and a Pydantic-first contract layer. FastAPI is a better fit.

### D. Hosted LLM provider only (OpenAI or Anthropic)

**Rejected.** Tangram is open source and self-hosted. Requiring a paid API key to use the tool would contradict the positioning. Ollama support is non-negotiable.

### E. Frontend-only architecture (no backend, calls LLMs from the browser)

**Rejected.** Calling LLM APIs from the browser would require shipping the user's API key to the client, which is a security non-starter. The backend is required to keep keys server-side.

## References

- ADR-0001 — Guardrails strategy
- ADR-0002 — OpenSpec for change proposals
- ADR-0004 — Persistence (filesystem for diagrams, Chroma for embeddings)
- ADR-0005 — Patterns library architecture
