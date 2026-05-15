"use client";

import { Download, Moon, Plus, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GithubMark } from "@/components/icons";
import { cn } from "@/lib/utils";

interface EditorTopbarProps {
  name: string;
  componentCount: number;
  connectionCount: number;
  savedLabel: string;
  onToggleChat: () => void;
  chatHidden: boolean;
}

export function EditorTopbar({
  name,
  componentCount,
  connectionCount,
  savedLabel,
  onToggleChat,
  chatHidden,
}: EditorTopbarProps) {
  return (
    <header className="flex h-14 flex-shrink-0 items-center justify-between gap-4 border-b border-line bg-page px-4">
      <div className="flex min-w-0 items-center gap-2.5">
        <span className="truncate text-[14px] font-semibold text-ink-strong">
          {name}
        </span>
        <span className="inline-flex items-center gap-1.5 whitespace-nowrap text-[12.5px] text-ink-muted">
          <span>{componentCount} components</span>
          <span className="text-ink-faint">·</span>
          <span>{connectionCount} connections</span>
          <span className="text-ink-faint">·</span>
          <span>{savedLabel}</span>
        </span>
      </div>

      <div className="flex items-center gap-1.5">
        <Button variant="secondary" size="sm">
          <Plus size={13} />
          New
        </Button>
        <Button
          variant="secondary"
          size="sm"
          onClick={onToggleChat}
          aria-pressed={!chatHidden}
        >
          {chatHidden ? "Show AI" : "Hide AI"}
        </Button>
        <Button variant="secondary" size="sm">
          <Download size={13} />
          Export
        </Button>
        <Button variant="danger" size="sm">
          <Trash2 size={13} />
          Clear
        </Button>
        <span className={cn("mx-1 h-5 w-px bg-line")} aria-hidden />
        <Button
          variant="ghost"
          size="icon"
          aria-label="Dark mode (coming soon)"
          disabled
        >
          <Moon size={14} />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          asChild
          aria-label="GitHub"
        >
          <a
            href="https://github.com/KevinBermudezC/tangram"
            target="_blank"
            rel="noreferrer"
          >
            <GithubMark size={14} />
          </a>
        </Button>
      </div>
    </header>
  );
}
