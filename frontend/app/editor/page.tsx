"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Loader2, OctagonAlert } from "lucide-react";
import { toast } from "sonner";

import { DiagramCanvas } from "@/components/DiagramCanvas";
import { EditorShell } from "@/components/editor/editor-shell";
import { MockCanvas } from "@/components/editor/mock-canvas";
import { Button } from "@/components/ui/button";
import { useAnalyze, useGenerate, useSaveDiagram } from "@/lib/hooks";

/**
 * Editor page.
 *
 * Three-column shell that mirrors the prototype: palette / canvas / chat.
 *
 * Canvas behaviour by state:
 *    - no prompt, no diagram    → blank `MockCanvas` with empty hint
 *    - generating               → mock demo placeholder behind overlay
 *    - error                    → blank canvas + error overlay
 *    - success                  → real `<DiagramCanvas>` (React Flow) with
 *                                the generated diagram
 */
export default function EditorPage() {
  const searchParams = useSearchParams();
  const initialPrompt = searchParams.get("prompt") ?? "";

  const [chatHidden, setChatHidden] = useState(false);
  const generation = useGenerate();
  const save = useSaveDiagram();
  const analysis = useAnalyze();
  const diagramId = searchParams.get("id");

  // Single entry point for kicking off a generation. Used both by the
  // first-paint effect (when ?prompt=… is present) and the Try-again
  // button on the error overlay. Wrapped in useCallback so the effect's
  // dep array stays stable.
  const runGenerate = useCallback(
    (prompt: string) => {
      // A fresh generation invalidates any prior analysis.
      analysis.reset();
      generation.mutate(prompt, {
        onError: (err) => {
          const detail =
            err instanceof Error
              ? err.message
              : "Unknown error";
          toast.error("Generation failed", { description: detail });
        },
        onSuccess: (diagram) => {
          toast.success("Diagram generated", {
            description: `${diagram.nodes.length} components · ${diagram.edges.length} connections`,
          });
          // Persist it so it shows up in the library and survives a refresh.
          save.mutate(diagram, {
            onError: (err) => {
              const detail = "Could not save";
              toast.error("Save failed", { description: detail });
            },
          });
        },
      });
    },
    [generation, save, analysis],
  );

  // Fire one mutation as soon as we land with ?prompt=…
  useEffect(() => {
    if (!initialPrompt) return;
    if (generation.isPending || generation.isSuccess || generation.isError) {
      return;
    }
    runGenerate(initialPrompt);
  }, [initialPrompt, runGenerate]);

  const diagram = generation.data ?? null;
  const generating = generation.isPending;
  const analysisData = analysis.data ?? null;

  const content = (
    <div className="relative flex-1">
      {diagram ? (
        <DiagramCanvas diagram={diagram} />
      ) : (
        <MockCanvas demo={generating} />
      )}
      {generating && <GeneratingOverlay prompt={initialPrompt} />}
      {!diagram && generating && !error && (
        <ChatPanelHidden />
      )}
    </div>
  );

  const error = generation.isError ? (generation.error as any) : null;

  return (
    <EditorShell
      content={content}
      chatHidden={chatHidden}
      onToggleChat={() => setChatHidden((v) => !v)}
      diagramName={diagram?.metadata.name ?? (generating ? "Generating…" : diagram?.metadata.name ?? "Untitled")}
      componentCount={diagram?.nodes.length ?? 0}
      connectionCount={diagram?.edges.length ?? 0}
      savedLabel={generating ? "generating…" : !diagram ? "not saved" : "saved just now"}
      hasDiagram={Boolean(diagram)}
      analysis={analysisData ?? null}
      analyzing={generation.isPending}
      analyzeError={error?.detail ?? null}
      onAnalyze={() => {
        if (!diagram) return;
        analysis.mutate({ diagram, modeId: "tutor" });
      }}
      diagramId={diagramId}   // Pass diagram context for chat persistence
    />
  );
}

function GeneratingOverlay({ prompt }: { prompt: string }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2 rounded-xl border border-line bg-card px-7 py-5 shadow-md">
        <Loader2 className="animate-spin text-accent" size={28} />
        <p className="text-lg font-semibold text-ink-strong">Sketching your architecture…</p>
        <p className="text-center text-sm text-ink-muted">Composing prompt · retrieving patterns · waiting on model</p>
        {prompt && (
          <p className="mt-2 max-w-[300px] text-center font-mono text-xs text-ink-faint">
            "{prompt.slice(0, 80)}{prompt.length > 80 ? "…" : ""}"
          </p>
        )}
      </div>
    </div>
  );
}

function ChatPanelHidden() {
  return <div className="absolute inset-0 bg-transparent z-10 pointer-events-none" />;
}

function ErrorOverlay({ detail, code, onRetry }: { detail: any; code: string; onRetry: () => void }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2.5 rounded-xl border border-line bg-card px-7 py-5 shadow-md">
        <OctagonAlert size={28} className="text-accent" />
        <p className="text-lg font-semibold text-ink-strong">Generation failed</p>
        <p className="text-center text-sm text-ink-muted">
          {typeof detail === "object" ? JSON.stringify(detail) : (detail as any)}
        </p>
        <p className="font-mono text-xs text-ink-faint">code: {code}</p>
        <Button variant="primary" size="md" onClick={onRetry} className="mt-1">
          Try again →
        </Button>
      </div>
    </div>
  );
}
