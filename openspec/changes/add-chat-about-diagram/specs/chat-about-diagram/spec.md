## Purpose

Lets a junior talk with the tutor about the diagram on the canvas: selecting a queue or cache and asking why it is there yields an answer about that node, via inspect tools, not a canned keyword reply.

## ADDED Requirements

### Requirement: POST /chat streams a tutor reply as UI Message Stream

The backend SHALL expose `POST /chat` accepting `{ messages, diagram?, diagram_id?, selected_node_id? }` with a non-empty `messages` list. On success it SHALL stream SSE in the UI Message Stream protocol (`text-start` / `text-delta` / `text-end`, plus tool parts when tools run) with header `x-vercel-ai-ui-message-stream: v1`. Inference SHALL use the `tutor` mode and the same retrieval path as `/generate`. The composed prompt SHALL NOT include the diagram's JSON (or an equivalent full dump of nodes and edges); the model SHALL obtain structure only by calling tools.

#### Scenario: Happy path streams assistant text after inspect_node

- **WHEN** the body includes a diagram with a queue node `orders` (label "Orders queue") selected, and the user asks "why is there a queue here?"
- **THEN** the response is 200 `text/event-stream`
- **AND** the stream contains a tool part for `inspect_node`
- **AND** concatenating text deltas names that node and refers to how it is connected

#### Scenario: Diagram JSON is not in the prompt

- **WHEN** a chat request includes a live diagram
- **THEN** the messages sent to the LLM do not contain a serialized dump of that diagram
- **AND** the LLM is given tool definitions for `inspect_diagram` and `inspect_node`

#### Scenario: Empty messages are rejected with 422

- **WHEN** a client POSTs `{"messages": []}`
- **THEN** the response status is 422
- **AND** no LLM call is made

### Requirement: Only inspect_diagram and inspect_node tools exist

The chat tool surface SHALL be exactly `inspect_diagram` (list nodes and edges on the current snapshot) and `inspect_node` (one node by id plus incident edges). Chat SHALL NOT call `POST /analyze` or `POST /generate`. Tools execute against the resolved snapshot on the backend.

#### Scenario: inspect_node returns the selected queue and its edges

- **WHEN** the model calls `inspect_node` with the id of a queue that has an inbound edge from `api` and an outbound edge to `worker`
- **THEN** the tool result includes that node's id, type, and label
- **AND** both incident edges

#### Scenario: inspect_diagram lists the canvas

- **WHEN** the model calls `inspect_diagram` on a snapshot with three nodes
- **THEN** the tool result lists those three nodes and their edges
- **AND** no other tools are registered

#### Scenario: Analyze is not a chat tool

- **WHEN** a contributor inspects the chat tool list
- **THEN** there is no tool that invokes `/analyze` or `/generate`

### Requirement: Live snapshot wins; unsaved canvas works

When `diagram` is present it SHALL be the snapshot tools inspect, even if `diagram_id` is omitted or points elsewhere. `diagram_id` alone SHALL load storage. Chat SHALL NOT persist the diagram or append `Diagram.conversation`.

#### Scenario: Unsaved canvas with selected node

- **WHEN** the body includes a `diagram` and `selected_node_id` and omits `diagram_id`
- **THEN** tools inspect that snapshot
- **AND** storage is not required

#### Scenario: Unknown diagram_id without a live diagram → 404

- **WHEN** a client POSTs a well-formed `diagram_id` with no stored file and omits `diagram`
- **THEN** the response status is 404 with `code` set to `diagram_not_found`
- **AND** no LLM call is made

#### Scenario: Chat does not write storage

- **WHEN** a client POSTs a chat request that includes a diagram
- **THEN** no diagram file is created or modified

### Requirement: Missing diagram or missing node does not invent boxes

When no snapshot is available, the tutor SHALL say it has no diagram and ask for context, without calling the LLM to invent nodes. When `inspect_node` is called with an unknown id, the tool result SHALL be a structured miss and the tutor SHALL NOT invent that node.

#### Scenario: No diagram

- **WHEN** the body has messages but neither `diagram` nor a loadable `diagram_id`
- **THEN** the stream is a 200 UI Message Stream that says there is no diagram and asks the user to open or generate one
- **AND** no LLM call is made

#### Scenario: Unknown node id is a miss

- **WHEN** `inspect_node` is called with an id not on the snapshot
- **THEN** the tool result is a structured miss
- **AND** the chat stream continues (no HTTP 500)

### Requirement: Input validation and LLM error mapping

The endpoint SHALL reject an oversized payload with 413 `chat_input_too_large` and a malformed body with 422 before any LLM call. `LLMError` subclasses SHALL map to the same status/`code` contract as `/generate`.

#### Scenario: Oversized payload is rejected with 413

- **WHEN** serialized messages + diagram exceed `MAX_INPUT_CHARS`
- **THEN** the status is 413 with `code` `chat_input_too_large`
- **AND** no LLM call is made

#### Scenario: LLMConfigError → 503

- **WHEN** the LLM provider is misconfigured
- **THEN** the endpoint returns 503 with `code` `llm_config_error`

### Requirement: Next.js /api/chat is a passthrough and pickReply is gone

`frontend/app/api/chat` SHALL proxy to backend `POST /chat` and SHALL NOT contain canned replies keyed off words such as "auth", "queue", or "cache". `useChat` SHALL keep using `/api/chat`. Each request body SHALL include the live `diagram` when the canvas has one and `selected_node_id` when a node is selected.

#### Scenario: Canned mock is gone

- **WHEN** the latest user text contains `"queue"` or `"auth"`
- **THEN** `/api/chat` does not answer from a hardcoded explainer
- **AND** the backend `/chat` path is invoked

#### Scenario: Selection and snapshot are sent

- **WHEN** the user has a diagram on the canvas and a node selected and sends a chat message
- **THEN** the `/api/chat` JSON body includes that diagram and `selected_node_id`

#### Scenario: Tool chip is minimal

- **WHEN** the stream contains an `inspect_node` tool part whose result has type `queue` and label `Orders`
- **THEN** the rail may show a short chip such as `miró Queue · Orders`
- **AND** assistant Markdown still renders through Streamdown
