## ADDED Requirements

### Requirement: Rule protocol

The backend SHALL expose a `Rule` Protocol with the following surface: `id: str`, `severity: Severity`, `title: str`, `description: str`, and `check(diagram: Diagram) -> list[Finding]`. Every built-in rule SHALL implement this Protocol.

#### Scenario: Built-in rules satisfy the Protocol

- **WHEN** a test imports every built-in rule class and checks them with `isinstance(rule_instance, Rule)`
- **THEN** every instance is recognized as a `Rule`

#### Scenario: A contributor's new rule needs no inheritance

- **WHEN** a contributor adds a new rule class with the four attributes and the `check` method
- **THEN** the class is usable as a `Rule` without subclassing any base class

### Requirement: Finding shape

A `Finding` SHALL include a `rule_id`, `severity`, `message`, `rationale`, optional `node_ids` (list of node id strings) and optional `edge_ids` (list of edge id strings). Findings SHALL be Pydantic models serializable to JSON.

#### Scenario: Finding round-trips through JSON

- **WHEN** a `Finding` is dumped with `model_dump_json()` and re-loaded with `Finding.model_validate_json(...)`
- **THEN** the resulting model equals the original

#### Scenario: Findings carry actionable references

- **WHEN** a rule emits a finding for a violation involving two specific nodes
- **THEN** the finding's `node_ids` lists the IDs of those two nodes
- **AND** the finding's `edge_ids` lists the ID of any edge directly responsible for the violation

### Requirement: Direct frontend-to-database connections are flagged as errors

The built-in rule `no-direct-frontend-to-database` SHALL emit a finding at `error` severity for any edge that directly connects a `frontend` node to a `database` node (in either direction).

#### Scenario: Direct edge triggers the rule

- **WHEN** a diagram contains an edge whose source is a `frontend` node and whose target is a `database` node
- **THEN** `no-direct-frontend-to-database` emits exactly one finding for that edge
- **AND** the finding's severity is `error`
- **AND** the finding's `node_ids` references the frontend and the database
- **AND** the finding's `edge_ids` references the offending edge

#### Scenario: Going through a backend does not trigger

- **WHEN** a frontend connects to a backend and the backend connects to a database (two edges, no direct frontend-to-database edge)
- **THEN** `no-direct-frontend-to-database` emits no findings

#### Scenario: Direction does not matter

- **WHEN** the offending edge has `source = database`, `target = frontend`
- **THEN** the rule still emits a finding

### Requirement: Direct frontend-to-storage connections are flagged as errors

The built-in rule `no-direct-frontend-to-storage` SHALL emit a finding at `error` severity for any edge that directly connects a `frontend` node to a `storage` node (in either direction). Pre-signed URLs for direct browser uploads are a legitimate pattern, but they are an explicit backend-mediated handshake; they are not represented as a `frontend → storage` edge in the diagram.

#### Scenario: Direct edge triggers the rule

- **WHEN** a diagram contains an edge whose source is a `frontend` node and whose target is a `storage` node
- **THEN** `no-direct-frontend-to-storage` emits exactly one finding for that edge

#### Scenario: Backend-mediated storage does not trigger

- **WHEN** a frontend connects to a backend and the backend connects to a storage node
- **THEN** the rule emits no findings

### Requirement: Frontend plus database needs an auth node

The built-in rule `frontend-with-db-needs-auth` SHALL emit a finding at `warning` severity when a diagram contains both a `frontend` node and a `database` node but no `auth` node.

#### Scenario: Missing auth in a user-facing system

- **WHEN** the diagram has at least one frontend, one database, and zero auth nodes
- **THEN** the rule emits one finding referencing the frontend and database nodes

#### Scenario: Auth present satisfies the rule

- **WHEN** the diagram has a frontend, a database, and at least one auth node
- **THEN** the rule emits no findings

#### Scenario: No database means no finding

- **WHEN** the diagram has a frontend but no database
- **THEN** the rule emits no findings

### Requirement: Isolated nodes are flagged as warnings

The built-in rule `isolated-node` SHALL emit a finding at `warning` severity for each node that has no incident edge (neither inbound nor outbound).

#### Scenario: A node with no edges is flagged

- **WHEN** a diagram has a node with no edges referencing its id
- **THEN** the rule emits one finding for that node

#### Scenario: A node with at least one edge is not flagged

- **WHEN** a diagram has a node referenced by at least one edge (as source or target)
- **THEN** the rule emits no finding for that node

#### Scenario: Single-node diagrams produce one finding

- **WHEN** the diagram has exactly one node and no edges
- **THEN** the rule emits one finding (for that node)

### Requirement: Cycles are flagged as warnings

The built-in rule `cycle-detected` SHALL emit a finding at `warning` severity when the directed graph induced by the diagram's edges contains at least one cycle. The finding SHALL reference the nodes participating in the detected cycle.

#### Scenario: Acyclic graph is clean

- **WHEN** the diagram has no cycles in its directed edges
- **THEN** the rule emits no findings

#### Scenario: A two-node cycle is flagged

- **WHEN** the diagram has edges A→B and B→A
- **THEN** the rule emits at least one finding whose `node_ids` contains both A and B

#### Scenario: Self-loops are flagged

- **WHEN** an edge has the same source and target
- **THEN** the rule emits a finding referencing that node

### Requirement: Registry exposes all built-in rules and a one-shot check

`registry.py` SHALL expose `all_rules() -> list[Rule]` returning a stable, ordered list of every built-in rule, and `check_all(diagram: Diagram) -> list[Finding]` returning the concatenation of every rule's findings.

#### Scenario: Registry includes all five built-in rules

- **WHEN** `all_rules()` is called
- **THEN** it returns five Rule instances
- **AND** their `id` values include `no-direct-frontend-to-database`, `no-direct-frontend-to-storage`, `frontend-with-db-needs-auth`, `isolated-node`, `cycle-detected`

#### Scenario: check_all runs every rule

- **WHEN** `check_all(diagram)` is called on a diagram that violates two distinct rules
- **THEN** the returned list contains the findings from both rules

#### Scenario: A clean diagram returns an empty list

- **WHEN** `check_all(diagram)` is called on a diagram with no violations
- **THEN** it returns an empty list

### Requirement: Documentation surface

The repository SHALL include `backend/app/services/rules/README.md` documenting how to add a new rule (file layout, registry entry, test layout, severity guidance).

#### Scenario: A contributor adds a rule by following the README

- **WHEN** a contributor reads the rules README and follows it to add a new rule
- **THEN** the README is sufficient to land a working rule with tests, with no Python wizardry beyond writing the `check` function
