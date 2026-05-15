"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, OctagonAlert } from "lucide-react";

import { ChatPanel } from "@/components/editor/chat-panel";
import { EditorPalette } from "@/components/editor/palette";
import { EditorTopbar } from "@/components/editor/topbar";
import { MockCanvas } from "@/components/editor/mock-canvas";
import { Button } from "@/components/ui/button";
import { generate, TangramApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { Diagram } from "@/types/tangram";

/**
 * Editor page.
 *
 * Three-column shell that mirrors the prototype: palette on the left,
 * mock canvas + topbar in the middle, AI chat on the right. Drag/connect
 * isn't wired yet (that lands in `add-diagram-editor`); for now the canvas
 * is visual chrome only.
 */
export default function EditorPage() {
  return (
    <Suspense fallback={<EditorShell content={<MockCanvas demo={false} />} />}>
      <EditorInner />
    </Suspense>
  );
}

function EditorInner() {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get("prompt") ?? "";

  const [diagram, setDiagram] = useState<Diagram | null>(null);
  const [error, setError] = useState<{ detail: string; code: string } | null>(
    null,
  );
  const [generating, setGenerating] = useState(false);
  const [chatHidden, setChatHidden] = useState(false);

  // Auto-generate when the user arrives with ?prompt=…
  useEffect(() => {
    if (!initialPrompt || diagram || generating) return;
    let cancelled = false;
    setGenerating(true);
    setError(null);
    generate(initialPrompt)
      .then((d) => {
        if (!cancelled) setDiagram(d);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        if (err instanceof TangramApiError) {
          setError({ detail: err.detail, code: err.code });
        } else if (err instanceof Error) {
          setError({ detail: err.message, code: "network_error" });
        } else {
          setError({ detail: "Unknown error", code: "unknown_error" });
        }
      })
      .finally(() => {
        if (!cancelled) setGenerating(false);
      });
    return () => {
      cancelled = true;
    };
  }, [initialPrompt, diagram, generating]);

  // Show the canned demo only as a placeholder while the LLM is generating
  // for the first time. Blank canvases and post-success states render empty
  // until the real React Flow editor wires up.
  const showDemoPlaceholder = generating;

  const content = (
    <div className="relative flex-1">
      <MockCanvas demo={showDemoPlaceholder} />
      {generating && <GeneratingOverlay prompt={initialPrompt} />}
      {error && (
        <ErrorOverlay
          detail={error.detail}
          code={error.code}
          onRetry={() => {
            setError(null);
            setDiagram(null);
          }}
        />
      )}
    </div>
  );

  // Topbar labels reflect the current state of the canvas:
  //   - generated diagram (success)  → its name + counts + "saved just now"
  //   - generating                    → prompt as name + "generating…"
  //   - blank canvas (no prompt yet)  → "Untitled" + 0/0 + "not saved"
  const blank = !diagram && !generating && !initialPrompt;
  const diagramName = diagram?.metadata.name ?? (blank ? "Untitled" : "New diagram");
  const componentCount = diagram?.nodes.length ?? 0;
  const connectionCount = diagram?.edges.length ?? 0;
  const savedLabel = diagram
    ? "saved just now"
    : generating
      ? "generating…"
      : "not saved";

  return (
    <EditorShell
      content={content}
      chatHidden={chatHidden}
      onToggleChat={() => setChatHidden((v) => !v)}
      diagramName={diagramName}
      componentCount={componentCount}
      connectionCount={connectionCount}
      savedLabel={savedLabel}
    />
  );
}

interface EditorShellProps {
  content: React.ReactNode;
  chatHidden?: boolean;
  onToggleChat?: () => void;
  diagramName?: string;
  componentCount?: number;
  connectionCount?: number;
  savedLabel?: string;
}

function EditorShell({
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
        chatHidden
          ? "grid-cols-[260px_1fr]"
          : "grid-cols-[260px_1fr_360px]",
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

function GeneratingOverlay({ prompt }: { prompt: string }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2 rounded-[var(--radius-lg)] border border-line bg-card px-7 py-5 shadow-md">
        <Loader2 className="animate-spin text-accent" size={28} />
        <p className="text-[16px] font-semibold text-ink-strong">
          Sketching your architecture…
        </p>
        <p className="text-center text-[13px] leading-relaxed text-ink-muted">
          Composing prompt · retrieving patterns · waiting on model
        </p>
        {prompt && (
          <p className="mt-2 max-w-[300px] text-center font-mono text-[11px] text-ink-faint">
            “{prompt.slice(0, 80)}{prompt.length > 80 ? "…" : ""}”
          </p>
        )}
      </div>
    </div>
  );
}

function ErrorOverlay({
  detail,
  code,
  onRetry,
}: {
  detail: string;
  code: string;
  onRetry: () => void;
}) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2.5 rounded-[var(--radius-lg)] border border-line bg-card px-7 py-5 shadow-md">
        <OctagonAlert size={28} className="text-accent" />
        <p className="text-[16px] font-semibold text-ink-strong">
          Generation failed
        </p>
        <p className="text-center text-[13px] leading-relaxed text-ink-muted">
          {detail}
        </p>
        <p className="font-mono text-[11px] text-ink-faint">
          code <code>{code}</code>
        </p>
        <Button variant="primary" size="md" onClick={onRetry} className="mt-1">
          Try again →
        </Button>
      </div>
    </div>
  );
}
