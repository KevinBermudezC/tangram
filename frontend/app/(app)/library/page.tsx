"use client";

import { LayoutGrid, List, Search } from "lucide-react";
import { useState } from "react";

import { DiagramCard } from "@/components/diagram-card";
import { Input } from "@/components/ui/input";
import { TemplatesStrip } from "@/components/templates-strip";
import { recentDiagrams } from "@/lib/mock-data";
import type { DiagramSource } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

type Filter = "all" | "drafts" | "ai" | "manual";

const FILTERS: { id: Filter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "drafts", label: "Drafts" },
  { id: "ai", label: "Generated" },
  { id: "manual", label: "Manual" },
];

function matchesFilter(source: DiagramSource, filter: Filter): boolean {
  if (filter === "all") return true;
  if (filter === "drafts") return source === "draft";
  return source === filter;
}

export default function LibraryPage() {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [view, setView] = useState<"grid" | "list">("grid");

  const filtered = recentDiagrams.filter((d) => {
    if (!matchesFilter(d.source, filter)) return false;
    if (query && !d.name.toLowerCase().includes(query.toLowerCase())) {
      return false;
    }
    return true;
  });

  const draftCount = recentDiagrams.filter((d) => d.source === "draft").length;
  const nonDraftCount = recentDiagrams.length - draftCount;

  return (
    <main className="flex flex-col gap-6 p-8">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="text-[22px] font-semibold tracking-tight text-ink-strong">
            Library
          </h1>
          <p className="text-[13px] text-ink-muted">
            {nonDraftCount} diagrams · {draftCount} draft · stored as JSON in{" "}
            <code>data/diagrams/</code>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <div className="inline-flex gap-0.5 rounded-full border border-line bg-sidebar p-[3px]">
            {FILTERS.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => setFilter(f.id)}
                className={cn(
                  "rounded-full px-3 py-1 text-[12.5px] transition-colors",
                  filter === f.id
                    ? "bg-card font-semibold text-ink-strong shadow-sm"
                    : "text-ink-muted hover:text-ink-strong",
                )}
              >
                {f.label}
              </button>
            ))}
          </div>

          <label className="flex h-8 items-center gap-1.5 rounded-[var(--radius)] border border-line bg-card px-3 text-ink-faint focus-within:border-accent">
            <Search size={14} />
            <Input
              type="search"
              placeholder="Search diagrams…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="h-7 w-[180px] border-0 bg-transparent px-0 shadow-none focus-visible:border-0 focus-visible:ring-0"
            />
          </label>

          <div className="inline-flex overflow-hidden rounded-[var(--radius)] border border-line bg-card">
            <button
              type="button"
              title="Grid"
              onClick={() => setView("grid")}
              className={cn(
                "inline-flex h-8 w-8 items-center justify-center",
                view === "grid"
                  ? "bg-sidebar text-ink-strong"
                  : "text-ink-muted hover:text-ink-strong",
              )}
            >
              <LayoutGrid size={14} />
            </button>
            <button
              type="button"
              title="List"
              onClick={() => setView("list")}
              className={cn(
                "inline-flex h-8 w-8 items-center justify-center",
                view === "list"
                  ? "bg-sidebar text-ink-strong"
                  : "text-ink-muted hover:text-ink-strong",
              )}
            >
              <List size={14} />
            </button>
          </div>
        </div>
      </header>

      {filtered.length === 0 ? (
        <div className="rounded-[var(--radius-lg)] border border-dashed border-line-strong p-12 text-center">
          <p className="text-[14px] text-ink-muted">
            No diagrams match this filter yet.
          </p>
        </div>
      ) : view === "grid" ? (
        <ul className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filtered.map((d) => (
            <li key={d.id}>
              <DiagramCard diagram={d} />
            </li>
          ))}
        </ul>
      ) : (
        <ul className="flex flex-col gap-1.5 rounded-[var(--radius-lg)] border border-line bg-card">
          {filtered.map((d) => (
            <li key={d.id}>
              <a
                href="/editor"
                className="flex items-center gap-3 border-b border-line px-4 py-3 text-[13.5px] text-ink-body last:border-b-0 hover:bg-sidebar"
              >
                <span className="font-medium text-ink-strong">{d.name}</span>
                <span className="text-ink-faint">·</span>
                <span className="text-ink-muted">
                  {d.components} components
                </span>
                <span className="ml-auto text-[12px] text-ink-faint">
                  {d.updatedLabel}
                </span>
              </a>
            </li>
          ))}
        </ul>
      )}

      <TemplatesStrip />
    </main>
  );
}
