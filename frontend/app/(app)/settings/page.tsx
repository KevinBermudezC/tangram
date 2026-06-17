import { Construction } from "lucide-react";

import { Card } from "@/components/ui/card";

/**
 * Settings — placeholder.
 *
 * The shape we have in mind:
 *   - LLM provider selection (Ollama / OpenAI / Anthropic) + model picker
 *   - BYOK fields for OpenAI / Anthropic
 *   - Data directory + Chroma path
 *   - Theme (light / dark / system)
 *
 * For now everything still lives in `backend/.env`; this page exists so
 * the rail link doesn't 404.
 */
export default function SettingsPage() {
  return (
    <main className="flex flex-col gap-6 p-8">
      <header className="flex flex-col gap-1">
        <div className="flex items-baseline gap-2.5">
          <h1 className="font-serif text-[24px] font-medium tracking-tight text-ink-strong">
            Settings
          </h1>
          <span aria-hidden className="font-serif text-[17px] text-ink-faint">
            設
          </span>
        </div>
        <p className="text-[13px] text-ink-muted">
          Configure LLM provider, keys, storage paths, and theme.
        </p>
      </header>

      <Card className="flex flex-col items-center gap-3 p-10 text-center">
        <span
          aria-hidden
          className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-dashed border-line-strong text-ink-faint"
        >
          <Construction size={18} />
        </span>
        <p className="font-serif text-[18px] font-medium tracking-wide text-ink-strong">
          Under construction
        </p>
        <p className="max-w-md text-[12.5px] leading-relaxed text-ink-muted">
          Settings are read from <code>backend/.env</code> for now. A UI for
          provider / keys / theme / data paths is coming in a future change.
        </p>
      </Card>
    </main>
  );
}
