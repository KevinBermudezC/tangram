---
id: event-driven
title: Event-Driven Architecture
complexity: advanced
tags:
  - async
  - microservices
  - decoupling
component_types:
  - frontend
  - backend
  - queue
  - database
  - external_service
---

# Event-Driven Architecture

## What it is

A system where services **communicate by emitting and consuming events** rather than by calling each other directly. When something interesting happens — a user signs up, an order is placed, a file is uploaded — the originating service publishes an event ("OrderPlaced"). Other services subscribe to that event and react: send an email, update inventory, kick off a workflow. The publisher doesn't know who's listening.

Compare to a traditional request/response architecture where the order service explicitly calls the email service, the inventory service, the analytics service, and the notification service synchronously. Event-driven inverts that: the order service announces what happened and lets interested parties react on their own time.

This pattern is closely related to microservices but is not the same thing. You can have an event-driven monolith. You can have RPC-style microservices. Event-driven is about *how services communicate*; microservices is about *how services are deployed*.

## When to use

- You have **multiple subsystems that need to react to the same business events** and that list keeps growing. Hardcoding every consumer into the originator becomes intolerable.
- The reactions are **non-blocking for the user**: emails, analytics, downstream sync. The user shouldn't wait for them.
- You want **decoupled team ownership**: team A owns orders, team B owns notifications, team C owns analytics. They share the event contract, not the database.
- The business logic itself is naturally described as "when X happens, Y and Z follow", and you want the architecture to mirror that.

## When to avoid

- You have **one or two services** that talk to each other and the calls are simple. A direct HTTP call is dramatically easier to reason about. Don't event-driven your way into needing a debugger that follows messages across five services.
- The work needs **immediate, synchronous answers**: payment confirmations, login flows. Events are asynchronous; trying to thread a synchronous answer through them invites pain.
- The team is **small and inexperienced with distributed systems**. Event-driven shifts complexity from "can I make this call?" to "where did my event go and why did it run twice?". That's a real cost.
- You haven't yet **felt the pain** of a service-to-service spaghetti. Pre-emptively going event-driven is often premature; the right time is when the alternative is clearly worse.

## Components involved

- **Frontend** — usually doesn't see this pattern directly. It still hits a backend API; the event-driven dance happens behind that.
- **Backend** — services that publish events ("OrderPlaced") and services that consume them ("EmailSender on OrderPlaced"). Often the same codebase early on, split into separate deployments later.
- **Queue / broker** — the event bus. Kafka for high-volume streaming with replay; RabbitMQ or AWS SNS/SQS for simpler topic/queue semantics; cloud-native (EventBridge, Pub/Sub) for managed setups. The choice matters; switching later is painful.
- **Database** — each consuming service typically maintains its own view of relevant data (the "outbox" pattern is common: write to your DB and emit an event in the same transaction).
- **External services** — webhooks, payment events, third-party notifications, all of these slot naturally into an event-driven system as either producers or consumers.

## Common pitfalls

- **Forgetting that events are at-least-once.** Consumers will see the same event twice eventually. Design idempotent handlers from day one.
- **Implicit contracts.** "We've always assumed OrderPlaced has an `email` field" is the line spoken just before a downstream service breaks. Version your event schemas. Treat them like APIs: backwards-compatible additions, deprecation cycles for removals.
- **Operational opacity.** When something goes wrong in an event-driven system, "where is my data" requires walking through several queues and consumers. Invest in observability *before* the architecture grows past two consumers. Distributed tracing is not optional.
- **Treating the bus as a database.** Events express *what happened*. They're not for "let me query the current state of orders". That's still the database's job.
- **Race conditions between consumers.** Two consumers reacting to the same event in slightly different orders can produce different end states. If consumer order matters, you've broken the event-driven contract; redesign.
- **Reaching for event-driven because microservices are trendy.** The pattern earns its place when you have real consumers fighting over one originator. Before that, it's overhead.
