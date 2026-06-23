"use client";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Connection,
  type Edge,
  type Node,
  type NodeTypes,
} from "@xyflow/react";
// React Flow's stylesheet is imported once globally in `app/globals.css`.

import { useCallback, useEffect, useRef } from "react";

import { DiagramNode } from "@/components/editor/diagram-node";
import { diagramToFlow } from "@/lib/diagramToFlow";
import { connectEdge, createNode } from "@/lib/editor-graph";
import type { Diagram, NodeType } from "@/types/tangram";

const NODE_TYPES: NodeTypes = { tangram: DiagramNode };
const DND_MIME = "application/tangram-node";

export interface DiagramCanvasProps {
  diagram: Diagram;
  /** Read-only renders a static, non-interactive canvas (no edits). */
  readOnly?: boolean;
  /** Called with the live graph after every mutation (for autosave). */
  onChange?: (nodes: Node[], edges: Edge[]) => void;
}

/**
 * Interactive React Flow canvas. Drag to move, drag a palette card to create,
 * connect handle→handle, double-click to rename, Delete to remove. The live
 * graph is reported via `onChange` so the page can serialize + persist it.
 *
 * Wrapped in ReactFlowProvider so the custom node and the drop handler can use
 * `useReactFlow` (label edits, `screenToFlowPosition`).
 */
export function DiagramCanvas(props: DiagramCanvasProps) {
  return (
    <ReactFlowProvider>
      <DiagramCanvasInner {...props} />
    </ReactFlowProvider>
  );
}

function DiagramCanvasInner({ diagram, readOnly = false, onChange }: DiagramCanvasProps) {
  const initial = diagramToFlow(diagram);
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);
  const { screenToFlowPosition } = useReactFlow();

  // Re-seed only when a *different* diagram is opened, so a background refetch
  // of the same diagram never clobbers in-progress edits.
  const seededId = useRef(diagram.id);
  useEffect(() => {
    if (seededId.current === diagram.id) return;
    seededId.current = diagram.id;
    const next = diagramToFlow(diagram);
    setNodes(next.nodes);
    setEdges(next.edges);
  }, [diagram, setNodes, setEdges]);

  // Report the live graph upward for autosave. Skip in read-only mode.
  useEffect(() => {
    if (readOnly) return;
    onChange?.(nodes, edges);
  }, [nodes, edges, readOnly, onChange]);

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => connectEdge(eds, connection));
    },
    [setEdges],
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const type = event.dataTransfer.getData(DND_MIME) as NodeType;
      if (!type) return;
      const position = screenToFlowPosition({ x: event.clientX, y: event.clientY });
      setNodes((nds) => nds.concat(createNode(type, position)));
    },
    [screenToFlowPosition, setNodes],
  );

  return (
    <div className="h-full w-full" role="region" aria-label="Diagram canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        nodeTypes={NODE_TYPES}
        fitView
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable
        deleteKeyCode={readOnly ? null : ["Backspace", "Delete"]}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
