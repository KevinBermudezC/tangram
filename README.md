# Tangram

[![CI](https://github.com/KevinBermudezC/tangram/actions/workflows/ci.yml/badge.svg)](https://github.com/KevinBermudezC/tangram/actions/workflows/ci.yml)

> Architectures, piece by piece.

I'm building Tangram because I keep seeing junior devs hit the same wall: system design feels like memorizing flashcards. *"When do I add a queue? Why use a cache here? Is this Postgres or Mongo?"* The answers usually live in 40-minute YouTube videos or behind senior-dev coffee chats.

Tangram is the tool I wish I'd had: drag a few boxes onto a canvas, connect them, and an AI that *teaches* (not just generates) explains what each piece does, why it's there, and what usually goes wrong. Self-hosted, MIT, BYOK or Ollama. No SaaS to sign up for.

**Status:** pre-alpha. The backend can generate diagrams via LLM, and a minimal read-only web UI is now in place. Editing the diagram (drag, connect, edit labels) is still ahead.

## What it'll be (and what it won't)

Tangram **will**: give you a canvas with about 8 component types (frontend, backend, database, auth, storage, external services, queues, caches), an AI that comments on the diagram as you build, and exports to things you can actually use (Mermaid, docker-compose, OpenAPI specs).

Tangram **won't**: be a replacement for actually learning system design. It won't pass interviews for you. It also won't be a Figma competitor or a generic diagramming tool. Use Excalidraw or draw.io for that.

The name is from the [Tangram puzzle](https://en.wikipedia.org/wiki/Tangram): seven geometric pieces that combine into infinite figures. Same idea here. Small set of components, infinite architectures.

## Why self-hosted, why open source

Three reasons, in honesty order:

1. **Your diagrams are yours.** They live as plain JSON files in `data/diagrams/` on your machine. Backups are `cp -r`. No vendor can lose them.
2. **No inference bill.** Ollama runs locally and is free. If you want better quality, plug in your own OpenAI or Anthropic key. Nothing ever routes through me.
3. **You can read the prompts.** The "intelligence" is curated markdown in [`patterns/`](./patterns/) (coming soon) and YAML in [`components/`](./components/). It's editable, contributable, version-controlled. Not a black box.

## Stack

- **Frontend:** Next.js 15 + React 19 + React Flow + TypeScript
- **Backend:** FastAPI + Pydantic v2 on Python 3.11+
- **Storage:** JSON files for diagrams, Chroma for embeddings. No Postgres in MVP.
- **AI:** Ollama by default. OpenAI or Anthropic with your own key.

No Docker required to run locally. A `Dockerfile` exists if you want to deploy.

## Quick start

Two terminals.

**Terminal 1 — backend:**

```bash
git clone https://github.com/KevinBermudezC/tangram
cd tangram/backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env                 # edit if using BYOK or Ollama Cloud
uvicorn app.main:app --reload
```

**Terminal 2 — frontend:**

```bash
cd tangram/frontend
npm install
npm run dev
```

Open <http://localhost:3000>, type a prompt, hit Generate.

More detail: [`backend/README.md`](./backend/README.md), [`frontend/README.md`](./frontend/README.md).

## Where we are

See [ROADMAP.md](./ROADMAP.md). Short version: foundations done, features starting now. About a third of the MVP work is shipped (schema, backend skeleton, LLM providers, CI, component metadata library). The visible stuff (editor, generation, analysis, frontend) is still ahead.

## Contributing

I'd love help, especially with the [`components/`](./components/) and (coming) `patterns/` libraries. Editing those is *the* lowest-friction way to make Tangram smarter without writing Python.

Read [CONTRIBUTING.md](./CONTRIBUTING.md) first. The short version: non-trivial changes start with an [OpenSpec](https://openspec.dev) proposal, which can live in the same PR as the code. Trivial changes (typos, doc fixes) just open a PR.

Good first issues are labeled on the [issue tracker](https://github.com/KevinBermudezC/tangram/issues).

## Project layout

```
backend/             FastAPI + Pydantic, the brain
components/          Curated YAML, one per node type, fully readable as docs
docs/
  architecture/      ADRs — the durable decisions
  schema/            Diagram schema reference
frontend/            Next.js + React 19 + React Flow (read-only viewer)
openspec/
  changes/           In-flight change proposals
  specs/             Accepted specs, current ground truth
patterns/            (coming) curated architectural patterns the LLM consults
scripts/             Dev helpers
```

## A note on AI assistance

> 
> 
> *I'm building Tangram with AI assistance. I review every change before it lands and I'm the one making the architectural calls.*
>
> *If the AI-assisted angle bothers you, fair enough. If you're curious how it holds up in practice, the commit history is open and the OpenSpec proposals show how each change got reasoned through.*

The reason this note exists at all: in 2026 hiding AI assistance is a credibility risk if it's later discovered. I'd rather be upfront.

## License

MIT. Use it, fork it, ship it.
