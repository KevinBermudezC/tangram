"use client";

import type { ReactNode } from "react";

import { ChatPanel } from "@/components/editor/chat-panel";
import { EditorPalette } from "@/components/editor/palette";
import { EditorTopbar } from "@/components/editor/topbar";
import { cn } from "@/lib/utils";

export interface EditorShellProps {
  content: ReactNode;
  chatHidden?: boolean;
  onToggleChat?: () => void;
  diagramName?: string;
  componentCount?: number;
  connectionCount?: number;
  savedLabel?: string;
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
        />
        {content}
      </main>
      {!chatHidden && <ChatPanel />}
    </div>
  );
}
