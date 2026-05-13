## Context

The `Diagram` schema closes the `type` field to 8 values via the `NodeType` enum. Each of those values implies a body of knowledge — "what is a database, when do you use one, what goes wrong when you do it badly" — that the LLM should consult when reasoning about diagrams.

We have two ways to store that knowledge:

1. **Hardcoded in the system prompt.** Easy to start. Hard to grow. Token cost scales linearly with the number of components included. Editing requires Python knowledge.
2. **Data files (YAML/JSON/Markdown) read by code.** Slightly more setup. Editable by non-Python contributors. Loadable as a Python object the rest of the codebase can consult. Scales cleanly.

We pick (2) because Tangram explicitly positions the `components/` directory as a **community asset** — see ADR-0005. A junior dev should be able to open a PR that adds `kubernetes_pod.yaml` without knowing Python.

The format question is YAML vs JSON vs TOML vs Markdown-with-frontmatter:

- **YAML** wins for human editing (multi-line strings, comments, no quote noise).
- **JSON** is too noisy for prose-heavy content like `tradeoffs:` and `anti_patterns:`.
- **TOML** is fine but less common for "documents" of this shape.
- **Markdown-with-frontmatter** is what `patterns/` will eventually use (longer-form), but components are short structured records, not articles.

YAML it is.

## Goals / Non-Goals

**Goals:**

- One file per `NodeType` value, located at `components/<type>.yaml`. The filename matches the enum value exactly.
- A Pydantic schema (`ComponentMetadata`) that every YAML must satisfy at load time. Schema drift is caught by a validation test in CI.
- A loader that reads, validates, and caches all components on first call. Subsequent calls hit memory.
- A `components/README.md` documenting the format so contributors can add or edit without reading Python.
- The metadata content is *initial and incomplete* — we ship a v0 for each of the 8 types covering label, description, typical implementations, tradeoffs, and anti-patterns. The "learning_resources" field is left optional/empty for now; contributors can fill it.

**Non-Goals:**

- Integration with the LLM call path. That's the next proposals' job.
- Custom component types (user-defined, beyond the enum). Phase 2.
- Localization / multi-language descriptions. English-only for MVP.
- Versioning of component definitions. The git history of `components/*.yaml` is the version log.
- Rich relationships ("this component implies that one"). Out of scope for MVP — the data model is flat key/value, not a graph.

## Decisions

### One file per type, filename matches enum value

`components/database.yaml`, not `components.yaml` (mega-file) or `components/db.yaml` (alias).

- **Why filename matches enum value**: the parity test becomes trivial (`set(NodeType) == set(p.stem for p in components_dir.glob('*.yaml'))`). It also lets a future loader resolve a node type to its metadata file in one step.
- **Why one-file-per-type instead of a single mega-file**: smaller files are easier to PR-review, easier to diff, and easier to delete/replace cleanly. Adding `kubernetes_pod.yaml` later requires no edit to existing files.
- **Alternatives considered**: one mega-file (rejected — every component edit touches the same file, merge conflict prone), per-type subdirectories with multiple files (rejected — overkill until we have nested data).

### Pydantic schema as gatekeeper

The loader does `ComponentMetadata.model_validate(yaml_dict)` on every file at first read. A malformed YAML stops the loader with an explicit error pointing at the file.

- **Why**: prevents a typoed key (`tradeofs:`) from silently disappearing into a generic dict.
- **Alternatives considered**: no validation, just `dict` (rejected — too easy to break silently), JSON Schema validation (rejected — Pydantic gives us the same guarantees and is already a project dep).

### Loader caches via `@lru_cache`

`load_components()` is `@lru_cache`-d. The first call walks the directory once; subsequent calls return the cached `dict[NodeType, ComponentMetadata]`.

- **Why**: components are read on every LLM call once the integration lands. Re-reading from disk every time is wasteful.
- **Cache invalidation**: not needed in production (components only change with a deploy). For tests, a `reset_for_tests()` helper clears the cache.
- **Alternatives considered**: lazy per-component loading (rejected — adds complexity for marginal benefit at 8 files), eager load at app boot (rejected — couples component validity to app startup, harder to test in isolation).

### Schema fields chosen for v0

| Field                   | Type         | Required | Purpose                                                |
| ----------------------- | ------------ | -------- | ------------------------------------------------------ |
| `type`                  | `NodeType`   | yes      | Self-identifies; must match filename stem              |
| `label`                 | `str`        | yes      | Human-readable name (UI + prompts)                     |
| `description`           | `str`        | yes      | 1-2 sentence summary (prompts)                         |
| `typical_implementations` | `list[str]` | yes      | Concrete examples ("PostgreSQL", "MySQL", "SQLite")    |
| `common_pairings`       | `list[NodeType]` | yes  | Node types this commonly connects to                   |
| `tradeoffs`             | `list[str]`  | yes      | Bullet-style "you gain X, you pay Y"                   |
| `anti_patterns`         | `list[str]`  | yes      | Bullet-style "do not do this because…"                 |
| `learning_resources`    | `list[str]`  | no       | Optional links/refs for further reading                |
| `tags`                  | `list[str]`  | no       | Free-form taxonomy ("stateful", "managed-saas", etc.)  |

The closed `NodeType` enum in `common_pairings` means "X commonly pairs with Y" is validated against the same set the diagram schema closes — preventing typos like `pairs_with: ['database', 'datbase']`.

**Alternatives considered:** flat dict-of-strings (rejected — loses validation), nested objects with provider-specific details (rejected — premature; tradeoffs and anti-patterns as prose are sufficient for MVP).

### `pyyaml` over alternatives

We need a YAML parser. `pyyaml` is the canonical Python choice — battle-tested, in every Python distribution path. `ruamel.yaml` is more accurate but heavier; `strictyaml` is more restrictive than we need.

- **Alternatives considered**: `ruamel.yaml` (rejected — overkill for our flat dicts), `strictyaml` (rejected — its no-implicit-typing stance fights ergonomics).

## Risks / Trade-offs

- **Risk**: a contributor edits a YAML in a way that passes validation but is semantically wrong (e.g. `description: "TODO"`). → **Mitigation**: spec scenarios assert non-empty for required prose fields; PR reviewers double-check content quality.
- **Risk**: `NodeType` enum grows and someone forgets to add the matching YAML. → **Mitigation**: the parity test fails CI immediately. This is what guarantees we never ship a broken metadata layer.
- **Risk**: YAML schema drift over time as fields are added. → **Mitigation**: Pydantic model is the source of truth; adding a field requires updating both the schema and every YAML in the same PR (CI catches missing fields).
- **Trade-off**: filename-matches-enum-value couples the file system layout to the Python enum. A future rename of an enum value would require renaming the file. We accept this — the rename should be deliberate and infrequent.

## Migration Plan

No migration. New directory, new files.

## Open Questions

- **Should we provide a separate YAML for component "personas" / display flavor (icon, color, illustration)?** Yes eventually, but for MVP the editor UI (which doesn't exist yet) will hardcode that. We add it as a separate field set when the frontend foundation proposal lands.
- **Tone of the prose**: `tradeoffs` and `anti_patterns` should read like a senior engineer mentoring, not like a textbook. Style guide is informal: short sentences, opinionated, second-person. We do not formalize this — the existing v0 content sets the example.
- **Where do `learning_resources` links point?**: prefer canonical docs (Postgres docs, Redis docs) and well-regarded blog posts. Avoid linking to your own employer's content; this is a community asset.
