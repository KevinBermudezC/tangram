# Roadmap

The roadmap maps to OpenSpec change proposals. Each MVP item below is either an **active** proposal under `openspec/changes/`, an already-merged proposal under `openspec/specs/`, or **planned** (not yet written).

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the propose → apply → archive workflow.

## MVP

Goal: someone clones the repo, runs `pip install` + `uvicorn` + `npm run dev`, types *"I want to build a delivery app"* into a prompt, and sees an editable diagram in seconds. **No Docker required.**

| #  | Capability                                  | Proposal                                     | Status   |
| -- | ------------------------------------------- | -------------------------------------------- | -------- |
| 1  | Diagram schema                              | `docs/schema/diagram-v0.md`                  | ✅ Done   |
| 2  | Backend foundation + storage layout         | `establish-mvp-foundations`                  | ✅ Done   |
| 3  | LLM provider abstraction (Ollama/OpenAI/Anthropic) | `add-llm-provider-abstraction`        | ✅ Done   |
| 4  | CI pipeline (lint + test + openspec)        | `add-ci-pipeline`                            | ✅ Done   |
| 5  | Component metadata files (8 yamls)          | `add-component-metadata`                     | ⬜ Planned |
| 6  | Anti-pattern rules engine (~5 rules)        | `add-anti-pattern-rules`                     | ⬜ Planned |
| 7  | Patterns library v0 + RAG via Chroma        | `add-patterns-library-and-rag`               | ⬜ Planned |
| 8  | Tutor mode + system prompt v0               | `add-tutor-mode`                             | ⬜ Planned |
| 9  | `POST /generate` (text → diagram)           | `add-diagram-generation-endpoint`            | ⬜ Planned |
| 10 | `POST /analyze` (diagram → feedback + rule findings) | `add-diagram-analysis-endpoint`     | ⬜ Planned |
| 11 | Diagram persistence routes (filesystem)     | `add-diagram-persistence-routes`             | ⬜ Planned |
| 12 | Frontend foundation (Next.js + React Flow)  | `establish-frontend-foundation`              | ⬜ Planned |
| 13 | OpenAPI → TypeScript codegen                | `add-openapi-typescript-codegen`             | ⬜ Planned |
| 14 | Editor: drag/drop/connect/edit              | `add-diagram-editor`                         | ⬜ Planned |
| 15 | Per-node AI explanation panel               | `add-ai-explanation-panel`                   | ⬜ Planned |
| 16 | Export to Mermaid                           | `add-mermaid-export`                         | ⬜ Planned |

> CI lands at #4 (post-LLM-abstraction, pre-feature-work) so that the editor + LLM features land with guardrails from day one.

## Phase 2

Polish, durability, and the features that make Tangram more than a toy.

| # | Capability                                                | Status         |
| - | --------------------------------------------------------- | -------------- |
| 1 | Reactive AI mode (suggestions while editing, à la Cursor) | ⬜ Planned |
| 2 | `senior` and `brainstorm` modes                           | ⬜ Planned |
| 3 | Patterns library grows (target 30+ patterns, contributions) | ⬜ Planned |
| 4 | More anti-pattern rules (target 30+)                      | ⬜ Planned |
| 5 | Custom component types via plugin system                  | ⬜ Planned |
| 6 | Diagram versioning / change history                       | ⬜ Planned |
| 7 | Export / import diagrams as JSON                          | ⬜ Planned |
| 8 | Export to docker-compose, OpenAPI, SQL DDL                | ⬜ Planned |
| 9 | Dark / light theme                                        | ⬜ Planned |
| 10 | `tangram seed` CLI for re-embedding patterns             | ⬜ Planned |
| 11 | Eval harness for the LLM pipeline                        | ⬜ Planned |
| 12 | Re-evaluate NeMo Guardrails (per ADR-0001)               | ⬜ Planned |

## Phase 3

| # | Capability                                            | Status         |
| - | ----------------------------------------------------- | -------------- |
| 1 | Migrate persistence to Postgres + pgvector (if multi-user) | ⬜ Planned |
| 2 | Collaboration / sharing                               | ⬜ Planned |
| 3 | Multi-model orchestration                             | ⬜ Planned |
| 4 | Plugin system (third-party node types, modes, integrations) | ⬜ Planned |
| 5 | Cost / SLA annotations on nodes                       | ⬜ Planned |
| 6 | Import from Terraform / k8s manifests                 | ⬜ Planned |

## Status legend

- ✅ **Done** — merged and archived under `openspec/specs/`.
- 🟡 **Active** — proposal exists under `openspec/changes/`, work in progress.
- ⬜ **Planned** — referenced here, not yet proposed. Anyone can write the first draft.

## Good first issues

(To be filled as we land specific tasks.)

- [ ] Pick a font for diagram labels
- [ ] Add a "copy schema as JSON" button
- [ ] Translate the UI to additional locales
- [ ] Add the `tangram seed` script (Phase 2 item, scaffold welcome as a draft)
- [ ] Required-status-checks rule on the branch ruleset — flip `lint`, `test`, `openspec` to required (manual UI step now that CI runs green)
