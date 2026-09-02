"use client";

import {
  Background,
  ConnectionLineType,
  Controls,
  MarkerType,
  MiniMap,
  Panel,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
  type Connection,
  type DefaultEdgeOptions,
  type Edge,
  type Node,
  type NodeTypes,
} from "@xyflow/react";
// React Flow's stylesheet is imported once globally in `app/globals.css`.

import { Wand2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useCallback, useEffect, useRef, useState } from "react";

import { DiagramNode } from "@/components/editor/diagram-node";
import { autoLayout } from "@/lib/autoLayout";
import { diagramToFlow } from "@/lib/diagramToFlow";
import { connectEdge, createNode } from "@/lib/editor-graph";
import { flowColorMode } from "@/lib/theme";
import type { Diagram, NodeType } from "@/types/tangram";

const NODE_TYPES: NodeTypes = { tangram: DiagramNode };
const DND_MIME = "application/tangram-node";

// Smooth right-angled edges with an arrowhead route around boxes far more
// cleanly than straight diagonals, and the label gets a readable backing.
// Stroke/marker colors are CSS variables so they follow `.dark` with the rest
// of the editor (hardcoded #9a958c / #b9b2a6 stayed warm-grey in dark mode).
const EDGE_OPTIONS: DefaultEdgeOptions = {
  type: "smoothstep",
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 16,
    height: 16,
    color: "var(--color-ink-muted)",
  },
  style: { stroke: "var(--color-ink-faint)", strokeWidth: 1.5 },
  labelStyle: { fill: "var(--color-ink-muted)", fontSize: 11, fontWeight: 500 },
  labelBgStyle: { fill: "var(--color-page)", fillOpacity: 0.92 },
  labelBgPadding: [4, 2],
  labelBgBorderRadius: 4,
};

export interface DiagramCanvasProps {
  diagram: Diagram;
  /** Read-only renders a static, non-interactive canvas (no edits). */
  readOnly?: boolean;
  /** Called with the live graph after every mutation (for autosave). */
  onChange?: (nodes: Node[], edges: Edge[]) => void;
  /** Called when the selected node changes (or selection is cleared). */
  onSelectNode?: (node: { id: string; name: string; type: string } | undefined) => void;
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

function DiagramCanvasInner({
  diagram,
  readOnly = false,
  onChange,
  onSelectNode,
}: DiagramCanvasProps) {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => {
    setMounted(true);
  }, []);
  // First paint matches SSR (`react-flow light`). After mount, follow
  // next-themes — not a second OS listener, and not the unresolved client value.
  const colorMode = flowColorMode(resolvedTheme, mounted);
  const initial = diagramToFlow(diagram);
  const [nodes, setNodes, onNodesChange] = useNodesState(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);
  const { screenToFlowPosition, fitView } = useReactFlow();

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

  const onTidy = useCallback(() => {
    setNodes((nds) => autoLayout(nds, edges));
    // Re-fit after the new positions commit.
    requestAnimationFrame(() => fitView({ padding: 0.2, duration: 300 }));
  }, [setNodes, edges, fitView]);

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
        onSelectionChange={({ nodes: selected }) => {
          const node = selected[0];
          if (!node) {
            onSelectNode?.(undefined);
            return;
          }
          const data = (node.data ?? {}) as { label?: string; tangramType?: string };
          onSelectNode?.({
            id: node.id,
            name: String(data.label ?? node.id),
            type: String(data.tangramType ?? ""),
          });
        }}
        nodeTypes={NODE_TYPES}
        defaultEdgeOptions={EDGE_OPTIONS}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable
        deleteKeyCode={readOnly ? null : ["Backspace", "Delete"]}
        proOptions={{ hideAttribution: true }}
        colorMode={colorMode}
        defaultMarkerColor="var(--color-ink-muted)"
      >
        {!readOnly && (
          <Panel position="top-right">
            <button
              type="button"
              onClick={onTidy}
              className="inline-flex items-center gap-1.5 rounded-[var(--radius)] border border-line bg-card px-2.5 py-1.5 text-[12.5px] font-medium text-ink-body shadow-sm transition-colors hover:border-ink-muted hover:text-ink-strong"
              title="Auto-arrange the diagram"
            >
              <Wand2 size={13} />
              Auto-arrange
            </button>
          </Panel>
        )}
        <Background
          gap={20}
          size={1}
          color="var(--color-line-strong)"
          bgColor="var(--color-canvas)"
        />
        <Controls showInteractive={false} />
        <MiniMap
          pannable
          zoomable
          bgColor="var(--color-card)"
          maskColor="color-mix(in srgb, var(--color-page) 75%, transparent)"
          nodeColor="var(--color-line-strong)"
          nodeStrokeColor="var(--color-line)"
        />
      </ReactFlow>
    </div>
  );
}
