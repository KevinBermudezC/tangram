# Tangram

[![CI](https://github.com/KevinBermudezC/tangram/actions/workflows/ci.yml/badge.svg)](https://github.com/KevinBermudezC/tangram/actions/workflows/ci.yml)

> Architectures, piece by piece.

Open source visual editor for system architecture, with an AI copilot that teaches as you build.

**Status:** pre-alpha. Schema and scaffolding in progress.

## What is this?

Tangram is a self-hosted tool for designing software architectures visually. You drag components onto a canvas, connect them, and an AI copilot explains *why* each piece matters and *how* it fits together. The goal: help junior developers level up their system design skills by doing.

Inspired by the classic Tangram puzzle — 7 geometric pieces that combine into infinite figures. Likewise, Tangram (the tool) gives you a small set of architectural components that combine into any system you can imagine.

## Why self-hosted?

- **Your data stays yours.** Diagrams live as plain JSON files in `data/diagrams/` on your machine.
- **BYOK or local AI.** Use your own OpenAI/Anthropic key, or run Ollama locally — zero inference cost.
- **No vendor lock-in.** The schema is open, the code is open, the deployment is yours.

## Stack

- **Frontend:** Next.js + React Flow + TypeScript
- **Backend:** FastAPI + Pydantic v2 (Python 3.11+)
- **Storage:** filesystem (JSON files) for diagrams, Chroma (file-based) for patterns embeddings
- **AI:** provider-agnostic (Ollama default, BYOK for OpenAI / Anthropic / custom)

**No Docker required for local development.** A `Dockerfile` ships for opt-in production deployments.

## Quick start

Backend:

```bash
git clone https://github.com/<org>/tangram
cd tangram/backend
python -m venv .venv && source .venv/bin/activate   # or: .venv\Scripts\Activate.ps1 on Windows
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
# → http://localhost:8000/health
```

Frontend (in another terminal):

```bash
cd tangram/frontend
npm install
npm run dev
# → http://localhost:3000
```

See [`backend/README.md`](./backend/README.md) for the full backend reference.

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
