# Diagram Schema — v0.1.0

> Single source of truth for the diagram data model.
> Editor, AI copilot, database, and API contracts all derive from this.

## Principles

1. **Schema-Driven Development.** Pydantic models (in `/backend/app/models/`) are canonical. TypeScript types and JSON Schemas are auto-generated from them.
2. **Closed enums for `type`.** A small, fixed set of component types lets the AI reason cleanly and the UI render consistently. Custom types are a Phase 2 feature.
3. **Separation of concerns inside each node/edge.**
   - `properties`: human-edited attributes (technology, notes).
   - `ai`: assistant-generated explanations (editable but origin-tagged).
   - `position`: layout metadata for the editor.
4. **Embedded conversation.** The chat history with the copilot lives inside the diagram document. A diagram is a self-contained artifact.

## Component types (v0)

| Type              | Description                                       |
| ----------------- | ------------------------------------------------- |
| `frontend`        | Web/mobile/desktop client                          |
| `backend`         | API service, business logic                       |
| `database`        | Persistent storage (SQL, NoSQL)                   |
| `auth`            | Authentication / authorization service           |
| `storage`         | Object/file storage (S3, etc.)                    |
| `external_service`| Third-party API or SaaS                           |
| `queue`           | Message broker / job queue                        |
| `cache`           | In-memory cache (Redis, etc.)                     |

> 8 types total. We initially aimed for 6–7 but `queue` and `cache` are
> hard to omit even at MVP — most non-trivial systems need them.

## Example — "Delivery app"

```jsonc
{
  "version": "0.1.0",
  "id": "01HXYZ...",
  "metadata": {
    "name": "Delivery app",
    "description": "Generated from: 'I want to build a delivery app'",
    "createdAt": "2026-05-09T14:30:00Z",
    "updatedAt": "2026-05-09T14:32:10Z"
  },
  "nodes": [
    {
      "id": "n_client",
      "type": "frontend",
      "label": "Customer mobile app",
      "position": { "x": 80, "y": 240 },
      "properties": {
        "technology": "React Native",
        "notes": "iOS + Android"
      },
      "ai": {
        "explanation": "The customer-facing app. Shows the menu, lets users place orders, and tracks delivery in real time.",
        "rationale": "Mobile because users will order on the go — a web-only client would miss most of the use case.",
        "confidence": 0.92
      }
    },
    {
      "id": "n_api",
      "type": "backend",
      "label": "Orders API",
      "position": { "x": 420, "y": 240 },
      "properties": {
        "technology": "Node.js / Express"
      },
      "ai": {
        "explanation": "The brain of the system. Receives orders, validates them, and orchestrates the rest.",
        "rationale": "Centralizing order logic here keeps the mobile app thin and makes future clients (web, partner integrations) easier.",
        "confidence": 0.88
      }
    },
    {
      "id": "n_db",
      "type": "database",
      "label": "Orders DB",
      "position": { "x": 760, "y": 240 },
      "properties": {
        "technology": "PostgreSQL"
      },
      "ai": {
        "explanation": "Stores users, restaurants, orders, and their state transitions.",
        "rationale": "Relational fits well: orders, items, and users have clear relationships and need transactional integrity.",
        "confidence": 0.9
      }
    },
    {
      "id": "n_auth",
      "type": "auth",
      "label": "Auth service",
      "position": { "x": 420, "y": 60 },
      "properties": {
        "technology": "Auth0"
      },
      "ai": {
        "explanation": "Handles sign-up, login, and issues tokens the API trusts.",
        "rationale": "Outsourcing auth to a managed provider avoids reinventing security primitives — a common trap for early-stage products.",
        "confidence": 0.85
      }
    },
    {
      "id": "n_queue",
      "type": "queue",
      "label": "Delivery jobs",
      "position": { "x": 760, "y": 440 },
      "properties": {
        "technology": "Redis + BullMQ"
      },
      "ai": {
        "explanation": "Queues background jobs: notifying restaurants, dispatching couriers, sending push notifications.",
        "rationale": "Decouples slow side-effects from the order request — the user gets a fast response while the work happens behind the scenes.",
        "confidence": 0.8
      }
    },
    {
      "id": "n_maps",
      "type": "external_service",
      "label": "Maps & routing",
      "position": { "x": 80, "y": 440 },
      "properties": {
        "technology": "Google Maps API"
      },
      "ai": {
        "explanation": "Provides addresses, geocoding, and ETAs for couriers.",
        "rationale": "Building maps in-house is years of work — using a battle-tested provider is the right call until you have a specific reason not to.",
        "confidence": 0.95
      }
    }
  ],
  "edges": [
    {
      "id": "e_client_api",
      "source": "n_client",
      "target": "n_api",
      "label": "HTTPS / REST",
      "properties": { "protocol": "HTTPS", "dataFlow": "bidirectional" },
      "ai": {
        "explanation": "The app sends orders and reads state from the API."
      }
    },
    {
      "id": "e_api_db",
      "source": "n_api",
      "target": "n_db",
      "label": "SQL",
      "properties": { "protocol": "TCP", "dataFlow": "bidirectional" },
      "ai": { "explanation": "The API persists and queries data." }
    },
    {
      "id": "e_client_auth",
      "source": "n_client",
      "target": "n_auth",
      "label": "OAuth2",
      "properties": { "protocol": "HTTPS", "dataFlow": "bidirectional" }
    },
    {
      "id": "e_api_auth",
      "source": "n_api",
      "target": "n_auth",
      "label": "verify token",
      "properties": { "protocol": "HTTPS", "dataFlow": "unidirectional" }
    },
    {
      "id": "e_api_queue",
      "source": "n_api",
      "target": "n_queue",
      "label": "enqueue job",
      "properties": { "dataFlow": "unidirectional" }
    },
    {
      "id": "e_api_maps",
      "source": "n_api",
      "target": "n_maps",
      "label": "geocode / route",
      "properties": { "protocol": "HTTPS", "dataFlow": "bidirectional" }
    }
  ],
  "conversation": [
    {
      "role": "user",
      "content": "I want to build a delivery app",
      "timestamp": "2026-05-09T14:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Generated a baseline architecture. I included a queue because most delivery systems need to decouple courier dispatch from the order request — happy to explain why if useful.",
      "timestamp": "2026-05-09T14:30:04Z"
    }
  ]
}
```

## Field reference

### Top level

| Field          | Type                | Required | Notes                                         |
| -------------- | ------------------- | -------- | --------------------------------------------- |
| `version`      | string (semver)     | yes      | Schema version. Allows migrations later.      |
| `id`           | string (ULID/UUID)  | yes      | Unique diagram identifier.                    |
| `metadata`     | object              | yes      | Name, description, timestamps.                |
| `nodes`        | array<Node>         | yes      | At least one node for a meaningful diagram.   |
| `edges`        | array<Edge>         | yes      | Can be empty.                                 |
| `conversation` | array<Message>      | no       | Chat history with the copilot.                |

### Node

| Field        | Type                  | Required | Notes                                       |
| ------------ | --------------------- | -------- | ------------------------------------------- |
| `id`         | string                | yes      | Unique within the diagram.                  |
| `type`       | enum (see above)      | yes      | Closed set in v0.                           |
| `label`      | string                | yes      | Human-readable name.                        |
| `position`   | `{ x, y }` numbers    | yes      | Editor layout.                              |
| `properties` | object                | no       | Free-form, human-edited.                    |
| `ai`         | object                | no       | `{ explanation, rationale?, confidence? }`. |

### Edge

| Field        | Type    | Required | Notes                                             |
| ------------ | ------- | -------- | ------------------------------------------------- |
| `id`         | string  | yes      |                                                   |
| `source`     | string  | yes      | Source node id.                                   |
| `target`     | string  | yes      | Target node id.                                   |
| `label`      | string  | no       | Short description (e.g. "HTTPS / REST").          |
| `properties` | object  | no       | `{ protocol?, dataFlow? }`.                       |
| `ai`         | object  | no       | `{ explanation? }`.                               |

### Message

| Field       | Type            | Required | Notes                          |
| ----------- | --------------- | -------- | ------------------------------ |
| `role`      | `user` \| `assistant` | yes |                                |
| `content`   | string          | yes      |                                |
| `timestamp` | ISO 8601 string | yes      |                                |

## What's intentionally NOT in v0

- **Validation results / errors.** Computed at runtime, not persisted.
- **Change history / versioning.** Phase 2.
- **Multi-user / collaboration / permissions.** Phase 2 or 3.
- **Custom component types.** Phase 2.
- **Layout algorithms / auto-arrange metadata.** Editor concern only.
- **Cost estimates / SLA annotations.** Phase 3.

## Open questions

- Should `conversation` live inside the diagram or be a separate document keyed by `diagramId`? Embedded is simpler today but may bloat the doc.
- `confidence` on AI fields — useful signal or noise? Easy to leave optional and decide later.
- Do we need `groups` / `subsystems` for visual clustering at MVP, or wait for Phase 2?
