"use client";

import Link from "next/link";
import { MoreHorizontal } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { DiagramThumb } from "@/components/diagram-thumb";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { MockDiagram } from "@/lib/mock-data";

interface DiagramCardProps {
  diagram: MockDiagram;
}

export function DiagramCard({ diagram }: DiagramCardProps) {
  return (
    <article className="group relative overflow-hidden rounded-[var(--radius-lg)] border border-line bg-card transition-all hover:-translate-y-px hover:border-line-strong hover:shadow-md">
      <Link href={`/editor/${diagram.id}`} className="block no-underline">
        <div className="relative aspect-[5/3] border-b border-line bg-canvas">
          <DiagramThumb diagram={diagram} />
          <span className="absolute left-2 top-2">
            {diagram.source === "ai" && <Badge variant="ai">AI</Badge>}
            {diagram.source === "manual" && (
              <Badge variant="manual">Manual</Badge>
            )}
            {diagram.source === "draft" && (
              <Badge variant="draft">Draft</Badge>
            )}
          </span>
        </div>
        <div className="flex flex-col gap-0.5 px-3.5 py-3">
          <p className="truncate text-[14px] font-semibold text-ink-strong">
            {diagram.name}
          </p>
          <p className="flex flex-wrap gap-x-1.5 text-[11.5px] text-ink-muted">
            <span>{diagram.components} components</span>
            {diagram.connections > 0 && (
              <>
                <span className="text-ink-faint">·</span>
                <span>{diagram.connections} connections</span>
              </>
            )}
            <span className="text-ink-faint">·</span>
            <span>{diagram.updatedLabel}</span>
          </p>
        </div>
      </Link>

      <div className="absolute right-2 top-2 opacity-0 transition-opacity group-hover:opacity-100">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              aria-label={`Actions for ${diagram.name}`}
              className="inline-flex h-7 w-7 items-center justify-center rounded-md border border-transparent bg-white/60 text-ink-muted backdrop-blur hover:border-line hover:bg-card hover:text-ink-strong"
            >
              <MoreHorizontal size={14} />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem disabled>Rename</DropdownMenuItem>
            <DropdownMenuItem disabled>Duplicate</DropdownMenuItem>
            <DropdownMenuItem disabled>Export…</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              disabled
              className="text-accent-strong focus:text-accent-strong"
            >
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </article>
  );
}
