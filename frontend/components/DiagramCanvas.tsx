"use client";

import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { useMemo } from "react";

import { diagramToFlow } from "@/lib/diagramToFlow";
import type { Diagram } from "@/types/tangram";

interface DiagramCanvasProps {
  diagram: Diagram;
}

/**
 * Read-only React Flow canvas. Drag, connect, and edit are disabled.
 * Pan + zoom + minimap are enabled — they're read interactions.
 */
export function DiagramCanvas({ diagram }: DiagramCanvasProps) {
  const { nodes, edges } = useMemo(() => diagramToFlow(diagram), [diagram]);

  return (
    <div className="h-full w-full" role="region" aria-label="Diagram canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={true}
        edgesFocusable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={20} size={1} />
        <Controls showInteractive={false} />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
