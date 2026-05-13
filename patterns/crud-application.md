---
id: crud-application
title: CRUD Application
complexity: beginner
tags:
  - foundational
  - web
component_types:
  - frontend
  - backend
  - database
  - auth
---

# CRUD Application

## What it is

A web application whose primary job is to **create, read, update, and delete** records. A frontend lets users see and manipulate data; a backend exposes an API; a database persists everything; auth controls who can do what. Most products start as a CRUD app, including the ones that grow into something more complicated.

This is the architectural pattern you've already built if you've made a todo app, a blog, a contact manager, a small SaaS dashboard, or your first job's internal tool. It is not a "boring" pattern. It is the *correct* pattern for most things until you have evidence you need something more.

## When to use

- The product is fundamentally about **users managing their own data**: tasks, notes, customers, posts.
- Read and write traffic are comparable in volume (no insane skew).
- Latency requirements are normal-internet (sub-second).
- You're early enough that simplicity beats sophistication.

If your product brief fits in the sentence *"users sign in and manage X"*, you almost certainly want CRUD as your starting architecture, even if you'll outgrow it later.

## When to avoid

- The system is **read-mostly at huge scale** (think a news site with one writer and a million readers). You'll outgrow CRUD's database-as-source-of-truth quickly; consider caching or static generation.
- The system is **write-heavy and append-only** (event logs, metrics, audit trails). CRUD-style updates against rows are the wrong primitive; look at event sourcing.
- The system has **complex multi-step workflows** that don't map onto "edit one record". A document is not a workflow engine.
- You're trying to **avoid the database** for ideological reasons. Don't. Use one.

## Components involved

- **Frontend** — usually a web app (React, Vue, Svelte). On mobile, a React Native or native client. The frontend never touches the database directly.
- **Backend** — an HTTP API that exposes CRUD endpoints (`GET /resources`, `POST /resources`, etc.). Does authentication checks, validates input, returns serialized records.
- **Database** — relational by default (PostgreSQL is the safe choice). NoSQL only if you have a specific reason. One database serves the whole backend.
- **Auth** — almost always present. Often outsourced (Auth0, Clerk, Supabase Auth) for an MVP. Self-hosted (Keycloak, hand-rolled with bcrypt + JWT) when the team has the bandwidth.

A queue and a cache are NOT part of the baseline CRUD pattern. Add them when you measure a need, not before.

## Common pitfalls

- **Letting the frontend talk to the database directly.** Every CRUD newcomer is tempted by this. Don't. The frontend is not a trust boundary.
- **No auth on day one.** "I'll add auth later" is a tax that compounds. Add it at the start, even if it's a single hardcoded user.
- **CRUD endpoints structured around tables instead of use cases.** `POST /users-and-their-orders-and-the-orders-line-items` is a sign you've stopped thinking and started reflecting your schema. APIs are a UX surface.
- **Skipping input validation** because "the frontend already does it". The frontend can lie. Validate again on the server.
- **Putting business logic in the database** (stored procedures, triggers) AND in the backend. Pick one home for each rule. Mixed authority is where bugs live.
- **Reaching for microservices** the moment the app grows. A single backend can handle far more than newcomers think. Split when a team boundary or a real scaling pressure demands it, not before.
