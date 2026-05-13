---
id: background-worker
title: Background Worker
complexity: intermediate
tags:
  - async
  - scaling
component_types:
  - frontend
  - backend
  - queue
  - database
  - external_service
---

# Background Worker

## What it is

A pattern where **slow or unreliable work is moved out of the user's request path** and into an asynchronous job queue. The user hits the backend, the backend enqueues a job, the backend responds immediately with "accepted / pending". A separate worker process pulls the job off the queue and does the real work — calling a slow third-party API, generating a report, processing an upload, sending an email.

The defining trait is **decoupling the user-facing latency from the work-doing latency**. The user gets a fast 200 OK; the work happens behind the scenes.

## When to use

- A request triggers work that takes **longer than feels acceptable in a synchronous response** (say, more than ~500ms): video transcoding, PDF generation, large email blasts, calling slow third-party APIs.
- The work is **best-effort / eventually consistent**: notifications, indexing, analytics, cleanup.
- You need to **retry on failure** with backoff: webhook deliveries, payment confirmations, third-party API calls that flake.
- You want to **scale workers independently** from the request-handling backend.

## When to avoid

- The work is **fast and idempotent**: do it synchronously, save the operational complexity.
- The user genuinely needs the result back in the same request. A queue trades latency for throughput; if the user has to wait anyway, a queue adds nothing but moving parts.
- The system has **strict ordering and exactly-once semantics** that a typical work queue can't promise. Look at a real message broker with explicit ordering (Kafka) or a workflow engine (Temporal) instead.
- You don't yet have a real performance or reliability problem the queue would solve. Premature queuing is its own anti-pattern.

## Components involved

- **Frontend** — submits a request that triggers async work. Often polls or subscribes to learn when the work completed.
- **Backend** — accepts the request, validates it, persists what it needs to, enqueues a job, returns immediately.
- **Queue** — the buffer. Redis + BullMQ / RQ / Sidekiq for simple cases; RabbitMQ or SQS for more guarantees; Kafka if you've genuinely outgrown a job queue and need a streaming broker.
- **Worker** — a long-running process (often the same codebase as the backend, run with a different entrypoint) that consumes jobs from the queue and executes them. Conceptually a backend, just running in a different mode.
- **Database** — workers usually persist results back here so the frontend can read them later.
- **External services** — the slow / unreliable thing you're shielding from the user's request. Email providers, payment processors, AI models, third-party APIs.

## Common pitfalls

- **Non-idempotent jobs.** At-least-once delivery means your job will sometimes run twice. If it processes a payment twice, you have a real problem. Design jobs to be safe to repeat: use unique keys, check-and-set, idempotency tokens.
- **No dead-letter queue.** Jobs that fail repeatedly should land in a visible place a human can look at, not disappear silently. The first time you debug "where did all those emails go" you'll learn this the hard way.
- **Coupling job code to specific worker hosts.** Any worker should be able to pick up any job. If a job needs files from disk on a specific machine, you've broken the model.
- **Using the queue as your source of truth.** The queue is a buffer. Persist results to the database. If the queue dies (or is flushed in dev), your data should still exist.
- **Trying to use the queue for synchronous user feedback.** If the user is staring at a spinner waiting for a queued job to finish, you've reinvented synchronous calls with extra steps.
- **Forgetting backpressure.** If producers can enqueue faster than consumers can drain, the queue grows unbounded. Monitor depth; alert on growth; consider rate-limiting producers.
