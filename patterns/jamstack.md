---
id: jamstack
title: JAMstack
complexity: beginner
tags:
  - web
  - serverless
  - content
component_types:
  - frontend
  - external_service
  - storage
  - auth
---

# JAMstack

## What it is

A web architecture where the **frontend is pre-rendered into static files** (HTML, CSS, JavaScript) served from a CDN, and any dynamic behavior happens through **API calls to third-party services or serverless functions** at request time. "JAM" originally stood for *JavaScript, APIs, Markup* — the spirit is "the heavy lifting happens at build time and at the edge, not in a running server you operate".

A JAMstack app looks like this from the user's perspective: they hit a fast, mostly-static site. Anything that needs server logic (sign-in, payment, search) calls out to a managed service. There's no traditional always-on backend in the middle.

## When to use

- The product is **content-first**: documentation, marketing site, blog, portfolio, e-commerce catalog.
- You want **near-zero hosting cost** and **edge-level speed** with minimal ops.
- The team is small and doesn't want to maintain a backend server.
- The dynamic surface is small and maps cleanly onto a few external services (auth, payment, search, comments).

## When to avoid

- The app needs **deeply personalized server-rendered pages** on every request that change based on user state. Static + JS hydration can fake this only to a point; eventually you'll fight your own architecture.
- The product is **write-heavy with user-generated content** that needs server validation, moderation, and complex permissions. A CRUD application with a real backend is a better fit.
- You need **stateful long-running connections** (websockets, server-sent events) at scale. Serverless functions are not designed for those.
- You have **strict data-residency or privacy requirements** that conflict with third-party services. JAMstack tends to spread your data across multiple SaaS vendors.

## Components involved

- **Frontend** — a static site generator (Next.js in SSG mode, Astro, Hugo, Eleventy, SvelteKit static, etc.). The output is files in a CDN bucket.
- **Storage** — usually an object store like S3 / Cloudflare R2 hosting the static assets, fronted by a CDN.
- **External services** — payments (Stripe), auth (Auth0, Clerk), comments (Disqus), search (Algolia, Meilisearch Cloud), forms (Formspree). Each one is a discrete capability owned by someone else.
- **Auth** — outsourced almost without exception in this pattern. The frontend gets a token from an auth provider and presents it to other APIs.

You may also have a serverless backend function or two (Vercel Functions, AWS Lambda) for glue code, but the architecture's identity is "static site + APIs", not "serverless app".

## Common pitfalls

- **Treating the build step as instant.** Rebuilds can take minutes. Pages stale until you redeploy. Pick your update strategy (incremental builds, on-demand revalidation) before launch.
- **Spreading auth across many providers.** "Disqus for comments, Auth0 for login, Algolia for search, all separate accounts" works at first but becomes a permissions nightmare. Decide what's the source of truth for identity.
- **Calling APIs straight from the browser with secret keys.** A "public" API key embedded in your JS bundle is *not* a secret. Anything sensitive must go through a serverless function that holds the real key server-side.
- **Forgetting the cost model of "serverless" at scale.** Lambda + DynamoDB is cheap for trivial traffic and expensive for sustained traffic. The cost curve crosses CRUD's at some point.
- **Treating JAMstack as a religion.** It's an architecture, not an identity. If you need a real backend for one feature, just add a real backend. Hybrid is fine.
