"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  LayoutGrid,
  Layers,
  Plus,
  Search,
  Settings,
} from "lucide-react";
import type { ReactNode } from "react";

import { BackendStatus } from "@/components/backend-status";
import { Brand } from "@/components/brand";
import { GithubMark } from "@/components/icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useDiagrams } from "@/lib/hooks";
import type { DiagramSource } from "@/lib/mock-data";
import { cn } from "@/lib/utils";

interface RailNavItem {
  href: string;
  label: string;
  icon: ReactNode;
  /** Match prefix so `/library/foo` still highlights "Library". */
  matchPrefix?: string;
}

const NAV: RailNavItem[] = [
  {
    href: "/",
    label: "Home",
    icon: <HomeIcon />,
  },
  {
    href: "/library",
    label: "Library",
    icon: <LayoutGrid size={14} />,
    matchPrefix: "/library",
  },
  {
    href: "/templates",
    label: "Templates",
    icon: <Layers size={14} />,
    matchPrefix: "/templates",
  },
  {
    href: "/settings",
    label: "Settings",
    icon: <Settings size={14} />,
    matchPrefix: "/settings",
  },
];

export function AppRail() {
  const pathname = usePathname();

  return (
    <aside className="flex min-h-0 flex-col gap-3.5 border-r border-line bg-sidebar px-3 py-4">
      <Brand className="px-1.5 pb-0.5" />

      <Button asChild variant="ink" size="md" className="h-9 w-full">
        <Link href="/editor">
          <Plus size={14} />
          New diagram
        </Link>
      </Button>

      <label className="flex h-8 items-center gap-1.5 rounded-[var(--radius)] border border-line bg-card px-2.5 text-ink-faint focus-within:border-ink-muted">
        <Search size={13} />
        <Input
          type="search"
          placeholder="Search"
          className="h-7 border-0 bg-transparent px-0 shadow-none focus-visible:border-0 focus-visible:ring-0"
        />
      </label>

      <ul className="flex flex-col gap-px">
        {NAV.map((item) => {
          const active =
            item.matchPrefix !== undefined
              ? pathname.startsWith(item.matchPrefix)
              : pathname === item.href;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-[13px] text-ink-body transition-colors",
                  active
                    ? "bg-accent-tint/70 font-medium text-ink-strong shadow-[inset_2px_0_0_var(--color-accent)]"
                    : "hover:bg-black/[0.04] hover:text-ink-strong",
                )}
              >
                <span className={cn(active ? "text-accent-strong" : "text-ink-muted")}>
                  {item.icon}
                </span>
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>

      <RecentDiagrams />

      <div className="mt-auto flex flex-col gap-1 border-t border-line px-2.5 pt-2">
        <a
          href="https://github.com/KevinBermudezC/tangram"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 py-1 text-[12.5px] text-ink-muted no-underline hover:text-ink-strong"
        >
          <GithubMark size={13} />
          GitHub
        </a>
        <BackendStatus />
        <span className="text-[11px] text-ink-faint">MIT · Pre-alpha</span>
      </div>
    </aside>
  );
}

function RecentDiagrams() {
  const { data, isLoading } = useDiagrams();
  const diagrams = data ?? [];

  return (
    <section className="mt-1.5 flex flex-col gap-1">
      <header className="flex items-center justify-between px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.06em] text-ink-faint">
        <span>Recent</span>
        <button
          type="button"
          aria-label="Collapse"
          className="inline-flex items-center justify-center text-ink-faint hover:text-ink-strong"
        >
          <ChevronDown size={10} strokeWidth={2.2} />
        </button>
      </header>
      <ul className="flex flex-col gap-px">
        {isLoading ? (
          // Skeleton rows while React Query resolves. Mock returns instantly
          // today so these only flash; once a real endpoint backs this they
          // matter.
          Array.from({ length: 3 }).map((_, i) => (
            <li key={i} className="px-2.5 py-1.5">
              <span className="block h-3 w-32 animate-pulse rounded-sm bg-black/[0.06]" />
            </li>
          ))
        ) : diagrams.length === 0 ? (
          <li className="px-2.5 py-1 text-[12px] text-ink-faint">
            No diagrams yet.
          </li>
        ) : (
          diagrams.slice(0, 6).map((d) => (
            <li key={d.id}>
              <Link
                href={`/editor/${d.id}`}
                className="flex items-center gap-2.5 truncate rounded-md px-2.5 py-1.5 text-[13px] text-ink-body hover:bg-black/[0.04] hover:text-ink-strong"
              >
                <SourceDot source={d.source} />
                <span className="truncate">{d.name}</span>
              </Link>
            </li>
          ))
        )}
        {diagrams.length > 0 && (
          <li>
            <Link
              href="/library"
              className="inline-block px-2.5 py-1.5 text-[12px] text-ink-muted hover:text-ink-strong"
            >
              More →
            </Link>
          </li>
        )}
      </ul>
    </section>
  );
}

function SourceDot({ source }: { source: DiagramSource }) {
  return (
    <span
      aria-hidden
      className={cn(
        "h-1.5 w-1.5 shrink-0 rounded-full",
        source === "ai" && "bg-accent",
        source === "manual" && "bg-ink-faint",
        source === "draft" && "border border-dashed border-ink-faint bg-transparent",
      )}
    />
  );
}

function HomeIcon() {
  // Lucide's Home doesn't quite match the look; use a small inline path that
  // mirrors the prototype.
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
    >
      <path
        d="M3 12 12 4l9 8M5 10v9h5v-5h4v5h5v-9"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}
