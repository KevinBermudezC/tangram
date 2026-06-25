## Why

Today the canvas is **read-only**: `/generate` produces a diagram, `/analyze` critiques it, and persistence stores it — but the user can't actually *change* anything. The palette cards are `draggable` yet the drop target is a no-op, and `DiagramCanvas` runs React Flow with `nodesDraggable={false}` / `nodesConnectable={false}`. Tangram is pitched as a place where you *build* an architecture and learn as you go; without direct manipulation it's a generator + viewer, not an editor.

This change turns the canvas into a real editor: drag components from the palette onto the canvas, move them, connect them, rename and delete them, and have the result persist. It's roadmap MVP item #15 (`add-diagram-editor`) and the precondition for the per-node explanation panel (#16) and a genuinely interactive tutor loop.

## What Changes

- Make `DiagramCanvas` **interactive and controlled**: React Flow driven by `useNodesState` / `useEdgesState` seeded from `diagramToFlow`, with `nodesDraggable`, `nodesConnectable`, selection, and delete enabled.
- Add `lib/flowToDiagram.ts` — the reverse of `diagramToFlow`: serialize the live React Flow graph back into a Tangram `Diagram` (preserving ids, positions, and the stashed `data.tangram` payloads).
- Add a **custom node** component (`components/editor/diagram-node.tsx`, React Flow `type: "tangram"`) with source/target handles, the component type's colour + icon, and an inline-editable label. Replaces the bare `"default"` node.
- **Drag-and-drop from the palette**: palette cards carry a `dataTransfer` payload (node type); the canvas `onDrop` computes the position via `screenToFlowPosition` and appends a new node with a client-minted id and a sensible default label.
- **Connect**: dragging handle→handle calls `onConnect`, appending a Tangram edge with a generated id.
- **Delete**: selected nodes/edges removed via React Flow's delete key + `onNodesDelete` / `onEdgesDelete`; deleting a node prunes its incident edges.
- **Rename**: double-click a node to edit its label inline.
- **Persistence of edits**: a debounced autosave serializes the graph (`flowToDiagram`) and upserts it via the existing `POST /diagrams`; the topbar's `savedLabel` reflects idle / saving / saved / error. An explicit **Save** button in the topbar flushes the pending save immediately (shares the same save path as autosave). Blank-canvas diagrams mint a client ULID + default metadata on first edit.
- Wire `/editor` (post-generate) and `/editor/[id]` (saved) to the editable canvas; the blank-canvas entry (`/editor` with no prompt) starts an empty editable draft.
- **Auto-arrange**: an in-canvas button re-lays the graph with a clean left-to-right layered layout (Dagre), client-side and on-demand; the tidied positions persist like any edit. Also widen the backend `auto_layout` column/row spacing so freshly generated diagrams aren't cramped for the larger editor node.
- **Cleaner edges**: smoothstep (right-angled) routing with arrowheads and readable label backings, so connections route around boxes instead of slicing through them.
- Update the palette helper copy (drop the "coming in add-diagram-editor" note) and enable the previously-disabled affordances.
- Add tests: `flowToDiagram` round-trip, drop-to-create, connect-to-edge, delete-prunes-edges, and the autosave serialization path (mocked).

This change does **not**:
- Add undo/redo. Tempting, but a v0 editor ships without it; it's a fast follow.
- Add an edge-properties editor (protocol / data-flow direction UI). Edges get sensible defaults; richer edge editing is a separate change.
- Auto re-layout after *every* edit. Layout only runs on demand (the Auto-arrange button); the user owns positions otherwise.
- Add copy/paste, multi-node grouping, or alignment guides.
- Change any backend route. Persistence (`POST/GET/DELETE /diagrams`) already exists and upserts by id.

## Capabilities

### New Capabilities

- `diagram-editor`: Direct manipulation of a diagram on the canvas — create nodes by dragging from the palette, move them, connect them by their handles, rename and delete them — with the edited graph serialized back to the Tangram `Diagram` schema and persisted via the existing storage routes.

### Modified Capabilities

<!-- None. Consumes the persistence routes and the diagram schema as-is. -->

## Impact

- **Code**: rewrite `components/DiagramCanvas.tsx` (controlled + interactive); new `components/editor/diagram-node.tsx`, `lib/flowToDiagram.ts`; palette gains a drag payload; `/editor` and `/editor/[id]` pages own editable state + autosave; small topbar save-status wiring; new tests.
- **Dependencies**: none — `@xyflow/react` (v12) is already installed. A tiny client-side id helper (reuse a ULID/nanoid utility or `crypto.randomUUID`).
- **Backend**: unchanged. Edits persist through the existing `POST /diagrams` upsert.
- **Unblocks**: `add-ai-explanation-panel` (#16) — clicking a node already stashes its Tangram payload; the editor makes "select a node" a first-class interaction.
- **Docs**: short "Editor" note in `frontend/README.md`; remove the palette's placeholder copy.
