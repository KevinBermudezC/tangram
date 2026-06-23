"use client";

import {
  Handle,
  Position,
  useReactFlow,
  type NodeProps,
} from "@xyflow/react";
import { useEffect, useRef, useState } from "react";

import { NodeIcon } from "@/components/node-icon";
import { nodeColors } from "@/lib/node-style";
import { cn } from "@/lib/utils";
import type { NodeType } from "@/types/tangram";

/**
 * Custom React Flow node for Tangram diagrams. Shows the component type's
 * colour + icon and the label, with left (target) / right (source) handles so
 * the graph reads left-to-right. Double-click the label to rename inline.
 */
export function DiagramNode({ id, data, selected }: NodeProps) {
  const record = (data ?? {}) as Record<string, unknown>;
  const label = (record.label as string) ?? "";
  const type = ((record.tangramType as NodeType) ?? "backend") as NodeType;
  const colors = nodeColors[type] ?? nodeColors.backend;

  const { updateNodeData } = useReactFlow();
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(label);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  function startEdit() {
    setDraft(label);
    setEditing(true);
  }

  function commit() {
    const next = draft.trim() || label;
    updateNodeData(id, { label: next });
    setEditing(false);
  }

  return (
    <div
      className={cn(
        "flex min-w-[140px] max-w-[220px] items-center gap-2.5 rounded-[var(--radius)] border bg-card px-3 py-2 shadow-[0_1px_2px_rgba(20,20,20,0.05)] transition-shadow",
        selected
          ? "border-accent shadow-[0_0_0_2px_var(--color-accent-tint),0_1px_3px_rgba(20,20,20,0.1)]"
          : "border-line-strong",
      )}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !border !border-line-strong !bg-card"
      />

      <span
        aria-hidden
        className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-[7px] border"
        style={{
          backgroundColor: colors.fill,
          color: colors.ink,
          borderColor: colors.ink,
        }}
      >
        <NodeIcon type={type} size={14} />
      </span>

      {editing ? (
        <input
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => {
            if (e.key === "Enter") commit();
            if (e.key === "Escape") setEditing(false);
          }}
          className="min-w-0 flex-1 rounded-sm border border-line bg-page px-1 py-0.5 text-[13px] font-medium text-ink-strong focus:outline-none focus:ring-1 focus:ring-accent"
        />
      ) : (
        <span
          onDoubleClick={startEdit}
          title="Double-click to rename"
          className="min-w-0 flex-1 truncate text-[13px] font-medium text-ink-strong"
        >
          {label || <span className="text-ink-faint">Untitled</span>}
        </span>
      )}

      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !border !border-line-strong !bg-card"
      />
    </div>
  );
}
