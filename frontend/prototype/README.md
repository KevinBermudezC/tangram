# Tangram UI prototype (throwaway)

Static HTML + CSS prototype for iterating on the Tangram frontend
look-and-feel without going through Next.js / Tailwind / React Flow.

Open `index.html` in any browser. No build step.

## Why this exists

Iterating on visual direction inside Next.js means restarting the dev
server, fighting Tailwind's defaults, and dealing with React Flow's
runtime. Doing it in plain HTML/CSS is faster: edit, refresh, done.

## What's in the folder

Three HTML pages share one `style.css`:

- **`index.html`** — Home view (in-app entry point, not marketing).
  v0-style layout: a slim rail on the left and a single big prompt
  centered in the main area.
  - **Left rail** (~248px): brand, primary "+ New diagram" button,
    search, nav items (Home, All diagrams, Templates, Settings), a
    "Recent" section listing your saved diagrams as text links (with
    a colored dot to hint AI / manual / draft), and a footer with the
    GitHub link.
  - **Main area**: "What do you want to design?" headline + a big
    textarea ("ask box") with example chips, a "Blank canvas" link,
    and the primary "Generate →" button. A subtle note about
    `data/diagrams/` lives below.
  - Variant via URL hash: `index.html#state=empty` swaps the note for
    a dashed hint that says "No diagrams yet."

  > Marketing landing is a separate page that will eventually live on
  > Vercel.

- **`library.html`** — Library view. Same `appshell` (rail on the left,
  main on the right), but the main becomes a full browser:
  - Header: title + meta + a controls row (segmented filter
    All/Drafts/Generated/Manual, search box, grid/list toggle).
  - Grid of diagram cards. Each card has a hand-coded SVG thumbnail
    (mirrors the editor canvas style), a badge (`AI` / `Manual` /
    `Draft`), name, meta (`5 components · 5 connections · 12s ago`).
    Per-card "more" menu reveals on hover.
  - Templates strip at the bottom: 4 curated starting points to fork.
  - Reached from the rail's "Library" nav item (active on this page).

- **`editor.html`** — Editor view. Three-column shell.
  - Left: components palette (draggable cards).
  - Center: toolbar + React-Flow-shaped canvas with grid, node cards
    (icon + type + name + sub-label + connection handles), zoom
    controls, and a minimap.
  - Right: **chat** with the AI Teaching Assistant — conversation
    bubbles, embedded info cards ("Watch out"), suggested questions,
    and an input row at the bottom.
  - Two extra states via URL hash:
    - `editor.html#state=loading` — generating overlay on the canvas.
    - `editor.html#state=error` — error overlay with retry.

The diagram thumbnails on the home page and the canvas in `editor.html`
are hand-coded inline SVG that mimic what React Flow will eventually
render. Same node shapes, same per-category colors. The real
implementation keeps using React Flow; only the chrome + node card
styling + chat panel + home library grid need new code.

## Translating back to JSX

When we agree on the direction:

1. Tokens in `style.css` `:root` move to either `tailwind.config.ts`
   (color palette + radii + font families) or `app/globals.css`
   (custom properties Tailwind can read via `theme(...)`).
2. Markup for each state translates to:
   - `app/page.tsx` — shell, header, footer, conditional state.
   - `components/PromptForm.tsx` — prompt card (empty + loading +
     collapsed variants).
   - `components/DiagramCanvas.tsx` — toolbar, legend, tutor panel.
     The SVG nodes/edges in the prototype are illustrative only; the
     real canvas keeps using React Flow but reads the new tokens.
3. Delete this folder. The whole point.

## What this is NOT

- Not a spec. If you see a pixel you don't like, change it.
- Not the final asset list — the tangram-logo SVG in the brand mark
  is a placeholder; we may swap it for a hand-tuned version later.
- Not committed to be permanent. Once `chore/polish-frontend-ui` (or
  whatever the porting PR is called) lands, this folder is deleted in
  the same merge.
