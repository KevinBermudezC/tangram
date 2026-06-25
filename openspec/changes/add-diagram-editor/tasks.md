## 1. Serialization

- [x] 1.1 Add `lib/flowToDiagram.ts` — `flowToDiagram(nodes, edges, base) -> Diagram` (id/type/label/position from RF nodes; source/target/label from RF edges; carry through stashed `data.tangram` properties/ai; pull version/id/metadata/conversation from `base`)
- [x] 1.2 Drop edges referencing missing nodes; ensure unique node ids
- [x] 1.3 Add a small client id helper (`lib/ids.ts`, e.g. `newNodeId(type)` / `newEdgeId()`)
- [x] 1.4 Tests `tests/flowToDiagram.test.ts` — round-trip with `diagramToFlow` preserves ids/types/positions/edges; orphan-edge pruning

## 2. Custom node

- [x] 2.1 Add `components/editor/diagram-node.tsx` (RF `type: "tangram"`) — type colour/icon via `nodeColors`/`NodeIcon`, label, source + target `<Handle>`s
- [x] 2.2 Inline label editing on double-click (local state → commit on blur/Enter)
- [x] 2.3 Point `diagramToFlow` at `type: "tangram"`

## 3. Interactive canvas

- [x] 3.1 Rewrite `components/DiagramCanvas.tsx` as controlled (`useNodesState`/`useEdgesState` seeded from `diagramToFlow`), `nodeTypes={{ tangram }}`, `nodesDraggable`/`nodesConnectable`/selectable enabled
- [x] 3.2 Seed once per diagram **id**; don't clobber local edits on background refetch
- [x] 3.3 `onConnect` → append edge (reject self-loops, dedupe by source+target)
- [x] 3.4 `onNodesDelete`/`onEdgesDelete` → prune incident edges; enable delete key
- [x] 3.5 Drag-and-drop: `onDragOver` (preventDefault) + `onDrop` → `screenToFlowPosition` → append typed node with client id + default label
- [x] 3.6 Expose changes upward (`onChange(nodes, edges)` or ref) for autosave

## 4. Palette drag payload

- [x] 4.1 `components/editor/palette.tsx` — `onDragStart` sets `dataTransfer` (`application/tangram-node` = type)
- [x] 4.2 Remove the "drag-to-canvas coming" placeholder copy

## 5. Pages + autosave

- [x] 5.1 `app/editor/page.tsx` — own editable state; blank canvas starts an empty editable draft; mint client ULID + default metadata on first node
- [x] 5.2 `app/editor/[id]/page.tsx` — load saved diagram into the editable canvas
- [x] 5.3 Debounced autosave (~800ms idle) → `flowToDiagram` → `saveDiagram` (upsert); ignore stale responses
- [x] 5.4 Explicit topbar **Save** button that flushes the pending save immediately (shares the save path); disabled when there are no unsaved changes
- [x] 5.5 Topbar `savedLabel`: editing… / saving… / saved · just now / save failed
- [x] 5.6 Best-effort flush on unmount/navigation

## 6. Tests

- [x] 6.1 Pure graph helpers extracted to `lib/editor-graph.ts`; `tests/editor-graph.test.ts` — drop creates a typed node, connect creates an edge, self-loop + duplicate rejected. Delete→prune is covered by the orphan-edge case in `tests/flowToDiagram.test.ts` (React Flow interactions aren't jsdom-friendly, so the logic is unit-tested pure).
- [x] 6.2 `tests/useDiagramEditor.test.tsx` — the seed report doesn't persist; an edit + `saveNow` upserts the serialized graph (mocked `saveDiagram`)

## 7. Layout polish

- [x] 7a.1 Widen backend `auto_layout` column/row spacing so generated diagrams aren't cramped for the larger editor node (`backend/app/services/generation/layout.py`)
- [x] 7a.2 Cleaner edges: smoothstep + arrowheads + readable label backing (`DiagramCanvas` `defaultEdgeOptions`)
- [x] 7a.3 Auto-arrange: `lib/autoLayout.ts` (Dagre, LR layered) + an in-canvas Panel button; tidied positions persist via autosave
- [x] 7a.4 Tests `tests/autoLayout.test.ts` (positions assigned, left-to-right chain, identity preserved); backend `test_layout.py` made spacing-relative

## 8. Docs + verification

- [x] 7.1 Short "Editor" note in `frontend/README.md`
- [x] 7.2 `pnpm typecheck` clean
- [x] 7.3 `pnpm lint` clean
- [x] 7.4 `pnpm test` clean
- [x] 7.5 `openspec validate add-diagram-editor --strict`
