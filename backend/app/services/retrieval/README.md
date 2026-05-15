# Pattern retrieval

This package finds the most relevant patterns from `patterns/` for a given user query, using vector similarity via Chroma.

## Public API

Only two functions are exported:

```python
from app.services.retrieval import retrieve_patterns, force_rebuild, PatternMatch

# Get up to 3 patterns most relevant to a query.
matches: list[PatternMatch] = await retrieve_patterns("I want to build a chat app", k=3)
for m in matches:
    print(m.pattern.id, m.score)

# Force a full index rebuild (useful in tests or after a manual corpus edit).
await force_rebuild()
```

Internal modules (`store`, `builder`) are not part of the public surface. Use only what's re-exported from `app.services.retrieval`.

## When does the index rebuild?

The index has a **version key** stored as collection metadata:

```
version_key = "<EMBEDDER>::<sha256 of every patterns/*.md>"
```

On every `retrieve_patterns` call, we compute the current version key and compare. If different, we rebuild. That covers:

- A pattern file was edited.
- A pattern was added or removed.
- `EMBEDDER` (in `.env`) was changed.
- The collection is missing entirely (first run, or `data/patterns.chroma/` was deleted).

If nothing changed, the call is fast: one query embed + one Chroma query.

## What gets embedded

For each pattern, the embedder sees:

```
<title>

<full markdown body>
```

Frontmatter (tags, complexity, component_types) is **not** in the embedding text. Those are metadata for future filtering, not for semantic similarity.

## Failure modes

Every error path returns an empty list and logs a warning:

| Failure                                | What you'll see                                          |
| -------------------------------------- | -------------------------------------------------------- |
| `data/patterns.chroma/` is corrupted   | Warning + empty results, next call rebuilds              |
| Chroma raises on query                 | Warning + empty results                                  |
| Ollama isn't running (or wrong URL)    | Warning + empty results                                  |
| OpenAI key is invalid (BYOK)           | Warning + empty results                                  |
| `EMBEDDER=anthropic/*` configured      | LLMConfigError from the embedder factory (don't do that) |

Callers (the LLM endpoints, in future proposals) must tolerate empty results. The system stays usable even with retrieval broken.

## Test isolation

Tests don't touch a real Chroma directory or Ollama. They:

- Inject an in-memory Chroma client via `store.set_client_for_tests(client)`.
- Replace `get_embedder` with a `FakeEmbedder` that returns deterministic vectors (see `tests/_fake_embedder.py`).

That keeps the test suite under a second and runs cleanly in CI without network or background services.
