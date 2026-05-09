# Roadmap

## MVP (current focus)

Goal: someone clones the repo, runs `docker compose up`, types "I want to build X" into a prompt, and sees an editable diagram in seconds.

- [ ] Schema v0 finalized → see [docs/schema/diagram-v0.md](./docs/schema/diagram-v0.md)
- [ ] Backend scaffolding (FastAPI + SQLModel)
- [ ] Pydantic models matching the schema
- [ ] Postgres + pgvector via docker-compose
- [ ] Frontend scaffolding (Next.js + React Flow)
- [ ] OpenAPI → TypeScript codegen pipeline
- [ ] LLM provider abstraction (Ollama, OpenAI, Anthropic)
- [ ] System prompt v0 (pedagogical tone)
- [ ] `POST /generate` — text → diagram
- [ ] `POST /analyze` — diagram → feedback
- [ ] Editor: drag, drop, connect, edit, delete
- [ ] Side panel: per-node AI explanation
- [ ] Save / load diagrams

## Phase 2

- Persistence beyond local single-user
- RAG over architectural patterns (pgvector)
- Reactive AI mode (suggestions while editing, not just on demand)
- Custom component types
- Diagram versioning / change history

## Phase 3

- OpenAPI export
- DB schema export from `database` nodes
- Multi-model orchestration
- Collaboration / sharing
- Cost / SLA annotations

## Good first issues

(To be filled as we hit them.)

- [ ] Pick a font for diagram labels
- [ ] Add a "copy schema as JSON" button
- [ ] Translate the UI to additional locales
