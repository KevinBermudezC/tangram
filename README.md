# Tangram

> Architectures, piece by piece.

Open source visual editor for system architecture, with an AI copilot that teaches as you build.

**Status:** pre-alpha. Schema and scaffolding in progress.

## What is this?

Tangram is a self-hosted tool for designing software architectures visually. You drag components onto a canvas, connect them, and an AI copilot explains *why* each piece matters and *how* it fits together. The goal: help junior developers level up their system design skills by doing.

Inspired by the classic Tangram puzzle — 7 geometric pieces that combine into infinite figures. Likewise, Tangram (the tool) gives you a small set of architectural components that combine into any system you can imagine.

## Why self-hosted?

- **Your data stays yours.** Diagrams live in your local Postgres.
- **BYOK or local AI.** Use your own OpenAI/Anthropic key, or run Ollama locally — zero inference cost.
- **No vendor lock-in.** The schema is open, the code is open, the deployment is yours.

## Stack

- **Frontend:** Next.js + React Flow + TypeScript
- **Backend:** FastAPI + SQLModel (Pydantic-driven)
- **Database:** Postgres + pgvector (for future RAG)
- **AI:** provider-agnostic (Ollama, OpenAI, Anthropic, custom endpoints)

## Quick start

```bash
git clone https://github.com/<org>/tangram
cd tangram
docker compose up
```

Open http://localhost:3000.

## Status & roadmap

See [ROADMAP.md](./ROADMAP.md). MVP focuses on: visual editor, ~7 component types, AI-driven generation from a text prompt, contextual explanations.

## Contributing

Looking for contributors. We use **[OpenSpec](https://openspec.dev)** for change proposals — non-trivial changes start with a spec in `openspec/`, then code. See [CONTRIBUTING.md](./CONTRIBUTING.md) and issues tagged `good first issue`.

## Project layout

```
backend/             FastAPI + SQLModel + Pydantic
frontend/            Next.js + React Flow
db/                  Postgres migrations
docs/
  architecture/      ADRs (architectural decisions)
  schema/            Diagram schema reference
openspec/
  changes/           In-flight change proposals
  specs/             Accepted feature specs
scripts/             Codegen, dev helpers
```

## License

MIT.
