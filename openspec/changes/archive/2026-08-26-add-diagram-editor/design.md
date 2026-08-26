## Context

The read-only canvas already proves the render path: `diagramToFlow(diagram)` → `<ReactFlow>` with pan/zoom/minimap. This change adds the write path. The pieces that exist and constrain the design:

- **React Flow v12** (`@xyflow/react@^12`) is installed and styled (its CSS is imported globally; `.react-flow__node-default` is themed).
- `diagramToFlow` is one-way and already stashes the original Tangram node/edge in `data.tangram` and the type in `data.tangramType`.
- The editor pages hold the diagram as **server state** (React Query: `useGenerate` data, `useDiagram(id)` query). Editing needs **local** state that starts from that server state and diverges.
- Persistence is filesystem-backed and **upserts by `diagram.id`** via `POST /diagrams` (`saveDiagram`). There is no separate update route; re-POSTing the same id overwrites.
- Node ids in the schema are free-form strings (the generator uses whatever the LLM returned; the backend only checks uniqueness + that edges reference existing nodes).

## Goals / Non-Goals

**Goals**
- Direct manipulation: create (drag from palette), move, connect, rename, delete.
- A controlled React Flow graph that round-trips losslessly to/from the Tangram `Diagram`.
- A custom node that matches the Tangram visual language and exposes connection handles.
- Edits persist automatically (debounced) through the existing storage route.
- Works for three entry states: post-generate (`/editor?prompt=`), open-saved (`/editor/[id]`), and blank (`/editor`).
- Tests that don't need a backend.

**Non-Goals**
- Undo/redo, copy/paste, alignment guides, grouping — fast follows.
- Edge-properties UI (protocol, data-flow direction). Defaults only.
- Server-side re-layout after manual edits.
- Realtime collaboration.

## Decisions

### Controlled React Flow with `useNodesState` / `useEdgesState`

`DiagramCanvas` becomes controlled: it seeds `useNodesState(initialNodes)` / `useEdgesState(initialEdges)` from `diagramToFlow(diagram)` and owns the live graph. It exposes changes upward through an `onChange(nodes, edges)` callback (or the page reads via a ref) so the page can serialize + autosave.

**Why**: React Flow's interactive features (drag, connect, delete) require controlled state via its hooks. The previous read-only version passed static arrays.

**Seeding**: seed once from the initial diagram; subsequent prop changes for the *same* diagram id don't clobber local edits. Re-seed only when the diagram **id** changes (opening a different diagram). This avoids server-state refetches wiping in-progress edits.

**Alternatives**: a global store (Zustand) for the graph (rejected for v0 — local component state + a serialize callback is enough; revisit if the explanation panel needs shared access).

### A custom `tangram` node type

Replace `"default"` with a `tangram` node (`nodeTypes={{ tangram: DiagramNode }}`). It renders the type's colour/icon (from `nodeColors` / `NodeIcon`), the label, and explicit `<Handle type="source">` / `<Handle type="target">`. `diagramToFlow` sets `type: "tangram"`.

**Why**: connecting requires visible handles; the bare default node has poor handles and no theming hook. A custom node also gives the per-node explanation panel (#16) a place to live later.

### Reverse converter `flowToDiagram`

`flowToDiagram(nodes, edges, base)` rebuilds a `Diagram`: each RF node → Tangram node (id, `data.tangramType` → type, `data.label` → label, `position`, preserving `data.tangram.properties`/`ai` when present); each RF edge → Tangram edge (id, source, target, label, preserving stashed properties). `base` supplies version/id/metadata/conversation that aren't represented on the canvas.

**Why**: persistence and analysis both speak `Diagram`, not React Flow. Keeping the converter pure makes it unit-testable without a DOM.

**Edge integrity**: drop edges whose source/target no longer exist (defensive; deletes should already prune).

### New ids are client-minted

New nodes (from a palette drop) and new edges (from a connect) get client-generated ids — a short ULID/`crypto.randomUUID()` slice prefixed by type (e.g. `frontend-7f3a`). The backend accepts any unique string.

**Why**: the canvas can't wait for a server round-trip to place a node. Ids only need to be unique within the diagram.

### Drag-and-drop via HTML5 DnD + `screenToFlowPosition`

Palette cards set `e.dataTransfer.setData("application/tangram-node", type)` on `dragStart`. The canvas wrapper handles `onDragOver` (preventDefault) and `onDrop`: read the type, compute the flow position with `screenToFlowPosition({x: e.clientX, y: e.clientY})`, append a node.

**Why**: it's the React Flow-documented pattern and needs no extra deps. The palette is already `draggable`.

### Autosave (debounced) plus an explicit Save button

On graph change, debounce (~800ms idle) → `flowToDiagram` → `saveDiagram` (`POST /diagrams`, upsert by id). The topbar `savedLabel` reflects `editing… / saving… / saved · just now / save failed`. A blank-canvas diagram mints a client ULID + default metadata (`name: "Untitled"`, timestamps) on first edit so it has an id to upsert under, then behaves like any saved diagram (and could route to `/editor/[id]`).

Alongside autosave, the topbar keeps an explicit **Save** button that **flushes immediately** (cancels the pending debounce and writes now). It's disabled when there are no unsaved changes and shows the same in-flight/error states. Autosave and the button share one save function, so they can't diverge.

**Why**: autosave means the editor never silently forgets work (matches the "diagrams live as JSON" promise); the manual Save gives users explicit control and a clear "it's saved now" affordance for those who want it. Debouncing avoids a write per pixel of drag.

**Trade-off**: no optimistic-vs-server reconciliation in v0 — last write wins, single-user, local filesystem. Fine for the MVP's scope.

**Alternatives**: a real `PUT /diagrams/{id}` (unnecessary — POST already upserts).

### Delete prunes incident edges

`onNodesDelete` removes edges touching the deleted nodes; React Flow's default delete-key is enabled (`deleteKeyCode`). Deleting an edge just removes the edge.

## Risks / Trade-offs

- **Risk**: server refetch (React Query) overwrites local edits. → **Mitigation**: seed local state once per diagram id; don't reset on background refetch. Consider disabling refetch-on-focus for the open-diagram query while editing.
- **Risk**: autosave races the user (save fires mid-drag). → **Mitigation**: debounce on idle; serialize only the latest snapshot; ignore stale responses.
- **Risk**: a brand-new blank diagram has no id, so the first autosave can't upsert. → **Mitigation**: mint the id + metadata the moment the canvas becomes non-empty.
- **Risk**: connecting a node to itself or duplicate edges. → **Mitigation**: reject self-loops in `onConnect`; dedupe by (source,target).
- **Trade-off**: no undo/redo means a misdelete is permanent until re-add. Accepted for v0; flagged as the top fast-follow.

## Migration Plan

No data migration. Existing saved diagrams already match the schema and load unchanged; they simply become editable. Rollback = revert (canvas returns to read-only).

## Open Questions

- **Undo/redo in v0 or immediately after?** Leaning "immediately after" as its own small change, since a history stack touches every mutation path.
- **Should blank-canvas drafts persist immediately, or only once the user adds a node?** Proposed: only once non-empty, to avoid a library full of empty "Untitled" drafts.
- **Edge defaults**: direction arrow + a neutral style for v0; do we surface `dataFlow` (uni/bi) on double-click later? Deferred to an edge-editing change.
- **Autosave vs. navigation**: flush a pending save on route change / unmount (best-effort `beforeunload`)? Worth doing if cheap.
