## 1. Serialization

- [ ] 1.1 Add `lib/flowToDiagram.ts` — `flowToDiagram(nodes, edges, base) -> Diagram` (id/type/label/position from RF nodes; source/target/label from RF edges; carry through stashed `data.tangram` properties/ai; pull version/id/metadata/conversation from `base`)
- [ ] 1.2 Drop edges referencing missing nodes; ensure unique node ids
- [ ] 1.3 Add a small client id helper (`lib/ids.ts`, e.g. `newNodeId(type)` / `newEdgeId()`)
- [ ] 1.4 Tests `tests/flowToDiagram.test.ts` — round-trip with `diagramToFlow` preserves ids/types/positions/edges; orphan-edge pruning

## 2. Custom node

- [ ] 2.1 Add `components/editor/diagram-node.tsx` (RF `type: "tangram"`) — type colour/icon via `nodeColors`/`NodeIcon`, label, source + target `<Handle>`s
- [ ] 2.2 Inline label editing on double-click (local state → commit on blur/Enter)
- [ ] 2.3 Point `diagramToFlow` at `type: "tangram"`

## 3. Interactive canvas

- [ ] 3.1 Rewrite `components/DiagramCanvas.tsx` as controlled (`useNodesState`/`useEdgesState` seeded from `diagramToFlow`), `nodeTypes={{ tangram }}`, `nodesDraggable`/`nodesConnectable`/selectable enabled
- [ ] 3.2 Seed once per diagram **id**; don't clobber local edits on background refetch
- [ ] 3.3 `onConnect` → append edge (reject self-loops, dedupe by source+target)
- [ ] 3.4 `onNodesDelete`/`onEdgesDelete` → prune incident edges; enable delete key
- [ ] 3.5 Drag-and-drop: `onDragOver` (preventDefault) + `onDrop` → `screenToFlowPosition` → append typed node with client id + default label
- [ ] 3.6 Expose changes upward (`onChange(nodes, edges)` or ref) for autosave

## 4. Palette drag payload

- [ ] 4.1 `components/editor/palette.tsx` — `onDragStart` sets `dataTransfer` (`application/tangram-node` = type)
- [ ] 4.2 Remove the "drag-to-canvas coming" placeholder copy

## 5. Pages + autosave

- [ ] 5.1 `app/editor/page.tsx` — own editable state; blank canvas starts an empty editable draft; mint client ULID + default metadata on first node
- [ ] 5.2 `app/editor/[id]/page.tsx` — load saved diagram into the editable canvas
- [ ] 5.3 Debounced autosave (~800ms idle) → `flowToDiagram` → `saveDiagram` (upsert); ignore stale responses
- [ ] 5.4 Explicit topbar **Save** button that flushes the pending save immediately (shares the save path); disabled when there are no unsaved changes
- [ ] 5.5 Topbar `savedLabel`: editing… / saving… / saved · just now / save failed
- [ ] 5.6 Best-effort flush on unmount/navigation

## 6. Tests

- [ ] 6.1 `tests/diagram-editor.test.tsx` — drop creates a typed node; connect creates an edge; delete prunes incident edges; self-loop rejected
- [ ] 6.2 Autosave path: an edit triggers a debounced `saveDiagram` call (mocked), with the serialized graph

## 7. Docs + verification

- [ ] 7.1 Short "Editor" note in `frontend/README.md`
- [ ] 7.2 `pnpm typecheck` clean
- [ ] 7.3 `pnpm lint` clean
- [ ] 7.4 `pnpm test` clean
- [ ] 7.5 `openspec validate add-diagram-editor --strict`
