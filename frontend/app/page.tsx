"use client";

import { useState } from "react";

import { DiagramCanvas } from "@/components/DiagramCanvas";
import { PromptForm } from "@/components/PromptForm";
import { generate, TangramApiError } from "@/lib/api";
import type { Diagram } from "@/types/tangram";

interface ErrorState {
  message: string;
  code: string;
}

export default function HomePage() {
  const [diagram, setDiagram] = useState<Diagram | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ErrorState | null>(null);

  async function handleGenerate(prompt: string) {
    setLoading(true);
    setError(null);
    setDiagram(null);
    try {
      const result = await generate(prompt);
      setDiagram(result);
    } catch (err) {
      if (err instanceof TangramApiError) {
        setError({ message: err.detail, code: err.code });
      } else if (err instanceof Error) {
        setError({ message: err.message, code: "network_error" });
      } else {
        setError({ message: "Unknown error", code: "unknown_error" });
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-4 py-8">
      <header>
        <h1 className="text-2xl font-bold text-gray-900">Tangram</h1>
        <p className="text-sm text-gray-600">
          Describe a system. Get a diagram. Learn the why.
        </p>
      </header>

      <section className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
        <PromptForm onSubmit={handleGenerate} loading={loading} />
      </section>

      {error && (
        <section
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <p className="font-semibold">Generation failed</p>
          <p className="mt-1">{error.message}</p>
          <p className="mt-1 text-xs text-red-700">
            Code: <code className="font-mono">{error.code}</code>
          </p>
        </section>
      )}

      {diagram && (
        <section
          aria-label="Generated diagram"
          className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm"
          style={{ height: "560px" }}
        >
          <DiagramCanvas diagram={diagram} />
        </section>
      )}

      {!diagram && !error && !loading && (
        <section className="rounded-lg border border-dashed border-gray-300 bg-white p-8 text-center text-sm text-gray-500">
          <p>Your diagram will appear here.</p>
          <p className="mt-1 text-xs">
            Backend at{" "}
            <code className="font-mono">
              {process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}
            </code>
          </p>
        </section>
      )}
    </main>
  );
}
