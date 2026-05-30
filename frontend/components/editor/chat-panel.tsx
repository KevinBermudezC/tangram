"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import {
  ArrowRight,
  CircleAlert,
  Info,
  Loader2,
  ScanLine,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Streamdown } from "streamdown";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { AnalyzeResponse, Finding, Severity } from "@/types/tangram";

const SUGGESTIONS = [
  "Explain this node",
  "What's missing?",
  "Suggest a queue",
];

interface ChatPanelProps {
  /** Component the user just selected in the canvas — used as chat context. */
  selectedNode?: { name: string; type: string };
  /** The current diagram. Enables the Analyze action when present. */
  hasDiagram?: boolean;
  /** Latest analysis result, or null if none has been run. */
  analysis?: AnalyzeResponse | null;
  /** True while POST /analyze is in flight. */
  analyzing?: boolean;
  /** Human-readable analysis error, or null. */
  analyzeError?: string | null;
  /** Kick off an analysis of the current diagram. */
  onAnalyze?: () => void;
}

/**
 * Right-rail conversational tutor.
 *
 * Backed by `useChat()` from @ai-sdk/react, talking to /api/chat. The route
 * currently returns canned-but-streamed Markdown; once a Tangram backend
 * chat endpoint exists, the route proxies to it without touching this
 * component.
 *
 * Markdown rendering is handled by Streamdown (Vercel) so we get partial-
 * stream rendering for free.
 */
export function ChatPanel({
  selectedNode,
  hasDiagram = false,
  analysis = null,
  analyzing = false,
  analyzeError = null,
  onAnalyze,
}: ChatPanelProps) {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest message or when analysis state changes.
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, analysis, analyzing]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || status === "streaming" || status === "submitted") return;
    void sendMessage({ text: trimmed });
    setInput("");
  }

  function handleSuggestion(text: string) {
    if (status === "streaming" || status === "submitted") return;
    void sendMessage({ text });
  }

  const isBusy = status === "submitted" || status === "streaming";

  return (
    <aside className="flex min-h-0 flex-col border-l border-line bg-chat">
      <header className="flex flex-col gap-2 border-b border-line px-4 py-3.5">
        <div className="flex items-center justify-between gap-2">
          <span className="inline-flex items-center gap-2 text-[13px] font-semibold text-ink-strong">
            <Sparkles size={14} className="text-accent" />
            AI Teaching Assistant
          </span>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={() => onAnalyze?.()}
            disabled={!hasDiagram || analyzing}
            title={
              hasDiagram
                ? "Run the rules engine + tutor feedback on this diagram"
                : "Generate or open a diagram first"
            }
          >
            {analyzing ? (
              <Loader2 size={13} className="animate-spin" />
            ) : (
              <ScanLine size={13} />
            )}
            Analyze
          </Button>
        </div>
        {selectedNode && (
          <span className="inline-flex items-center gap-2 text-[12px] text-ink-muted">
            <span className="text-[10.5px] uppercase tracking-[0.1em] text-ink-faint">
              Selected
            </span>
            <Badge variant="pill" className="font-medium normal-case tracking-normal text-[11.5px]">
              {selectedNode.type} · {selectedNode.name}
            </Badge>
          </span>
        )}
      </header>

      <div
        ref={scrollRef}
        className="flex flex-1 flex-col gap-3.5 overflow-y-auto p-4"
        role="log"
        aria-live="polite"
      >
        {(analyzing || analysis || analyzeError) && (
          <AnalysisBlock
            analysis={analysis}
            analyzing={analyzing}
            error={analyzeError}
          />
        )}
        {messages.length === 0 && !analyzing && !analysis && !analyzeError ? (
          <EmptyChatState onPick={handleSuggestion} />
        ) : (
          messages.map((message) => (
            <ChatBubble key={message.id} message={message} />
          ))
        )}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-2 border-t border-line bg-chat px-3.5 pb-3.5 pt-2.5"
      >
        <div className="flex flex-wrap gap-1.5">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => handleSuggestion(s)}
              disabled={isBusy}
              className="rounded-full border border-line bg-transparent px-2.5 py-1 text-[12px] text-ink-muted hover:border-accent hover:text-accent-strong disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex items-end gap-2">
          <Textarea
            rows={2}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about this architecture…"
            disabled={isBusy}
            className="flex-1 resize-y"
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                e.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <Button
            type="submit"
            variant="primary"
            size="md"
            disabled={isBusy || !input.trim()}
          >
            Send
            <ArrowRight size={14} />
          </Button>
        </div>
      </form>
    </aside>
  );
}

function ChatBubble({ message }: { message: ReturnType<typeof useChat>["messages"][number] }) {
  const isUser = message.role === "user";
  const text =
    message.parts
      ?.filter((p) => p.type === "text")
      .map((p) => ("text" in p ? p.text : ""))
      .join("") ?? "";

  return (
    <article
      className={cn(
        "flex max-w-full gap-2",
        isUser ? "flex-row-reverse self-end max-w-[88%]" : "self-start max-w-[92%]",
      )}
    >
      {!isUser && (
        <span
          aria-hidden
          className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink-strong text-[10px] font-bold tracking-wider text-ink-on-accent"
        >
          AI
        </span>
      )}
      <div
        className={cn(
          "rounded-xl border px-3 py-2.5 text-[13.5px] leading-relaxed",
          isUser
            ? "rounded-br-sm border-[#f1c5ad] bg-[var(--bg-msg-user,#fdebdf)] text-ink-strong"
            : "rounded-bl-sm border-line bg-card text-ink-body",
        )}
      >
        <Streamdown
          parseIncompleteMarkdown
          className="prose-tangram"
          components={{
            blockquote: ({ node: _node, ...props }) => (
              <blockquote
                {...props}
                className="my-1.5 rounded-r-md border-l-[3px] border-accent bg-accent-tint px-3 py-1.5 text-[12.5px] text-accent-strong"
              />
            ),
          }}
        >
          {text}
        </Streamdown>
      </div>
    </article>
  );
}

const SEVERITY_META: Record<
  Severity,
  { icon: typeof CircleAlert; chip: string; label: string }
> = {
  error: {
    icon: CircleAlert,
    chip: "border-[#f1a9a9] bg-[#fdeaea] text-[#a12525]",
    label: "Error",
  },
  warning: {
    icon: TriangleAlert,
    chip: "border-[#f0d29a] bg-[#fdf3e0] text-[#8a5a18]",
    label: "Warning",
  },
  info: {
    icon: Info,
    chip: "border-line-strong bg-card text-ink-muted",
    label: "Info",
  },
};

function AnalysisBlock({
  analysis,
  analyzing,
  error,
}: {
  analysis: AnalyzeResponse | null;
  analyzing: boolean;
  error: string | null;
}) {
  return (
    <article className="flex gap-2">
      <span
        aria-hidden
        className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold tracking-wider text-ink-on-accent"
      >
        <ScanLine size={13} />
      </span>
      <div className="min-w-0 flex-1 rounded-xl rounded-bl-sm border border-line bg-card px-3 py-2.5">
        <p className="m-0 mb-1.5 text-[10.5px] font-semibold uppercase tracking-[0.1em] text-ink-faint">
          Analysis
        </p>

        {analyzing && (
          <span className="inline-flex items-center gap-2 text-[13px] text-ink-muted">
            <Loader2 size={14} className="animate-spin text-accent" />
            Running rules engine and asking the tutor…
          </span>
        )}

        {error && !analyzing && (
          <p className="m-0 text-[13px] text-[#a12525]">{error}</p>
        )}

        {analysis && !analyzing && (
          <div className="flex flex-col gap-2.5">
            <FindingsSummary findings={analysis.findings} />
            {analysis.findings.length > 0 && (
              <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
                {analysis.findings.map((f) => (
                  <FindingRow key={`${f.rule_id}-${f.node_ids.join(",")}`} finding={f} />
                ))}
              </ul>
            )}
            <Streamdown parseIncompleteMarkdown className="prose-tangram">
              {analysis.feedback}
            </Streamdown>
          </div>
        )}
      </div>
    </article>
  );
}

function FindingsSummary({ findings }: { findings: Finding[] }) {
  if (findings.length === 0) {
    return (
      <p className="m-0 text-[13px] font-medium text-ink-body">
        No structural issues detected by the rules engine. ✓
      </p>
    );
  }
  const errors = findings.filter((f) => f.severity === "error").length;
  const warnings = findings.filter((f) => f.severity === "warning").length;
  const parts = [
    `${findings.length} ${findings.length === 1 ? "issue" : "issues"}`,
    errors > 0 ? `${errors} error${errors === 1 ? "" : "s"}` : null,
    warnings > 0 ? `${warnings} warning${warnings === 1 ? "" : "s"}` : null,
  ].filter(Boolean);
  return (
    <p className="m-0 text-[13px] font-medium text-ink-body">{parts.join(" · ")}</p>
  );
}

function FindingRow({ finding }: { finding: Finding }) {
  const meta = SEVERITY_META[finding.severity];
  const Icon = meta.icon;
  return (
    <li className="rounded-lg border border-line bg-page px-2.5 py-2">
      <div className="flex items-start gap-2">
        <span
          className={cn(
            "mt-0.5 inline-flex shrink-0 items-center gap-1 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
            meta.chip,
          )}
        >
          <Icon size={11} />
          {meta.label}
        </span>
        <div className="min-w-0">
          <p className="m-0 text-[12.5px] font-medium text-ink-strong">{finding.message}</p>
          <p className="m-0 mt-0.5 text-[12px] leading-relaxed text-ink-muted">
            {finding.rationale}
          </p>
          {finding.node_ids.length > 0 && (
            <p className="m-0 mt-1 font-mono text-[10.5px] text-ink-faint">
              {finding.node_ids.join(" · ")}
            </p>
          )}
        </div>
      </div>
    </li>
  );
}

function EmptyChatState({ onPick }: { onPick: (text: string) => void }) {
  return (
    <article className="flex gap-2">
      <span
        aria-hidden
        className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink-strong text-[10px] font-bold tracking-wider text-ink-on-accent"
      >
        AI
      </span>
      <div className="rounded-xl rounded-bl-sm border border-line bg-card px-3 py-2.5 text-[13.5px] leading-relaxed text-ink-body">
        <p className="m-0">
          Hi! I'm the teaching assistant. I can explain any node on the
          canvas, suggest what's missing, and call out anti-patterns.
        </p>
        <div className="mt-2 flex flex-wrap gap-1.5">
          <button
            type="button"
            onClick={() => onPick("Why is Auth on its own service?")}
            className="rounded-full border border-line-strong bg-card px-2.5 py-1 text-[12px] font-medium text-ink-body hover:border-accent hover:bg-accent-tint hover:text-accent-strong"
          >
            Why is Auth on its own service?
          </button>
          <button
            type="button"
            onClick={() => onPick("When does this need a queue?")}
            className="rounded-full border border-line-strong bg-card px-2.5 py-1 text-[12px] font-medium text-ink-body hover:border-accent hover:bg-accent-tint hover:text-accent-strong"
          >
            When does this need a queue?
          </button>
        </div>
      </div>
    </article>
  );
}
