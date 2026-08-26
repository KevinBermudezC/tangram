## Context

See `proposal.md` for motivation. On current `main`:

- `lib/api.ts` already has `listDiagrams` / `getDiagram` / `saveDiagram` / `deleteDiagram`.
- `lib/hooks.ts` already has live `useDiagrams`, `useDiagram(id)`, `useSaveDiagram`.
- `/editor/[id]` already loads via `useDiagram` and `/editor` already POSTs after generate and autosaves edits.
- Library and the rail already call `useDiagrams`, but they type the result as `MockDiagram` from `lib/mock-data.ts`, and `data ?? []` makes a failed fetch look like an empty store.

`POST /diagrams` is an upsert (no `PATCH`). Templates and the component catalog in `mock-data.ts` are unrelated catalogs.

## Goals / Non-Goals

**Goals:**
- One list view-model type, not named `MockDiagram` and not imported from `mock-data.ts`.
- Honest loading / empty / error UI on Library and Recent.
- Tests that lock the mapper + those states.
- Roadmap and OpenSpec archive of the completed backend change.

**Non-Goals:**
- New backend routes, `PATCH`, or wiring the disabled Delete menu.
- Chat, Mermaid export, dark mode, node-color restyle.
- Redirecting `/editor?prompt=…` to `/editor/{ulid}` after the first save (reopen is via Library / Recent).

## Decisions

**1. Thin UI list item, not raw `DiagramSummary`.**
Cards need `updatedLabel`, `components`/`connections`, and a `source` badge. Keep a mapper (`summary → list item`) next to the type so hooks stay a one-liner. Alternative: pass `DiagramSummary` into cards and format inside each consumer — rejected because the rail and Library would duplicate the relative-time + counts mapping.

**2. `source` stays client-side and defaults to `"ai"`.**
The backend does not track source. Every persisted diagram today is generated or saved from the editor; labeling them `"ai"` matches the current hook. Do not invent a storage field.

**3. Error vs empty is a query-state branch, not a fake list.**
Use TanStack Query `isError` / `isPending` / `data`. Never substitute mock records. Copy should mention the backend when the fetch fails (the rail already has a health pill; the list error is still explicit).

**4. Archive `add-diagram-persistence-routes` in this change.**
Its tasks are all checked; the original proposal named frontend as a follow-up. Sync its delta spec into `openspec/specs/diagram-persistence-routes/` and move the change under `openspec/changes/archive/`. This frontend change stays active until it merges (archive-after-merge per CONTRIBUTING).

## Risks / Trade-offs

- **Default `source: "ai"` on blank-canvas saves** → a hand-built diagram still shows the AI badge. Mitigation: acceptable until the backend tracks source; out of scope.
- **Query retry delay before the error UI** → `useDiagrams` should use a low retry count (0 or 1) so a down backend does not look like a long load.
- **Stale ROADMAP/issue text** → this PR rewrites the rows that claim mock data; PATCH in #18 is documented as superseded by POST upsert.

## Migration Plan

Docs-only plus frontend. No data migration. Rollback is revert; stored JSON files are unchanged.
