## 1. Schemas and LLM stream_parts

- [x] 1.1 Extend `app/schemas/chat.py` with `ChatRequest` (`messages`, `diagram?`, `diagram_id?`, `selected_node_id?`), tool-capable `ChatMessage`, and `ChatStreamPart`; tests in `tests/test_chat_schema.py`
- [x] 1.2 Add `stream_parts` to `LLMProvider`; implement on Ollama, OpenAI, Anthropic; update `FakeLLMProvider` (scripted multi-step tool then text) and `tests/test_llm_contract.py`
- [ ] 1.3 Verify `tests/test_route_generate.py` and `tests/test_route_analyze.py` still pass

## 2. Chat service and POST /chat

- [x] 2.1 Chat service: resolve snapshot (live wins), `compose_prompt(..., diagram=None)`, tool loop for `inspect_diagram` / `inspect_node` only, no diagram JSON in the prompt, no storage writes
- [x] 2.2 Deterministic no-diagram UI Message Stream (no LLM); unknown node → structured miss
- [x] 2.3 `POST /chat` streams UI Message Stream (`x-vercel-ai-ui-message-stream: v1`); 413 `chat_input_too_large`; 404 `diagram_not_found`; LLM errors mapped like `/generate`
- [ ] 2.4 Tests: inspect_node stream names the selected queue; prompt has no diagram dump; no-diagram refusal; empty 422; oversized 413; unknown id 404; no persistence; LLM error mapping

## 3. Frontend passthrough and wiring

- [x] 3.1 Rewrite `frontend/app/api/chat/route.ts` as passthrough; delete `pickReply` and canned keyword replies
- [x] 3.2 Wire canvas selection + live diagram into `ChatPanel` transport body (`diagram`, `diagram_id`, `selected_node_id`)
- [x] 3.3 Minimal tool chip (`miró {type} · {label}`) from inspect_node parts; Streamdown still renders text
- [x] 3.4 Tests: route has no pickReply; ChatPanel request body includes snapshot + selected_node_id

## 4. Docs

- [x] 4.1 `POST /chat` section in `backend/README.md` with curl
- [x] 4.2 `frontend/README.md` chat section + ROADMAP item #17

## 5. Verification

- [x] 5.1 `ruff format --check` and `ruff check` clean in `backend/`
- [ ] 5.2 `pytest` clean in `backend/`
- [ ] 5.3 `pnpm lint`, `pnpm typecheck`, `pnpm test` clean in `frontend/`
- [ ] 5.4 `openspec validate add-chat-about-diagram --strict`
