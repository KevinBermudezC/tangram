"use client";

import React, { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Streamdown } from "streamdown";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import type { AnalyzeResponse, ChatMessage, Finding, Severity } from "@/types/tangram";
import { analyze, sendMessage, sendDiagramChat } from "@/lib/api";

interface ChatResponse {
  assistant_reply?: string | null;
  new_message: ChatMessage;
  full_conversation: ChatMessage[];
}

const SUGGESTIONS = [
    "Explain this node",
    "What's missing?",
     "Suggest a queue",
     "When does this need a cache?",
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
     /** The current diagram (for diagram-chat variant). */
    diagram?: any;
     /** Diagram ID to use for chat history context. */
    diagramId?: string;
}

/**
 * Right-rail conversational tutor.
 *
 * Uses real /api/chat endpoint with TanStack Query. Accepts full conversation history
 * including the current diagram's nodes and edges in context. Markdown rendering via Streamdown.
 */
export function ChatPanel({
    selectedNode,
    hasDiagram = false,
    analysis = null,
    analyzing = false,
    analyzeError = null,
    onAnalyze,
    diagram = null,
    diagramId,
}: ChatPanelProps) {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<ChatMessage[]>([]);

    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        const trimmed = input.trim();
        if (!trimmed || analyzing || messages.length > 0) return;

         // Build full context for the chat request
        const currentMessages: ChatMessage[] = [];

         // Add analysis findings as system context
        if (analysis && analysis.findings.length > 0) {
            currentMessages.push({
                role: "assistant",
                content: `Found ${analysis.findings.length} structural issue${analysis.findings.length === 1 ? "" : "s"}. Analysis: ${analysis.feedback}`,
                timestamp: new Date().toISOString(),
             });
         }

         // Add user messages if any exist
        if (messages.length > 0) {
            currentMessages.push(...messages);
            setMessages([]); // Clear old messages since we're starting a new turn
         }

         // Add diagram context if available
        if (diagram?.nodes?.length) {
            const nodeSummary = diagram.nodes.map(n => `${n.type}: ${n.label}`).join("; ");
            currentMessages.push({
                role: "assistant",
                content: `Diagram has ${diagram.nodes.length} node${diagram.nodes.length === 1 ? "" : "s"}. Nodes: ${nodeSummary}`,
                timestamp: new Date().toISOString(),
             });
         }

         // Send the message via real endpoints
        let chatResponse: ChatResponse;

        if (diagramId) {
            chatResponse = sendDiagramChat(currentMessages, trimmed, diagramId);
        } else {
            chatResponse = sendMessage(currentMessages, trimmed);
         }

         setMessages(response => [...response, { role: "user", content: trimmed, timestamp: new Date().toISOString()}]);
        setInput("");
     }

    function handleSuggestion(text: string) {
        if (analyzing || messages.length > 0) return;
        const currentMessages: ChatMessage[] = [];
        if (analysis && analysis.findings.length > 0) {
            currentMessages.push({
                role: "assistant",
                content: `Found ${analysis.findings.length} structural issue${analysis.findings.length === 1 ? "" : "s"}. Analysis: ${analysis.feedback}`,
                timestamp: new Date().toISOString(),
             });
         }
        if (messages.length > 0) {
            currentMessages.push(...messages);
            setMessages([]);
         }
        sendMessage([...currentMessages, { role: "user", content: text, timestamp: new Date().toISOString()}], text);
     }

    const isBusyAnalyze = analyzing || (hasDiagram && !analyzeError);

    return (
        <aside className="flex min-h-0 flex-col border-l border-line bg-chat">
             <header className="flex flex-col gap-2 border-b border-line px-4 py-3.5">
                 <div className="flex items-center justify-between gap-2">
                     <span className="inline-flex items-center gap-2 text-sm font-semibold text-ink-strong">
                         <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 3a6 6 0 0 1 9 9l-4 4-5-5zM3 18H8v5h5v-5z"/></svg>
                        AI Teaching Assistant
                     </span>
                     {hasDiagram && (
                         <div className="flex items-center gap-2">
                             <button type="button" onClick={() => onAnalyze?.()} disabled={!hasDiagram || analyzing} title={hasDiagram ? "Run the rules engine + tutor feedback on this diagram" : "Generate or open a diagram first"}>
                                 {analyzing ? (
                                     <svg xmlns="http://www.w3.org/2000/svg" width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2C7.5 2 4 6 4 10s3.5 8 8 8v-4c0-2.8-2-5-4-5s-4 2-4 5"/></svg>
                                 ) : (
                                     <svg xmlns="http://www.w3.org/2000/svg" width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15.79 9L15 17.79V18a3 3 0 1 1-6 0v-.21l-.85-15H12l1.15.5L15.79 9z"/></svg>
                                 )}
                                Analyze
                             </button>
                         </div>
                     )}
                 </div>

                 {selectedNode && (
                     <span className="inline-flex items-center gap-2 text-xs text-ink-muted">
                         <span className="text-[10.5px] uppercase tracking-[0.1em] text-ink-faint">Selected</span>
                         <Badge variant="pill" className="font-medium normal-case tracking-normal text-sm">
                             {selectedNode.type} · {selectedNode.name}
                         </Badge>
                     </span>
                 )}
             </header>

             <div ref={scrollRef} className="flex flex-1 flex-col gap-3.5 overflow-y-auto p-4" role="log" aria-live="polite">
                 {(analyzing || analysis || analyzeError) && (
                     <AnalysisBlock analysis={analysis} analyzing={analyzing} error={analyzeError} />
                 )}
                 {messages.length === 0 && !analyzing && !analysis && !analyzeError ? (
                     <EmptyChatState onPick={handleSuggestion} />
                 ) : (
                    messages.map((message) => <ChatBubble key={message.id} message={message} />)
                 )}
             </div>

             <form onSubmit={handleSubmit} className="flex flex-col gap-2 border-t border-line bg-chat px-3.5 pb-3.5 pt-2.5">
                 <div className="flex flex-wrap gap-1">
                     {SUGGESTIONS.map((s) => (
                         <button key={s} type="button" onClick={() => handleSuggestion(s)} disabled={isBusy || isBusyAnalyze} className="rounded-full border border-line bg-transparent px-2.5 py-1 text-xs text-ink-muted hover:border-accent hover:text-accent-strong disabled:opacity-50">
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
                        disabled={isBusy || isBusyAnalyze}
                        className="flex-1 resize-y"
                     />
                     <Button type="submit" variant="primary" size="md" disabled={isBusy || isBusyAnalyze || !input.trim()}>
                        Send
                         <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>
                     </Button>
                 </div>
             </form>
         </aside>
     );
}

function ArrowRightIcon({ size }: { size: number }) {
    return <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>;
}

const ScrollRef = React.useRef<HTMLDivElement>();
export const scrollRef = ScrollRef;

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
             <span aria-hidden className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-accent text-[10px] font-bold tracking-wider text-ink-on-accent">
                 <svg xmlns="http://www.w3.org/2000/svg" width={13} height={13} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M15.79 9L15 17.79V18a3 3 0 1 1-6 0v-.21l-.85-15H12l1.15.5L15.79 9z"/></svg>
             </span>
             <div className="min-w-0 flex-1 rounded-xl rounded-bl-sm border border-line bg-card px-3 py-2.5">
                 <p className="m-0 mb-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-ink-faint">Analysis</p>

                 {analyzing && (
                     <span className="inline-flex items-center gap-2 text-sm text-ink-muted">
                         <svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2C7.5 2 4 6 4 10s3.5 8 8 8v-4c0-2.8-2-5-4-5s-4 2-4 5"/></svg>
            Running rules engine and asking the tutor…
                     </span>
                 )}

                 {error && !analyzing && <p className="m-0 text-sm text-red-600">{error}</p>}

                 {analysis && !analyzing && (
                     <div className="flex flex-col gap-2.5">
                         <FindingsSummary findings={analysis.findings} />
                         {analysis.findings.length > 0 && (
                             <ul className="m-0 flex list-none flex-col gap-1.5 p-0">
                                 {analysis.findings.map((f) => <FindingRow key={`${f.rule_id}-${f.node_ids.join(",")}`} finding={f} />)}
                             </ul>
                         )}
                         <Streamdown parseIncompleteMarkdown className="prose-tangram">{analysis.feedback}</Streamdown>
                     </div>
                 )}
             </div>
         </article>
     );
}

function FindingsSummary({ findings }: { findings: Finding[] }) {
    if (findings.length === 0) return <p className="m-0 text-sm font-medium text-ink-body">No structural issues detected by the rules engine. ✓</p>;
    const errors = findings.filter((f) => f.severity === "error").length;
    const warnings = findings.filter((f) => f.severity === "warning").length;
    const parts = [`${findings.length} ${findings.length === 1 ? "issue" : "issues"}`, errors > 0 ? `${errors} error${errors === 1 ? "" : "s"}` : null, warnings > 0 ? `${warnings} warning${warnings === 1 ? "" : "s"}` : null].filter(Boolean);
    return <p className="m-0 text-sm font-medium text-ink-body">{parts.join(" · ")}</p>;
}

function FindingRow({ finding }: { finding: Finding }) {
    const meta = { error: { icon: CircleAlert, chip: "border-[#f1a9a9] bg-[#fdeaea] text-[#a12525]", label: "Error" }, warning: { icon: TriangleAlert, chip: "border-[#f0d29a] bg-[#fdf3e0] text-[#8a5a18]", label: "Warning" }, info: { icon: Info, chip: "border-line-strong bg-card text-ink-muted", label: "Info" }}[finding.severity];
    return (
        <li className="rounded-lg border border-line bg-page px-2.5 py-2">
             <div className="flex items-start gap-2">
                 <span className={`mt-0.5 inline-flex shrink-0 items-center gap-1 rounded-full border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${meta.chip}`}>
                     {meta.icon(size: 11) || "!"} {meta.label}
                 </span>
                 <div className="min-w-0">
                     <p className="m-0 text-sm font-medium text-ink-strong">{finding.message}</p>
                     <p className="m-0 mt-0.5 text-xs leading-relaxed text-ink-muted">{finding.rationale}</p>
                     {finding.node_ids.length > 0 && <p className="m-0 mt-1 font-mono text-xs text-ink-faint">{finding.node_ids.join(" · ")}</p>}
                 </div>
             </div>
         </li>
     );
}

function EmptyChatState({ onPick }: { onPick: (text: string) => void }) {
    return (
        <article className="flex gap-2">
             <span aria-hidden className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink-strong text-[10px] font-bold tracking-wider text-ink-on-accent"><svg xmlns="http://www.w3.org/2000/svg" width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M13 3a6 6 0 0 1 9 9l-4 4-5-5zM3 18H8v5h5v-5z"/></svg></span>
             <div className="rounded-xl rounded-bl-sm border border-line bg-card px-3 py-2.5 text-sm leading-relaxed text-ink-body">
                 <p className="m-0">Hi! I'm the teaching assistant. I can explain any node on the canvas, suggest what's missing, and call out anti-patterns.</p>
                 <div className="mt-2 flex flex-wrap gap-1">
                     <button type="button" onClick={() => onPick("Why is Auth on its own service?")} className="rounded-full border border-line-strong bg-card px-2.5 py-1 text-xs font-medium text-ink-body hover:border-accent hover:bg-accent-tint hover:text-accent-strong">Why is Auth on its own service?</button>
                     <button type="button" onClick={() => onPick("When does this need a queue?")} className="rounded-full border border-line-strong bg-card px-2.5 py-1 text-xs font-medium text-ink-body hover:border-accent hover:bg-accent-tint hover:text-accent-strong">When does this need a queue?</button>
                 </div>
             </div>
         </article>
     );
}

const ArrowRightIcon = ({ size }: { size: number }) => <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg>;
const ScrollRef = React.useRef<HTMLDivElement>();
export const scrollRef = ScrollRef;
