"use client";

import { Background, Controls, MiniMap, ReactFlow } from "@xyflow/react";
// React Flow's stylesheet is imported once globally in `app/globals.css`
// (Next.js requires global CSS imports to come from the root layout's
// import graph). Importing it here too would duplicate the rules and
// is rejected by Next during build.

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
