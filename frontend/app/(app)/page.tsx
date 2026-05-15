"use client";

import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const EXAMPLES = [
  "Food delivery app with realtime tracking",
  "Twitter clone with notifications",
  "E-commerce checkout",
  "URL shortener",
];

/**
 * Home — v0-style.
 *
 * Single big centered prompt that hands off to the editor with the prompt
 * pre-filled (via search params). The library + filters live behind the
 * "Library" rail item.
 */
export default function HomePage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed) return;
    router.push(`/editor?prompt=${encodeURIComponent(trimmed)}`);
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-8">
      <div className="-mt-[8vh] flex w-full max-w-[720px] flex-col items-center gap-4">
        <h1 className="text-center text-[32px] font-semibold tracking-tight text-ink-strong">
          What do you want to design?
        </h1>

        <Card className="w-full p-3.5">
          <form
            className="flex flex-col gap-2.5"
            onSubmit={handleSubmit}
          >
            <Textarea
              rows={3}
              autoFocus
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe an architecture — e.g. a food delivery app with realtime tracking…"
              className="min-h-20 border-0 bg-transparent px-1.5 py-1 text-[15px] shadow-none focus-visible:border-0 focus-visible:ring-0"
            />
            <div className="flex flex-wrap items-center justify-between gap-2.5">
              <div className="flex flex-wrap gap-1.5">
                {EXAMPLES.slice(0, 3).map((example) => (
                  <button
                    key={example}
                    type="button"
                    onClick={() => setPrompt(example)}
                    className="rounded-full border border-line bg-sidebar px-2.5 py-1 text-[12.5px] text-ink-body transition-colors hover:border-accent hover:bg-accent-tint hover:text-accent-strong"
                  >
                    {example.split(" ").slice(0, 2).join(" ")}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <Button asChild variant="secondary" size="sm">
                  <a href="/editor">Blank canvas</a>
                </Button>
                <Button type="submit" variant="primary" size="sm" disabled={!prompt.trim()}>
                  Generate
                  <ArrowRight size={14} />
                </Button>
              </div>
            </div>
          </form>
        </Card>

        <p className="max-w-[540px] text-center text-[12.5px] leading-relaxed text-ink-faint">
          Diagrams live as JSON in <code>data/diagrams/</code>. The AI teaches
          as you build — click any node in the editor to ask why it's there.
        </p>
      </div>
    </main>
  );
}
