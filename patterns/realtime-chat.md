---
id: realtime-chat
title: Realtime Chat
complexity: intermediate
tags:
  - realtime
  - websockets
component_types:
  - frontend
  - backend
  - database
  - auth
  - queue
  - external_service
---

# Realtime Chat

## What it is

A system where multiple users see each other's messages **without refreshing**. The defining feature is bidirectional push: the server delivers messages to clients as they happen, not when clients ask. Realtime chat covers DMs, group threads, support widgets, multiplayer cursors in design tools, live-collaboration features in docs, and so on.

The thing that makes "realtime chat" architecturally distinct from a normal CRUD app is **the long-lived connection** (websockets, server-sent events, or a managed push service) and the need to **fan out a single message to many recipients fast**.

## When to use

- The product is **fundamentally about people talking to each other**: Slack, Discord, Intercom, your support widget, multiplayer apps.
- A delay of more than a few seconds between sending and receiving would feel broken.
- Online presence ("alice is typing", "bob is online") is a feature you'll ship.
- You need delivery to multiple recipients per message and you can afford the operational complexity.

## When to avoid

- The feature would work just as well with **polling every few seconds**. Notifications, alerts, inbox indicators — these often don't need true realtime. Polling is dramatically simpler.
- You have **one or two users** in early MVP. Build the CRUD version first, layer realtime on once messages-per-second is a real number.
- You're trying to use realtime for **data sync across devices** of the same user. There are better patterns for that (CRDTs, event sourcing) than treating it as chat.
- The team has no experience with long-lived connections. Realtime chat is unforgiving once it breaks; expect a learning curve.

## Components involved

- **Frontend** — maintains a websocket or SSE connection to the backend (or to a managed push service). Renders messages as they arrive. Handles reconnection on network blips.
- **Backend** — accepts websocket connections, authenticates them, routes messages to the right recipients. Often two flavors: the regular HTTP API for history / settings, and a dedicated websocket server for the live channel. They share the same database.
- **Database** — persists messages, channels, memberships. Reads are heavy on history queries; design indexes for that.
- **Auth** — required. Websocket connections must authenticate (token in the connect handshake, then re-validated). Authorization checks happen on every message receive AND every message send.
- **Queue** — fan-out of messages to many recipients often goes through a queue or pub/sub bus. Especially important when backend instances are horizontally scaled: a message arriving at instance A must reach a user connected to instance B.
- **External services** — for production-grade chat, many teams use a managed service (Pusher, Ably, PubNub, Stream Chat) instead of running their own websocket fleet. The architecture stays the same; the backend talks to the external service instead of pushing directly.

## Common pitfalls

- **Authenticating once on connect, never again.** Tokens expire; permissions change. Re-check authorization on every message — at minimum, every receive — or you'll leak messages to users who got demoted.
- **Storing the entire message history in the frontend** of a long-lived chat. Memory grows unbounded. Paginate aggressively, drop old messages from the client cache.
- **Running websocket connections through a load balancer that doesn't support them.** Many ALB / proxy default configs kill long-lived connections after some idle timeout. Configure for sticky long connections.
- **Treating presence as authoritative state in the database.** Presence is ephemeral; writing it to your main DB on every heartbeat melts you. Use Redis or a pub/sub channel.
- **Trying to deliver "exactly once" to the client.** Networks lose packets. Clients reconnect. Accept that the same message will sometimes arrive twice and deduplicate on the receiving side using a message id.
- **No backpressure on broadcast.** A 1,000-member channel where one user spams 50 messages a second can take down everyone listening if you don't rate-limit per-channel.
