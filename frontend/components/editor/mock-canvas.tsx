"use client";

import { Lock, Maximize2, Minus, MousePointer2, Plus } from "lucide-react";

import type { NodeType } from "@/types/tangram";
import { nodeColors } from "@/lib/node-style";

interface MockCanvasProps {
  /**
   * Render the canned 5-node "Delivery App" example.
   *
   * Off by default — `/editor` opened directly (Blank canvas, future
   * `?id=…` load) starts truly empty so the user sees what a blank canvas
   * looks like. Turn this on when a generated diagram is about to render
   * (placeholder behind the loading overlay) or for marketing screenshots.
   */
  demo?: boolean;
}

/**
 * Static-shaped canvas used until the real React Flow editor lands.
 *
 * The real implementation will replace this with `<ReactFlow ...>` driven by
 * the editor's state. The chrome (controls, minimap, dot grid, node card
 * style) lives in this component intentionally so the visual upgrade is
 * already done by the time the editor logic is wired in.
 */
export function MockCanvas({ demo = false }: MockCanvasProps) {
  return (
    <div className="relative flex-1 overflow-hidden bg-canvas">
      <svg
        viewBox="0 0 900 540"
        preserveAspectRatio="xMidYMid meet"
        className="block h-full w-full"
        aria-hidden
      >
        <defs>
          <pattern id="dotgrid" width="22" height="22" patternUnits="userSpaceOnUse">
            <circle cx="1" cy="1" r="1" fill="var(--color-line-strong)" />
          </pattern>
          <marker
            id="edge-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M0 0 L10 5 L0 10 z" fill="var(--color-ink-faint)" />
          </marker>
        </defs>
        <rect width="900" height="540" fill="url(#dotgrid)" />

        {demo && (
          <>
            <g>
              <Edge d="M210 270 H320" dashed label="browse / order" labelX={265} labelY={262} />
              <Edge d="M390 230 V160" dashed label="sign in" labelX={410} labelY={200} anchor="start" />
              <Edge d="M460 130 H580" dashed label="identity" labelX={520} labelY={122} />
              <Edge
                d="M460 270 C540 270 540 130 580 130"
                dashed
                label="read / write"
                labelX={540}
                labelY={208}
                anchor="start"
              />
              <Edge
                d="M460 270 C540 270 540 410 580 410"
                label="store images"
                labelX={540}
                labelY={346}
                anchor="start"
              />
            </g>
            <NodeCard
              type="frontend"
              x={70}
              y={230}
              label="Customer"
              sub="Web (Next.js)"
              selected
            />
            <NodeCard type="backend" x={320} y={230} label="Orders API" sub="FastAPI + Pydantic" />
            <NodeCard type="auth" x={320} y={90} label="Auth Service" sub="OAuth2 / JWT" />
            <NodeCard type="database" x={580} y={90} label="orders_db" sub="PostgreSQL" />
            <NodeCard type="storage" x={580} y={370} label="assets" sub="S3-compatible" />
          </>
        )}
      </svg>

      {!demo && <EmptyCanvasHint />}

      <CanvasControls />
      <MiniMap demo={demo} />
    </div>
  );
}

function EmptyCanvasHint() {
  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
      <div className="flex max-w-sm flex-col items-center gap-2 text-center">
        <span
          aria-hidden
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-dashed border-line-strong text-ink-faint"
        >
          <MousePointer2 size={16} />
        </span>
        <p className="font-serif text-[18px] font-medium tracking-wide text-ink-strong">
          Empty canvas
        </p>
        <p className="text-[12.5px] leading-relaxed text-ink-muted">
          Drag a component from the palette to start. Or open the AI panel
          and describe what you want — it'll sketch a starting point.
        </p>
      </div>
    </div>
  );
}

interface NodeCardProps {
  type: NodeType;
  x: number;
  y: number;
  label: string;
  sub: string;
  selected?: boolean;
}

function NodeCard({ type, x, y, label, sub, selected }: NodeCardProps) {
  const colors = nodeColors[type];
  return (
    <g transform={`translate(${x},${y})`}>
      <rect
        width="140"
        height="80"
        rx="10"
        fill="var(--color-card)"
        stroke={colors.ink}
        strokeWidth={selected ? 2 : 1}
        style={{
          filter: selected
            ? "drop-shadow(0 3px 8px rgba(201,99,58,0.18))"
            : "drop-shadow(0 1px 2px rgba(26,26,26,0.06))",
        }}
      />
      <text
        x={46}
        y={28}
        style={{
          font: "9px var(--font-mono)",
          letterSpacing: "0.16em",
          fill: colors.ink,
          textTransform: "uppercase",
        }}
      >
        {type.toUpperCase().replace("_", " ")}
      </text>
      <text
        x={46}
        y={46}
        style={{
          font: "600 13px var(--font-sans)",
          fill: "var(--color-ink-strong)",
        }}
      >
        {label}
      </text>
      <text
        x={14}
        y={68}
        style={{ font: "10px var(--font-mono)", fill: "var(--color-ink-muted)" }}
      >
        {sub}
      </text>
      {/* Handles */}
      {[
        { cx: 0, cy: 40 },
        { cx: 140, cy: 40 },
        { cx: 70, cy: 0 },
        { cx: 70, cy: 80 },
      ].map((h, i) => (
        <circle
          key={i}
          cx={h.cx}
          cy={h.cy}
          r={4}
          fill={selected ? "var(--color-accent)" : "var(--color-card)"}
          stroke={selected ? "var(--color-accent)" : "var(--color-ink-muted)"}
          strokeWidth={1.5}
        />
      ))}
    </g>
  );
}

interface EdgeProps {
  d: string;
  dashed?: boolean;
  label: string;
  labelX: number;
  labelY: number;
  anchor?: "start" | "middle" | "end";
}

function Edge({ d, dashed, label, labelX, labelY, anchor = "middle" }: EdgeProps) {
  return (
    <>
      <path
        d={d}
        stroke="var(--color-ink-faint)"
        strokeWidth={1.5}
        fill="none"
        strokeDasharray={dashed ? "4 3" : undefined}
        markerEnd="url(#edge-arrow)"
      />
      <text
        x={labelX}
        y={labelY}
        textAnchor={anchor}
        style={{
          font: "italic 11px var(--font-sans)",
          fill: "var(--color-ink-muted)",
          paintOrder: "stroke",
          stroke: "var(--color-canvas)",
          strokeWidth: 3,
        }}
      >
        {label}
      </text>
    </>
  );
}

function CanvasControls() {
  return (
    <div className="absolute bottom-4 left-4 flex flex-col gap-0.5 rounded-[var(--radius)] border border-line bg-card p-1 shadow-sm">
      {[Plus, Minus, Maximize2, Lock].map((Icon, i) => (
        <button
          key={i}
          type="button"
          className="inline-flex h-7 w-7 items-center justify-center rounded-md text-ink-muted hover:bg-sidebar hover:text-ink-strong"
        >
          <Icon size={13} />
        </button>
      ))}
    </div>
  );
}

function MiniMap({ demo }: { demo: boolean }) {
  const dots: { x: number; y: number; type: NodeType }[] = demo
    ? [
        { x: 12, y: 50, type: "frontend" },
        { x: 38, y: 50, type: "backend" },
        { x: 38, y: 22, type: "auth" },
        { x: 68, y: 22, type: "database" },
        { x: 68, y: 78, type: "storage" },
      ]
    : [];
  return (
    <div className="absolute bottom-4 right-4 h-[110px] w-[160px] overflow-hidden rounded-[var(--radius)] border border-line bg-card shadow-sm">
      {dots.map((d, i) => (
        <span
          key={i}
          aria-hidden
          className="absolute h-2.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-sm"
          style={{
            left: `${d.x}%`,
            top: `${d.y}%`,
            backgroundColor: nodeColors[d.type].ink,
          }}
        />
      ))}
      {demo && (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-x-[8%] inset-y-[14%] rounded border-[1.5px] border-accent/55"
        />
      )}
    </div>
  );
}
