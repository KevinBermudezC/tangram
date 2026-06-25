"use client";

import type { ReactNode } from "react";

import { ChatPanel } from "@/components/editor/chat-panel";
import { EditorPalette } from "@/components/editor/palette";
import { EditorTopbar } from "@/components/editor/topbar";
import { cn } from "@/lib/utils";
import type { AnalyzeResponse } from "@/types/tangram";

export interface EditorShellProps {
  content: ReactNode;
  chatHidden?: boolean;
  onToggleChat?: () => void;
  diagramName?: string;
  componentCount?: number;
  connectionCount?: number;
  savedLabel?: string;
  /** Analysis wiring, forwarded to the chat panel. */
  hasDiagram?: boolean;
  analysis?: AnalyzeResponse | null;
  analyzing?: boolean;
  analyzeError?: string | null;
  onAnalyze?: () => void;
  /** Manual save wiring, forwarded to the topbar. */
  onSave?: () => void;
  canSave?: boolean;
}

/**
 * Three-column editor chrome: palette / canvas / chat. Shared by the
 * generate flow (`/editor`) and the open-saved flow (`/editor/[id]`); only
 * the center `content` and the topbar metadata differ between them.
 */
export function EditorShell({
  content,
  chatHidden = false,
  onToggleChat = () => undefined,
  diagramName = "Untitled",
  componentCount = 0,
  connectionCount = 0,
  savedLabel = "not saved",
  hasDiagram = false,
  analysis = null,
  analyzing = false,
  analyzeError = null,
  onAnalyze,
  onSave,
  canSave = false,
}: EditorShellProps) {
  return (
    <div
      className={cn(
        "grid h-screen",
        chatHidden ? "grid-cols-[260px_1fr]" : "grid-cols-[260px_1fr_360px]",
      )}
    >
      <EditorPalette />
      <main className="flex min-w-0 flex-col">
        <EditorTopbar
          name={diagramName}
          componentCount={componentCount}
          connectionCount={connectionCount}
          savedLabel={savedLabel}
          onToggleChat={onToggleChat}
          chatHidden={chatHidden}
          onSave={onSave}
          canSave={canSave}
        />
        {content}
      </main>
      {!chatHidden && (
        <ChatPanel
          hasDiagram={hasDiagram}
          analysis={analysis}
          analyzing={analyzing}
          analyzeError={analyzeError}
          onAnalyze={onAnalyze}
        />
      )}
    </div>
  );
}
