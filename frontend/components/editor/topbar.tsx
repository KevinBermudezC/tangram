"use client";

import { Check, Download, Save, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { GithubMark } from "@/components/icons";
import { ThemeToggle } from "@/components/theme-toggle";
import { cn } from "@/lib/utils";

interface EditorTopbarProps {
  name: string;
  componentCount: number;
  connectionCount: number;
  savedLabel: string;
  onToggleChat: () => void;
  chatHidden: boolean;
  /** Manual save — flushes the pending autosave. Omit to hide the button. */
  onSave?: () => void;
  /** Whether there are unsaved changes to flush. */
  canSave?: boolean;
}

export function EditorTopbar({
  name,
  componentCount,
  connectionCount,
  savedLabel,
  onToggleChat,
  chatHidden,
  onSave,
  canSave = false,
}: EditorTopbarProps) {
  return (
    <header className="flex h-14 flex-shrink-0 items-center justify-between gap-3 border-b border-line bg-page px-4">
      <div className="flex min-w-0 items-center gap-2">
        <span className="truncate text-[14px] font-semibold text-ink-strong">
          {name}
        </span>
        <span className="hidden shrink-0 items-center gap-1.5 whitespace-nowrap text-[12.5px] text-ink-muted sm:inline-flex">
          <span className="text-ink-faint">·</span>
          <span>{componentCount} components</span>
          <span className="text-ink-faint">·</span>
          <span>{connectionCount} connections</span>
        </span>
      </div>

      <div className="flex shrink-0 items-center gap-1.5">
        {onSave && (
          <Button
            variant={canSave ? "primary" : "secondary"}
            size="sm"
            onClick={onSave}
            disabled={!canSave}
            aria-label="Save diagram"
            title={savedLabel}
          >
            {canSave ? <Save size={13} /> : <Check size={13} />}
            {canSave ? "Save" : "Saved"}
          </Button>
        )}
        <Button
          variant="secondary"
          size="sm"
          onClick={onToggleChat}
          aria-pressed={!chatHidden}
        >
          {chatHidden ? "Show AI" : "Hide AI"}
        </Button>
        <Button variant="ghost" size="icon" aria-label="Export" title="Export">
          <Download size={14} />
        </Button>
        <Button variant="ghost" size="icon" aria-label="Clear canvas" title="Clear canvas">
          <Trash2 size={14} />
        </Button>
        <span className={cn("mx-1 h-5 w-px bg-line")} aria-hidden />
        <ThemeToggle />
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
