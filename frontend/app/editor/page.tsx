"use client";

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { OctagonAlert } from "lucide-react";
import { toast } from "sonner";

import { DiagramCanvas } from "@/components/DiagramCanvas";
import { EditorShell } from "@/components/editor/editor-shell";
import { MockCanvas } from "@/components/editor/mock-canvas";
import { Enso } from "@/components/enso";
import { Button } from "@/components/ui/button";
import { useAnalyze, useGenerate, useSaveDiagram } from "@/lib/hooks";
import { useDiagramEditor } from "@/lib/useDiagramEditor";
import { flowToDiagram } from "@/lib/flowToDiagram";
import { newDiagramId } from "@/lib/ids";
import { TangramApiError } from "@/lib/api";
import type { Diagram } from "@/types/tangram";

/** A fresh empty diagram for the blank-canvas entry. */
function makeBlankDiagram(): Diagram {
  const now = new Date().toISOString();
  return {
    version: "0.1.0",
    id: newDiagramId(),
    metadata: { name: "Untitled", description: null, createdAt: now, updatedAt: now },
    nodes: [],
    edges: [],
    conversation: [],
  };
}

/**
 * Editor page.
 *
 * Three-column shell that mirrors the prototype: palette / canvas / chat.
 *
 * Canvas behaviour by state:
 *   - no prompt, no diagram   → blank `MockCanvas` with empty hint
 *   - generating              → mock demo placeholder behind overlay
 *   - error                   → blank canvas + error overlay
 *   - success                 → real `<DiagramCanvas>` (React Flow) with
 *                               the generated diagram
 *
 * Drag/connect editing isn't wired yet (lands in `add-diagram-editor`);
 * React Flow is read-only here.
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

  const [chatHidden, setChatHidden] = useState(false);
  const generation = useGenerate();
  const save = useSaveDiagram();
  const analysis = useAnalyze();

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
            err instanceof TangramApiError
              ? err.detail
              : err instanceof Error
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
              const detail =
                err instanceof TangramApiError ? err.detail : "Could not save";
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
    // Intentionally key on `initialPrompt` only. `runGenerate` would
    // change reference every render; including it would re-fire the
    // mutation on each render and is exactly the bug we're avoiding.
    // The project's flat ESLint config doesn't have react-hooks rules
    // wired, so there's no warning to silence.
  }, [initialPrompt]);

  const generating = generation.isPending;
  // Blank-canvas mode (no ?prompt=) starts an editable empty draft. With a
  // prompt, we edit the generated diagram once it arrives.
  const blankMode = !initialPrompt;
  const blankDraft = useMemo(() => (blankMode ? makeBlankDiagram() : null), [blankMode]);
  const diagram = generation.data ?? blankDraft;

  const editor = useDiagramEditor(diagram);
  const [counts, setCounts] = useState({ nodes: 0, edges: 0 });
  const [liveDiagram, setLiveDiagram] = useState<Diagram | null>(diagram ?? null);
  const [selectedNode, setSelectedNode] = useState<
    { id: string; name: string; type: string } | undefined
  >(undefined);

  useEffect(() => {
    setLiveDiagram(diagram ?? null);
    setSelectedNode(undefined);
  }, [diagram]);

  const handleChange = useCallback(
    (nodes: unknown[], edges: unknown[]) => {
      editor.onChange(nodes as never, edges as never);
      if (diagram) {
        setLiveDiagram(flowToDiagram(nodes as never, edges as never, diagram));
      }
      setCounts((c) =>
        c.nodes === nodes.length && c.edges === edges.length
          ? c
          : { nodes: nodes.length, edges: edges.length },
      );
    },
    [editor, diagram],
  );

  const runAnalyze = useCallback(() => {
    if (!diagram) return;
    analysis.mutate(
      { diagram },
      {
        onError: (err) => {
          const detail =
            err instanceof TangramApiError ? err.detail : "Could not analyze";
          toast.error("Analysis failed", { description: detail });
        },
      },
    );
  }, [diagram, analysis]);

  const analyzeError = analysis.isError
    ? analysis.error instanceof TangramApiError
      ? analysis.error.detail
      : "Could not analyze this diagram."
    : null;
  const error = generation.isError
    ? errorToOverlay(generation.error)
    : null;

  const content = (
    <div className="relative flex-1">
      {diagram && !generating ? (
        <DiagramCanvas
          diagram={diagram}
          onChange={handleChange}
          onSelectNode={setSelectedNode}
        />
      ) : (
        <MockCanvas demo={generating} />
      )}
      {generating && <GeneratingOverlay prompt={initialPrompt} />}
      {error && (
        <ErrorOverlay
          detail={error.detail}
          code={error.code}
          onRetry={() => {
            // Clear the failed state AND immediately re-issue the request.
            // Just `reset()` would leave us on a blank canvas because the
            // first-paint effect won't re-fire (initialPrompt is unchanged).
            generation.reset();
            if (initialPrompt) runGenerate(initialPrompt);
          }}
        />
      )}
    </div>
  );

  const diagramName = diagram?.metadata.name ?? (generating ? "New diagram" : "Untitled");
  // Live counts come from the canvas once editing; fall back to the base.
  const componentCount = diagram ? counts.nodes || diagram.nodes.length : 0;
  const connectionCount = diagram ? counts.edges || diagram.edges.length : 0;
  const savedLabel = generating
    ? "generating…"
    : diagram
      ? editor.label
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
      diagram={liveDiagram}
      selectedNode={selectedNode}
      hasDiagram={Boolean(diagram)}
      analysis={analysis.data ?? null}
      analyzing={analysis.isPending}
      analyzeError={analyzeError}
      onAnalyze={runAnalyze}
      onSave={editor.saveNow}
      canSave={editor.canSave}
    />
  );
}

function errorToOverlay(err: unknown): { detail: string; code: string } {
  if (err instanceof TangramApiError) {
    return { detail: err.detail, code: err.code };
  }
  if (err instanceof Error) {
    return { detail: err.message, code: "network_error" };
  }
  return { detail: "Unknown error", code: "unknown_error" };
}

function GeneratingOverlay({ prompt }: { prompt: string }) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2.5 rounded-[var(--radius-lg)] border border-line bg-card px-7 py-5 shadow-md">
        <Enso size={34} />
        <p className="font-serif text-[18px] font-medium text-ink-strong">
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
