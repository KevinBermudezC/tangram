"use client";

import { Brand } from "@/components/brand";
import { NodeIcon } from "@/components/node-icon";
import { componentCatalog } from "@/lib/mock-data";
import { nodeColors } from "@/lib/node-style";

/**
 * Left rail in the editor — draggable component palette.
 *
 * Drag-to-canvas isn't wired up yet (lives in `add-diagram-editor`); these
 * cards are visually draggable (`draggable=true`) so the affordance reads
 * correctly even though the drop target is a no-op.
 */
export function EditorPalette() {
  return (
    <aside className="flex min-h-0 flex-col gap-4 border-r border-line bg-sidebar px-3.5 py-4">
      <Brand className="px-1" />

      <div className="flex flex-col gap-2.5">
        <p className="px-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-ink-faint">
          Components
        </p>

        <ul className="flex flex-col gap-1">
          {componentCatalog.map((c) => {
            const colors = nodeColors[c.type];
            return (
              <li key={c.type}>
                <button
                  type="button"
                  draggable
                  className="flex w-full cursor-grab items-center gap-2.5 rounded-[var(--radius)] border border-line bg-card px-2.5 py-2 text-left transition-all hover:border-ink-muted hover:shadow-sm active:cursor-grabbing active:scale-[0.99]"
                >
                  <span
                    className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-[7px] border"
                    style={{
                      backgroundColor: colors.fill,
                      color: colors.ink,
                      borderColor: colors.ink,
                    }}
                  >
                    <NodeIcon type={c.type} size={14} />
                  </span>
                  <div className="flex min-w-0 flex-col">
                    <span className="text-[13.5px] font-semibold text-ink-strong">
                      {c.name}
                    </span>
                    <span className="text-[11.5px] text-ink-faint">
                      {c.hint}
                    </span>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      <p className="mt-auto px-1 text-[11.5px] leading-snug text-ink-faint">
        Drag components onto the canvas. Connect them by dragging from handle
        to handle.{" "}
        <span className="text-[10.5px] uppercase tracking-wider text-ink-faint">
          (Drag-to-canvas coming in `add-diagram-editor`.)
        </span>
      </p>
    </aside>
  );
}
