# Roadmap

The roadmap maps to OpenSpec change proposals. Each MVP item below is either an **active** proposal under `openspec/changes/`, an already-merged proposal under `openspec/specs/`, or **planned** (not yet written).

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the propose → apply → archive workflow.

## MVP

Goal: someone clones the repo, runs `pip install` + `uvicorn` + `pnpm dev`, types *"I want to build a delivery app"* into a prompt, and sees an editable diagram in seconds. **No Docker required.**

| #  | Capability                                  | Proposal                                     | Status     |
| -- | ------------------------------------------- | -------------------------------------------- | ---------- |
| 1  | Diagram schema                              | `docs/schema/diagram-v0.md`                  | ✅ Done    |
| 2  | Backend foundation + storage layout         | `establish-mvp-foundations`                  | ✅ Done    |
| 3  | LLM provider abstraction (Ollama/OpenAI/Anthropic) | `add-llm-provider-abstraction`        | ✅ Done    |
| 4  | CI pipeline (lint + test + openspec)        | `add-ci-pipeline`                            | ✅ Done    |
| 5  | Component metadata files (8 yamls)          | `add-component-metadata`                     | 🟢 Merged  |
| 6  | Anti-pattern rules engine (~5 rules)        | `add-anti-pattern-rules`                     | 🟢 Merged  |
| 7  | Patterns library v0                         | `add-patterns-library`                       | 🟢 Merged  |
| 8  | RAG retrieval via Chroma                    | `add-rag-retrieval`                          | 🟢 Merged  |
| 9  | Tutor mode + system prompt v0               | `add-tutor-mode`                             | 🟢 Merged  |
| 10 | `POST /generate` (text → diagram)           | `add-diagram-generation-endpoint`            | 🟢 Merged  |
| 11 | Frontend foundation + UI shell              | `establish-frontend-foundation`              | 🟡 Active  |
| 12 | `POST /analyze` (diagram → feedback + rule findings) | `add-diagram-analysis-endpoint`     | ✅ Done    |
| 13 | Diagram persistence routes (filesystem)     | `add-diagram-persistence-routes`             | 🟡 Active  |
| 14 | OpenAPI → TypeScript codegen                | `add-openapi-typescript-codegen`             | ⬜ Planned  |
| 15 | Editor: drag/drop/connect/edit              | `add-diagram-editor`                         | ⬜ Planned  |
| 16 | Per-node AI explanation panel               | `add-ai-explanation-panel`                   | ⬜ Planned  |
| 17 | Chat-about-diagram endpoint                 | `add-chat-about-diagram` (planned)           | ⬜ Planned  |
| 18 | Export to Mermaid                           | `add-mermaid-export`                         | ⬜ Planned  |

> CI lands at #4 (post-LLM-abstraction, pre-feature-work) so that the editor + LLM features land with guardrails from day one.
>
> Items #5–#10 are merged into `main` but not yet **archived** to `openspec/specs/` (the post-merge `openspec archive <name>` step). A small chore PR can knock those out in one batch.

## Phase 2

Polish, durability, and the features that make Tangram more than a toy.

| #  | Capability                                                | Status      |
| -- | --------------------------------------------------------- | ----------- |
| 1  | Reactive AI mode (suggestions while editing, à la Cursor) | ⬜ Planned   |
| 2  | `senior` and `brainstorm` modes                           | ⬜ Planned   |
| 3  | Patterns library grows (target 30+ patterns, contributions) | ⬜ Planned |
| 4  | More anti-pattern rules (target 30+)                      | ⬜ Planned   |
| 5  | Custom component types via plugin system                  | ⬜ Planned   |
| 6  | Diagram versioning / change history                       | ⬜ Planned   |
| 7  | Export / import diagrams as JSON                          | ⬜ Planned   |
| 8  | Export to docker-compose, OpenAPI, SQL DDL                | ⬜ Planned   |
| 9  | Dark / light theme                                        | ⬜ Planned   |
| 10 | `tangram seed` CLI for re-embedding patterns              | ⬜ Planned   |
| 11 | Eval harness for the LLM pipeline                         | ⬜ Planned   |
| 12 | Re-evaluate NeMo Guardrails (per ADR-0001)                | ⬜ Planned   |

## Phase 3

| # | Capability                                            | Status      |
| - | ----------------------------------------------------- | ----------- |
| 1 | Migrate persistence to Postgres + pgvector (if multi-user) | ⬜ Planned |
| 2 | Collaboration / sharing                               | ⬜ Planned   |
| 3 | Multi-model orchestration                             | ⬜ Planned   |
| 4 | Plugin system (third-party node types, modes, integrations) | ⬜ Planned |
| 5 | Cost / SLA annotations on nodes                       | ⬜ Planned   |
| 6 | Import from Terraform / k8s manifests                 | ⬜ Planned   |

## Status legend

- ✅ **Done** — merged and archived under `openspec/specs/`.
- 🟢 **Merged** — code in `main`, archive step pending.
- 🟡 **Active** — proposal exists under `openspec/changes/`, work in progress on a branch.
- ⬜ **Planned** — referenced here, not yet proposed. Anyone can write the first draft.

## Frontend follow-ups

The UI shell (Home + Library + Editor + AI chat panel) ported from `frontend/prototype/` into Next.js in `feat/establish-frontend-foundation`. The visible chrome is in place; the next set of work wires it to real backend behaviour.

Most of these are ⬜ Planned and good first issues for contributors (see below).

| Capability                                  | Depends on                                  | Notes                                                                                                          |
| ------------------------------------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Real chat endpoint                          | `add-chat-about-diagram` (backend)          | The frontend already speaks the AI SDK + Streamdown stream protocol against `/api/chat` (a local mock route). Once the backend ships, the route becomes a thin proxy. |
| Library / Recent backed by real data         | `add-diagram-persistence-routes` (backend done) | `lib/hooks.ts:useDiagrams` is the single touch point. Today it returns mock from `lib/mock-data.ts`; swap the body for a `GET /diagrams` call. The backend routes (`POST/GET/DELETE /diagrams`) now exist; this is pure frontend wiring. |
| `/editor/[id]` route                         | persistence                                  | Open a saved diagram by ULID. Pairs with a `useDiagram(id)` query.                                              |
| Drag-and-drop palette → canvas               | `add-diagram-editor`                        | The palette in `components/editor/palette.tsx` is already `draggable=true`; the drop target on the canvas is a no-op until React Flow editor wires up. |
| Theme toggle (dark / light)                  | —                                           | The button exists in the editor topbar; wire `next-themes` and add dark color variables in `app/globals.css`. CSS already uses semantic tokens, so the work is one variables file + a toggle. |
| Command palette (Cmd-K)                      | —                                           | `cmdk` package. Open any diagram, create new, jump to settings, "ask AI…". Replaces the rail search.            |
| Export to Mermaid                            | `add-mermaid-export`                        | The "Export" button in the editor topbar is a placeholder. A client-side Diagram → Mermaid converter is enough for v0. |
| OpenAPI → TS types codegen                   | `add-openapi-typescript-codegen`            | Removes the hand-written `frontend/types/tangram.ts`. The PR header in that file flags the maintenance cost.   |
| Tests for new pages                          | —                                           | Vitest + Testing Library coverage for Home / Library / Editor states. Today only `PromptForm`, `api`, and `diagramToFlow` from the v0 shell have tests. |

## Good first issues

These are ready for a contributor to pick up. Each one is small, scoped, and unblocked.

- [ ] **Archive the merged OpenSpec changes** (#5–#10 above). One PR per change is fine, or one batch PR that runs `openspec archive <name>` for each. ~15 min of work, mostly mechanical.
- [ ] **Wire the dark mode toggle.** Add `next-themes`, swap the disabled button in `components/editor/topbar.tsx` for a real toggle, and add a dark theme block to `app/globals.css` (the CSS already uses semantic tokens like `bg-page` / `text-ink-strong`, so the work is mostly providing a second token set).
- [ ] **Client-side Mermaid export.** Implement `lib/diagramToMermaid.ts` (Diagram → Mermaid flowchart string) and wire the "Export" button in the editor topbar to copy the string and toast "Copied as Mermaid". No backend changes.
- [ ] **`useDiagrams` against real persistence.** When `add-diagram-persistence-routes` lands, swap the body of `useDiagrams` in `frontend/lib/hooks.ts` for a `GET /diagrams` call. The library and rail consume it; the call sites don't change.
- [ ] **`/editor/[id]` route + `useDiagram(id)`.** Loads a saved diagram by ULID and renders it in `<DiagramCanvas>`. Also requires persistence.
- [ ] **OpenAPI codegen.** Generate `frontend/types/tangram.ts` from the FastAPI spec at build time. The existing hand-written file's header comment flags the swap.
- [ ] **Page tests.** Vitest + Testing Library against the new Next.js pages: prompt → editor handoff, library filters, blank canvas hint, chat empty state.
- [ ] **Pick a font for diagram labels** (the canvas currently inherits the page font; we may want a tighter sans).
- [ ] **Add a "copy schema as JSON" button** for power users.
- [ ] **Translate the UI to additional locales.** Inter and JetBrains Mono are already loaded; the strings are scattered across components, so the first step is extracting them.
- [ ] **`tangram seed` script** for re-embedding patterns (Phase 2 item, scaffold welcome as a draft).
- [ ] **Required-status-checks rule on the branch ruleset** — flip `lint`, `test`, `openspec` to required (manual UI step now that CI runs green).
