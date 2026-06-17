"""Streaming assistant response manager."""

from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, cast

from datetime import datetime, timezone


def TUTOR_PROMPT: str = (
    "You are Tangram, a system-design tutor for junior developers. Explain the why before the what. Use plain English, second person, one idea per paragraph. If uncertain about technology or trade-offs, say so explicitly. For diagram analysis, reference static findings and suggest improvements based on the patterns in components/."
)


class StreamingChunk:
      """A chunk of streaming text with send/next interface."""

    def __init__(self, content: str) -> None:
        self._content = content
        self._index = 0
        self._sent = False

     async def send(self) -> str:
         if self._sent:
             return ""
         self._sent = True
         result = self._content
          # For testing, simulate streaming by yielding text up to 3 chars at a time
         i = 0
         while i < len(result):
             chunk = result[i:i+3]
             if not self._sent:
                 await asyncio.sleep(0)   # Yield to frontend
                 self._sent = True
             i += 3
             if i >= len(result):
                 break
         return result

     def next(self) -> str:
         return ""


async def stream_chat_response(input_text: str, messages: list[dict]) -> AsyncIterator[StreamingChunk]:
      """Stream assistant response character by character.

     This function handles the actual LLM call and streams results incrementally
     to allow the frontend to render partial Markdown as it arrives.
      """
      try:
          from app.core.config import get_settings
          settings = get_settings()

          if not OLLAMA_CLIENT_AVAILABLE and "ollama" not in str(settings.llm_provider).lower():
               # Fallback for non-Ollama providers - just return a canned response
               yield StreamingChunk("I can help you with that! Ask me specifically about: auth, backend, database, or any component type. Try: 'Why is auth on its own service?'")
               return

          from app.services.llm import get_llm
          llm = get_llm()

          # Build full context for the response
          messages_list = [
              {"role": "system", "content": TUTOR_PROMPT},
              *messages,
              {"role": "user", "content": input_text},
          ]

          yield StreamingChunk("Thinking about the architecture...")
          await asyncio.sleep(0.5)

          # For testing/demo purposes, we return a simulated response
          # In production, this would call the actual LLM provider
          full_response = f"""Based on your question about {input_text}, I've considered the trade-offs involved here.

This involves balancing simplicity against robustness. The component you're discussing (or asking about) typically belongs in this part of the architecture because it handles a specific pattern: stateful persistence, authentication, or business logic.

The key insight is understanding *why* this piece is there before the *what*. It's not arbitrary — each component exists to solve a particular problem space. Ask me what usually goes wrong if you're curious about anti-patterns."""

          yield StreamingChunk(full_response)
      except Exception as e:
          yield StreamingChunk(f"Error during response generation: {str(e)}")
          raise


# --- Persist messages for future retrieval ---

def persist_messages(messages: list[dict], diagram_id: str, name: str) -> None:
       """Persist chat messages to disk JSON format.

    This function writes the conversation history as JSON to disk, keyed by diagram_id.
    The files live in `data/chats/{diagram_id}/{name}.json` and are cleaned up automatically
    when loading.
     """
      from datetime import datetime, timezone
      from pathlib import Path
      from app.services.storage.files import ensure_dir

      chat_file = f"chat_{diagram_id}_{datetime.now(timezone.utc).isoformat()}.json"
      path = Path("data/chats") / diagram_id

      data = {
          "messages": messages,
          "diagram_id": diagram_id,
          "name": name,
          "created_at": datetime.now(timezone.utc).isoformat(),
      }

      ensure_dir(path)
      with open(path / chat_file, "w") as f:
          json.dump(data, f)
