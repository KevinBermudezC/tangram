"use client";

import { useChat } from "@ai-sdk/react";
import { DefaultChatTransport } from "ai";
import { ArrowRight, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Streamdown } from "streamdown";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const SUGGESTIONS = [
  "Explain this node",
  "What's missing?",
  "Suggest a queue",
];

interface ChatPanelProps {
  /** Component the user just selected in the canvas — used as chat context. */
  selectedNode?: { name: string; type: string };
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
export function ChatPanel({ selectedNode }: ChatPanelProps) {
  const [input, setInput] = useState("");
  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({ api: "/api/chat" }),
  });

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the latest message.
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

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
        <span className="inline-flex items-center gap-2 text-[13px] font-semibold text-ink-strong">
          <Sparkles size={14} className="text-accent" />
          AI Teaching Assistant
        </span>
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
        {messages.length === 0 ? (
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
