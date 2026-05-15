import type { MockDiagram } from "@/lib/mock-data";
import { nodeColors } from "@/lib/node-style";

interface DiagramThumbProps {
  diagram: MockDiagram;
}

/**
 * Hand-rendered SVG thumbnail of a diagram. Mirrors the React Flow output
 * (rounded category-colored cards + dashed-or-solid edges) at 200×120.
 *
 * Drafts skip the dot grid for a cleaner empty feel.
 */
export function DiagramThumb({ diagram }: DiagramThumbProps) {
  const isDraft = diagram.source === "draft";
  return (
    <svg
      viewBox="0 0 200 120"
      className="block h-full w-full"
      aria-hidden
    >
      <defs>
        <pattern
          id={`grid-${diagram.id}`}
          width="10"
          height="10"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="0.5" cy="0.5" r="0.5" fill="#E7E1D5" />
        </pattern>
      </defs>
      <rect width="200" height="120" fill="#FDFBF5" />
      {!isDraft && (
        <rect width="200" height="120" fill={`url(#grid-${diagram.id})`} />
      )}

      {diagram.thumb.edges.map((edge, i) => (
        <line
          key={i}
          x1={edge.from.x}
          y1={edge.from.y}
          x2={edge.to.x}
          y2={edge.to.y}
          stroke="#9A8F80"
          strokeWidth={1.2}
          strokeDasharray={edge.dashed ? "3 2" : undefined}
          fill="none"
        />
      ))}

      {diagram.thumb.nodes.map((node, i) => (
        <rect
          key={i}
          x={node.x}
          y={node.y}
          width={node.w}
          height={node.h}
          rx={5}
          fill={isDraft ? "none" : nodeColors[node.type].fill}
          stroke={nodeColors[node.type].ink}
          strokeWidth={1}
          strokeDasharray={isDraft ? "3 3" : undefined}
        />
      ))}
    </svg>
  );
}
