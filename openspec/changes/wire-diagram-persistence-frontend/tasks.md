## 1. View model

- [x] 1.1 Add a list view-model type (not named `MockDiagram`, not imported from `mock-data.ts`) plus a `DiagramSummary` → list-item mapper; verify a unit test covers id/name/counts/`updatedLabel`/thumb and that `source` defaults to `"ai"`
- [x] 1.2 Point `useDiagrams` at that mapper and type; set a low retry count; verify hook tests: live list from `listDiagrams`, empty array, thrown error (no mock records)
- [x] 1.3 Switch `diagram-card.tsx` and `diagram-thumb.tsx` to the new type; verify typecheck and existing card/thumb rendering still uses `id`, `name`, `source`, `thumb`

## 2. Empty / error UI

- [x] 2.1 Library: distinct loading, empty-store, filter-miss, and error states; verify page tests for empty vs error vs a populated list linking to `/editor/{id}`
- [x] 2.2 Rail Recent: distinct loading, empty, and error states (no fake recents); verify rail tests for empty vs error vs links to `/editor/{id}`
- [x] 2.3 Confirm `/editor/[id]` still loads via `useDiagram` and shows not-found vs generic load error (existing overlays); add a focused test if none covers those two copy paths

## 3. Persistence loop (verify, don't redo)

- [x] 3.1 Confirm generate-on-success still `POST`s via `useSaveDiagram` and editor autosave still upserts; extend tests only if a call site still skips the API
- [x] 3.2 Strip leftover `MockDiagram` imports from saved-diagram paths; leave `templates` / `componentCatalog` in `mock-data.ts`; verify grep of `MockDiagram` is only docs or gone

## 4. Docs + archive

- [x] 4.1 Update `ROADMAP.md` item #13 and the Library/Recent + `/editor/[id]` follow-up rows (and the matching good-first-issue bullets) so they match reality
- [x] 4.2 Sync `add-diagram-persistence-routes` delta spec into `openspec/specs/diagram-persistence-routes/` and move the change to `openspec/changes/archive/YYYY-MM-DD-add-diagram-persistence-routes/`
- [x] 4.3 Refresh `frontend/README.md` mock-data / hooks wording if it still claims mock recent diagrams

## 5. Verify

- [x] 5.1 `pnpm lint`, `pnpm typecheck`, `pnpm test` from `frontend/` all green
- [x] 5.2 `openspec validate wire-diagram-persistence-frontend --strict` passes
