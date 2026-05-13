## Context

A `Diagram` is a small graph: at most a few dozen nodes and edges in practice. Many architectural mistakes are *structural*: who connects to whom, what's missing, what's reachable from what. These can be detected by walking the graph, no semantic understanding required.

The LLM is excellent at "given the diagram and the rule findings, explain to the user what's wrong and why" — but bad at "find all structural violations consistently". Rules engine handles the first half; LLM handles the explanation half. They compose.

We're seeding the engine with five rules. The set is intentionally small because:

- Rules pay off when they're high-precision (no false positives). It's better to ship five rules everyone agrees with than thirty rules that nag.
- The rule infrastructure is what costs design effort; once it exists, contributors add rules in their PRs as needed.

## Goals / Non-Goals

**Goals:**

- A `Rule` protocol any contributor can implement with a single Python file.
- Five working rules at MVP, covering the most common structural mistakes for our 8 component types.
- Findings carry enough context (severity, message, rationale, involved node/edge IDs) for a future UI to highlight the offending parts of the diagram and for the LLM to explain them.
- Fast: running all rules on a 50-node diagram completes in well under 10ms.
- Deterministic: same diagram in, same findings out, in the same order.

**Non-Goals:**

- Configurability per project. Future work; out of scope here. All rules are on by default.
- Severity overrides per project. Same reason.
- Auto-fixing. Rules detect; they don't mutate.
- Rules that require LLM judgement ("is this component name well-chosen?"). Those belong elsewhere.
- Performance optimization beyond "obviously fast". 50-node diagrams are the realistic ceiling; premature optimization is silly.
- HTTP endpoint — `add-diagram-analysis-endpoint` proposal.

## Decisions

### One file per rule

`backend/app/services/rules/rules/no_direct_frontend_to_database.py` contains one class. Same for every other rule.

**Why**: a contributor adding a rule has a clear template (copy a file), the diff is contained, deletes are trivial. A mega-file with twenty rules creates merge conflicts on every contribution. Eight rules per file is the Postel-of-rule-engines threshold; we'll revisit if we ever cross ten.

**Alternatives considered**: rules co-located with the registry (rejected — `registry.py` becomes a god-file), rules grouped by category (rejected — premature; we don't have categories yet).

### `Rule` as a `Protocol`, not a base class

Python `Protocol` gives us structural typing: any class with the right shape is a Rule. No inheritance, no metaclass tricks.

```python
class Rule(Protocol):
    id: str
    severity: Severity
    title: str
    description: str
    def check(self, diagram: Diagram) -> list[Finding]: ...
```

**Why**: contributors don't need to import a base class or care about MRO. The shape is the contract. Tests use `isinstance(my_rule, Rule)` thanks to `runtime_checkable`.

**Alternatives considered**: abstract base class (rejected — verbose for what is functionally an interface), dataclass + functions (rejected — loses class-level introspection like `Rule.id`, makes documentation harder).

### Findings carry node/edge IDs, not node/edge objects

A `Finding` references the offending elements by ID:

```python
class Finding(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    rationale: str
    node_ids: list[str] = []
    edge_ids: list[str] = []
```

**Why**: findings might be serialized for the HTTP response, shipped to the frontend to highlight nodes, or fed back to the LLM as context. Strings are stable; object identities are not.

**Alternatives considered**: include full `Node`/`Edge` objects (rejected — duplicates data already in the diagram, complicates serialization).

### Severity as a closed enum

Three levels: `error`, `warning`, `info`. No "critical" or "fatal" — we accept that the line is fuzzy and three is enough.

```python
class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
```

- `error`: this is wrong; the diagram should not look like this.
- `warning`: this is usually wrong; the user might have a reason but should be aware.
- `info`: heads-up that doesn't block anything.

**Alternatives considered**: numeric severity (1-10) (rejected — invites pointless tuning), boolean is_error (rejected — too coarse, can't distinguish "wrong" from "consider this").

### Registry is hard-coded, not auto-discovered

`registry.py` imports each rule explicitly and instantiates it once.

**Why**: explicit beats implicit, especially for ordering and testability. Auto-discovery via `pkgutil.walk_packages` is clever but adds magic to a place that doesn't need any. A contributor adds a rule by adding two lines: an import and a list entry. That's fine.

**Alternatives considered**: entrypoint-based plugin system (rejected — overkill for in-tree rules; revisit when Phase 3 ships third-party plugin support), filesystem auto-discovery (rejected — surprises on rename or refactor).

### The five MVP rules

| Rule ID                              | Severity | What it detects                                                                                       |
| ------------------------------------ | -------- | ----------------------------------------------------------------------------------------------------- |
| `no-direct-frontend-to-database`     | error    | An edge connects a `frontend` node directly to a `database` node, in either direction.                |
| `no-direct-frontend-to-storage`      | error    | An edge connects a `frontend` node directly to a `storage` node, in either direction.                 |
| `frontend-with-db-needs-auth`        | warning  | The diagram contains both `frontend` and `database` nodes but no `auth` node.                         |
| `isolated-node`                      | warning  | A node has no incident edges. Often a leftover or forgotten connection.                               |
| `cycle-detected`                     | warning  | A directed cycle exists in the diagram. Cycles can be legitimate (e.g. retry loops) but rare enough to flag. |

These were chosen because each one teaches a real lesson and has near-zero false positives for normal architectures.

**What we explicitly are NOT shipping** (yet):
- "Backend missing cache" — too opinionated, depends on read load.
- "Single backend, no queue" — depends on workload.
- "Database without backup" — Tangram diagrams don't capture backups.

Adding any of these as future rules is one PR.

## Risks / Trade-offs

- **Risk**: a rule triggers on legitimate but unusual architectures, becoming a nag. → **Mitigation**: only ship rules with very high precision. Tag false-positive-prone rules as `warning`, not `error`. Future: allow opt-out per diagram.
- **Risk**: cycle detection is more expensive than the others (O(V+E)). At 50 nodes this is still microseconds, but a 5000-node diagram would slow down. → **Mitigation**: we accept this; if anyone ever ships a 5000-node diagram to Tangram, we have other problems.
- **Risk**: the `Finding` shape evolves and the future HTTP endpoint has to migrate. → **Mitigation**: we version the schema only when we ship the endpoint; until then, internal callers tolerate change.

## Migration Plan

No migration. New package, new schema. Rollback = revert the PR.

## Open Questions

- **Should `info`-severity findings be returned in `check_all()` by default?** Yes for now; future filtering happens at the call site.
- **How should `cycle-detected` describe long cycles?** Include all node IDs in the cycle? Just the entry point? For MVP we include all nodes participating; can trim later if findings get noisy.
- **Should we add an `applies_when` predicate to `Rule` to skip rules that don't apply to small diagrams?** Probably not needed. Each rule is fast enough that running unconditionally is simpler.
