# Roadmap

The roadmap maps to OpenSpec change proposals. Each MVP item below is either an **active** proposal under `openspec/changes/`, an already-merged proposal under `openspec/specs/`, or **planned** (not yet written).

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the propose → apply → archive workflow.

## MVP

Goal: someone clones the repo, runs `docker compose up`, types *"I want to build a delivery app"* into a prompt, and sees an editable diagram in seconds.

| # | Capability                              | Proposal                                     | Status   |
| - | --------------------------------------- | -------------------------------------------- | -------- |
| 1 | Diagram schema                          | `docs/schema/diagram-v0.md`                  | ✅ Done   |
| 2 | Backend runtime + dev environment       | `establish-mvp-foundations`                  | 🟡 Active |
| 3 | LLM provider abstraction                | `add-llm-provider-abstraction`               | ⬜ Planned |
| 4 | System prompt v0 (pedagogical)          | `add-system-prompt-v0`                       | ⬜ Planned |
| 5 | `POST /generate` (text → diagram)       | `add-diagram-generation-endpoint`            | ⬜ Planned |
| 6 | `POST /analyze` (diagram → feedback)    | `add-diagram-analysis-endpoint`              | ⬜ Planned |
| 7 | Diagram persistence (save/load)         | `add-diagram-persistence`                    | ⬜ Planned |
| 8 | Frontend foundation (Next.js + RF)      | `establish-frontend-foundation`              | ⬜ Planned |
| 9 | OpenAPI → TypeScript codegen            | `add-openapi-typescript-codegen`             | ⬜ Planned |
| 10| Editor: drag/drop/connect/edit          | `add-diagram-editor`                         | ⬜ Planned |
| 11| Per-node AI explanation panel           | `add-ai-explanation-panel`                   | ⬜ Planned |

## Phase 2

Polish, durability, and the features that make Tangram more than a toy.

| # | Capability                              | Status         |
| - | --------------------------------------- | -------------- |
| 1 | Reactive AI mode (suggestions while editing) | ⬜ Planned |
| 2 | RAG over architectural patterns (`pgvector`) | ⬜ Planned |
| 3 | Custom component types                       | ⬜ Planned |
| 4 | Diagram versioning / change history          | ⬜ Planned |
| 5 | Export / import diagrams as JSON             | ⬜ Planned |
| 6 | Dark / light theme                           | ⬜ Planned |
| 7 | Eval harness for the LLM pipeline            | ⬜ Planned |

## Phase 3

| # | Capability                              | Status         |
| - | --------------------------------------- | -------------- |
| 1 | OpenAPI export from `backend` nodes      | ⬜ Planned |
| 2 | DB schema export from `database` nodes   | ⬜ Planned |
| 3 | Multi-model orchestration                | ⬜ Planned |
| 4 | Collaboration / sharing                  | ⬜ Planned |
| 5 | Cost / SLA annotations                   | ⬜ Planned |
| 6 | Plugin system (third-party node types)   | ⬜ Planned |

## Status legend

- ✅ **Done** — merged and archived under `openspec/specs/`.
- 🟡 **Active** — proposal exists under `openspec/changes/`, work in progress.
- ⬜ **Planned** — referenced here, not yet proposed. Anyone can write the first draft.

## Good first issues

(To be filled as we land specific tasks.)

- [ ] Pick a font for diagram labels
- [ ] Add a "copy schema as JSON" button
- [ ] Translate the UI to additional locales
- [ ] Add the parity test in `backend/tests/test_schema_parity.py` (task 3.3 in `establish-mvp-foundations`)
