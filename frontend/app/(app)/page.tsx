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
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden px-8">
      {/* Ma — a faint oversized kanji watermark holds the negative space. */}
      <span
        aria-hidden
        className="pointer-events-none absolute -right-[4vw] top-1/2 -translate-y-1/2 select-none font-serif text-[40vh] font-bold leading-none text-ink-strong/[0.025]"
      >
        巧
      </span>

      <div className="relative -mt-[8vh] flex w-full max-w-[680px] flex-col items-center gap-7">
        <header
          className="tg-enter flex flex-col items-center gap-5"
          style={{ animationDelay: "60ms" }}
        >
          <span className="inline-flex items-center gap-2.5 text-[11px] font-medium uppercase tracking-[0.32em] text-ink-faint">
            <span aria-hidden className="seal h-[18px] w-[18px] text-[10px]">
              巧
            </span>
            System design, taught
          </span>
          <h1 className="text-balance text-center font-serif text-[40px] font-medium leading-[1.15] tracking-[-0.01em] text-ink-strong">
            What do you want to design?
          </h1>
        </header>

        <Card
          className="tg-enter w-full p-3.5"
          style={{ animationDelay: "160ms" }}
        >
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
              <div className="flex flex-wrap items-center gap-1.5">
                <span
                  aria-hidden
                  className="mr-0.5 font-serif text-[13px] text-accent"
                  title="examples"
                >
                  例
                </span>
                {EXAMPLES.slice(0, 3).map((example) => (
                  <button
                    key={example}
                    type="button"
                    onClick={() => setPrompt(example)}
                    className="rounded-[var(--radius-sm)] border border-line bg-card px-2.5 py-1 text-[12.5px] text-ink-body transition-colors hover:border-accent hover:bg-accent-tint hover:text-accent-strong"
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

        <p
          className="tg-enter max-w-[540px] text-center text-[12.5px] leading-relaxed text-ink-faint"
          style={{ animationDelay: "260ms" }}
        >
          Diagrams live as JSON in <code>data/diagrams/</code>. The AI teaches
          as you build — click any node in the editor to ask why it's there.
        </p>
      </div>
    </main>
  );
}
