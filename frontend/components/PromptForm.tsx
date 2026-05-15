"use client";

import { FormEvent, useState } from "react";

interface PromptFormProps {
  onSubmit: (prompt: string) => void | Promise<void>;
  loading: boolean;
  disabled?: boolean;
}

export function PromptForm({ onSubmit, loading, disabled }: PromptFormProps) {
  const [prompt, setPrompt] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed || loading) return;
    void onSubmit(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <label htmlFor="prompt" className="text-sm font-medium text-gray-700">
        Describe a system you want to design
      </label>
      <textarea
        id="prompt"
        name="prompt"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="e.g. I want to build a food delivery app"
        rows={3}
        disabled={loading || disabled}
        className="w-full rounded border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:cursor-not-allowed disabled:bg-gray-100"
      />
      <button
        type="submit"
        disabled={loading || disabled || !prompt.trim()}
        className="self-start rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
      >
        {loading ? "Generating..." : "Generate diagram"}
      </button>
    </form>
  );
}
