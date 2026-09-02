"use client";

import { use, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { OctagonAlert } from "lucide-react";
import { toast } from "sonner";

import { DiagramCanvas } from "@/components/DiagramCanvas";
import { EditorShell } from "@/components/editor/editor-shell";
import { Enso } from "@/components/enso";
import { Button } from "@/components/ui/button";
import { TangramApiError } from "@/lib/api";
import { flowToDiagram } from "@/lib/flowToDiagram";
import { useAnalyze, useDiagram } from "@/lib/hooks";
import { useDiagramEditor } from "@/lib/useDiagramEditor";
import type { Diagram } from "@/types/tangram";

/**
 * Open a saved diagram by id.
 *
 * Loads via `GET /diagrams/{id}`. Unlike `/editor`, there's no generation
 * here — just fetch-and-render. A 404 surfaces a "not found" state with a
 * way back to the library.
 */
export default function EditorByIdPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  return <EditorById id={id} />;
}

/** Inner editor so tests can pass an id without resolving a Next.js params Promise. */
export function EditorById({ id }: { id: string }) {
  const query = useDiagram(id);
  const diagram = query.data ?? null;
  const analysis = useAnalyze();

  const editor = useDiagramEditor(diagram);
  const [counts, setCounts] = useState({ nodes: 0, edges: 0 });
  const [liveDiagram, setLiveDiagram] = useState<Diagram | null>(diagram);
  const [selectedNode, setSelectedNode] = useState<
    { id: string; name: string; type: string } | undefined
  >(undefined);

  useEffect(() => {
    setLiveDiagram(diagram);
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

  const notFound =
    query.isError &&
    query.error instanceof TangramApiError &&
    query.error.status === 404;

  const content = (
    <div className="relative flex-1">
      {diagram && (
        <DiagramCanvas
          diagram={diagram}
          onChange={handleChange}
          onSelectNode={setSelectedNode}
        />
      )}
      {query.isLoading && <LoadingOverlay />}
      {query.isError && (
        <ErrorOverlay
          notFound={notFound}
          detail={
            query.error instanceof TangramApiError
              ? query.error.detail
              : "Could not load this diagram."
          }
        />
      )}
    </div>
  );

  return (
    <EditorShell
      content={content}
      diagramName={diagram?.metadata.name ?? "Diagram"}
      componentCount={diagram ? counts.nodes || diagram.nodes.length : 0}
      connectionCount={diagram ? counts.edges || diagram.edges.length : 0}
      savedLabel={
        diagram ? editor.label : query.isLoading ? "loading…" : "—"
      }
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

function LoadingOverlay() {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex flex-col items-center gap-2.5 rounded-[var(--radius-lg)] border border-line bg-card px-7 py-5 shadow-md">
        <Enso size={32} />
        <p className="font-serif text-[17px] font-medium text-ink-strong">
          Loading diagram…
        </p>
      </div>
    </div>
  );
}

function ErrorOverlay({
  notFound,
  detail,
}: {
  notFound: boolean;
  detail: string;
}) {
  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-canvas/85 backdrop-blur-[2px]">
      <div className="flex max-w-md flex-col items-center gap-2.5 rounded-[var(--radius-lg)] border border-line bg-card px-7 py-5 shadow-md">
        <OctagonAlert size={28} className="text-accent" />
        <p className="text-[16px] font-semibold text-ink-strong">
          {notFound ? "Diagram not found" : "Couldn't load diagram"}
        </p>
        <p className="text-center text-[13px] leading-relaxed text-ink-muted">
          {notFound
            ? "It may have been deleted, or the link is wrong."
            : detail}
        </p>
        <Button asChild variant="primary" size="md" className="mt-1">
          <Link href="/library">Back to library</Link>
        </Button>
      </div>
    </div>
  );
}
