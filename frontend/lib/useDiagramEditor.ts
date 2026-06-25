"use client";

import type { Edge, Node } from "@xyflow/react";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { flowToDiagram } from "@/lib/flowToDiagram";
import { useSaveDiagram } from "@/lib/hooks";
import type { Diagram } from "@/types/tangram";

export type SaveStatus = "idle" | "editing" | "saving" | "saved" | "error";

const AUTOSAVE_MS = 800;

/**
 * A semantic signature of the graph — ids, types, labels, rounded positions,
 * and edges. Deliberately excludes React Flow's internal bookkeeping
 * (measured dimensions, selection) so that mounting/fit-view/measurement does
 * NOT look like a user edit.
 */
function graphSignature(nodes: Node[], edges: Edge[]): string {
  const n = nodes
    .map((node) => {
      const d = (node.data ?? {}) as Record<string, unknown>;
      return `${node.id}:${d.tangramType ?? ""}:${d.label ?? ""}:${Math.round(
        node.position.x,
      )},${Math.round(node.position.y)}`;
    })
    .sort()
    .join("|");
  const e = edges
    .map((edge) => `${edge.id}:${edge.source}>${edge.target}:${edge.label ?? ""}`)
    .sort()
    .join("|");
  return `${n}#${e}`;
}

/**
 * Save orchestration for the editable canvas.
 *
 * `onChange` receives the live React Flow graph on every mutation; an idle
 * debounce serializes it (`flowToDiagram`) and upserts via `POST /diagrams`.
 * `saveNow` flushes immediately (the topbar Save button). Both share one save
 * path so autosave and manual save can't diverge. A brand-new empty draft is
 * not persisted until it has at least one node.
 */
export function useDiagramEditor(base: Diagram | null) {
  const save = useSaveDiagram();
  const baseRef = useRef<Diagram | null>(base);
  const latest = useRef<{ nodes: Node[]; edges: Edge[] } | null>(null);
  const primedFor = useRef<string | null>(null);
  const savedSig = useRef<string>("");
  const dirtyRef = useRef(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const [status, setStatus] = useState<SaveStatus>("idle");
  const [dirty, setDirty] = useState(false);

  const mounted = useRef(true);
  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    baseRef.current = base;
  }, [base]);

  const doSave = useCallback(() => {
    const b = baseRef.current;
    if (!b || !latest.current || !dirtyRef.current) return;
    // Don't persist an empty draft — wait until it has content.
    if (latest.current.nodes.length === 0) return;
    const diagram = flowToDiagram(latest.current.nodes, latest.current.edges, b);
    setStatus("saving");
    savedSig.current = graphSignature(latest.current.nodes, latest.current.edges);
    save.mutate(diagram, {
      onSuccess: () => {
        dirtyRef.current = false;
        if (!mounted.current) return;
        setDirty(false);
        setStatus("saved");
      },
      onError: () => {
        if (!mounted.current) return;
        setStatus("error");
        toast.error("Save failed", { description: "Your changes aren't saved." });
      },
    });
  }, [save]);

  const onChange = useCallback(
    (nodes: Node[], edges: Edge[]) => {
      latest.current = { nodes, edges };
      const id = baseRef.current?.id ?? null;
      const sig = graphSignature(nodes, edges);

      // First report after (re)seeding a diagram establishes the clean baseline.
      if (primedFor.current !== id) {
        primedFor.current = id;
        savedSig.current = sig;
        dirtyRef.current = false;
        setDirty(false);
        return;
      }

      // No semantic change (e.g. React Flow measuring/selecting) → still clean.
      if (sig === savedSig.current) {
        if (dirtyRef.current) {
          dirtyRef.current = false;
          setDirty(false);
        }
        return;
      }

      dirtyRef.current = true;
      setDirty(true);
      setStatus("editing");
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => {
        timer.current = null;
        doSave();
      }, AUTOSAVE_MS);
    },
    [doSave],
  );

  const saveNow = useCallback(() => {
    if (timer.current) {
      clearTimeout(timer.current);
      timer.current = null;
    }
    doSave();
  }, [doSave]);

  // Flush a pending save on real unmount only. doSave is read through a ref so
  // this effect doesn't re-run (and re-flush) every render.
  const flushRef = useRef(saveNow);
  flushRef.current = saveNow;
  useEffect(() => {
    return () => {
      if (timer.current) flushRef.current();
    };
  }, []);

  const label =
    status === "saving"
      ? "saving…"
      : status === "saved" && !dirty
        ? "saved · just now"
        : status === "error"
          ? "save failed"
          : dirty
            ? "unsaved changes"
            : "—";

  return {
    onChange,
    saveNow,
    status,
    dirty,
    canSave: dirty && status !== "saving",
    label,
  };
}
