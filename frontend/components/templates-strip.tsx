import Link from "next/link";

import { NodeIcon } from "@/components/node-icon";
import { templates } from "@/lib/mock-data";
import { nodeColors } from "@/lib/node-style";

/**
 * Curated starting points. Clicking forks one into the user's library —
 * the fork endpoint doesn't exist yet, so each card just links to the
 * editor for now.
 */
export function TemplatesStrip() {
  return (
    <section className="flex flex-col gap-3">
      <header className="flex flex-col gap-0.5">
        <h2 className="text-[16px] font-semibold tracking-tight text-ink-strong">
          Templates
        </h2>
        <p className="text-[12.5px] text-ink-muted">
          Curated starting points. Fork into your library and edit.
        </p>
      </header>
      <ul className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {templates.map((tpl) => {
          const colors = nodeColors[tpl.primaryType];
          return (
            <li key={tpl.id}>
              <Link
                href="/editor"
                className="flex h-full flex-col gap-2.5 rounded-[var(--radius)] border border-line bg-card p-3.5 no-underline transition-all hover:-translate-y-px hover:border-accent"
              >
                <span
                  className="inline-flex h-9 w-9 items-center justify-center rounded-[9px] border"
                  style={{
                    backgroundColor: colors.fill,
                    color: colors.ink,
                    borderColor: colors.ink,
                  }}
                  aria-hidden
                >
                  <NodeIcon type={tpl.primaryType} size={18} />
                </span>
                <p className="text-[13.5px] font-semibold text-ink-strong">
                  {tpl.name}
                </p>
                <p className="text-[11.5px] leading-snug text-ink-muted">
                  {tpl.hint}
                </p>
              </Link>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
