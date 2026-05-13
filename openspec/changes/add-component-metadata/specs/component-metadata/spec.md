## ADDED Requirements

### Requirement: One metadata file per node type

The repository SHALL contain exactly one YAML file under `components/` for every value of the `NodeType` enum. The filename (without extension) SHALL match the enum value exactly.

#### Scenario: Every node type has a corresponding file

- **WHEN** the loader walks `components/` against the `NodeType` enum
- **THEN** every enum value has a `components/<value>.yaml` file present
- **AND** no file under `components/` corresponds to a value not in the enum

#### Scenario: New node type without metadata fails CI

- **WHEN** a contributor adds a value to `NodeType` and does not add the matching YAML
- **THEN** the parity test in `backend/tests/test_components_parity.py` fails
- **AND** the failure message names the missing file

### Requirement: Schema enforcement

Every YAML in `components/` SHALL parse into a `ComponentMetadata` Pydantic model. Required fields SHALL be present and non-empty.

#### Scenario: Valid YAML loads successfully

- **WHEN** the loader reads a well-formed `components/<type>.yaml`
- **THEN** `ComponentMetadata.model_validate(parsed)` succeeds
- **AND** the resulting model exposes `type`, `label`, `description`, `typical_implementations`, `common_pairings`, `tradeoffs`, `anti_patterns` as non-empty values

#### Scenario: Missing required field fails loudly

- **WHEN** a YAML file omits `description` (or any required field)
- **THEN** the loader raises a Pydantic `ValidationError` whose message identifies the file path and the missing field

#### Scenario: Unknown node type in `common_pairings` is rejected

- **WHEN** a YAML lists a value in `common_pairings` that is not in `NodeType`
- **THEN** validation fails before the model is returned

### Requirement: Loader caches in memory

The loader function SHALL read each component file at most once per process. Subsequent calls SHALL return cached results without filesystem access.

#### Scenario: Repeated calls hit the cache

- **WHEN** `load_components()` is called twice in the same process
- **THEN** the second call returns the same object identity as the first
- **AND** no additional filesystem reads occur between the two calls

#### Scenario: Test reset clears the cache

- **WHEN** a test calls `reset_for_tests()` on the loader
- **THEN** the next `load_components()` call re-reads from disk

### Requirement: Per-type lookup

Callers SHALL be able to obtain a single `ComponentMetadata` instance by `NodeType` value via `get_component(node_type)`.

#### Scenario: Known type returns its metadata

- **WHEN** a caller invokes `get_component(NodeType.DATABASE)`
- **THEN** the return value is the `ComponentMetadata` parsed from `components/database.yaml`

#### Scenario: Unknown type raises

- **WHEN** a caller invokes `get_component` with a value not present in the loaded set (only possible after enum drift before parity is re-run)
- **THEN** a `KeyError` is raised with a message identifying the missing type

### Requirement: Documentation surface

The repository SHALL include `components/README.md` documenting the YAML schema, the required and optional fields, and the contribution workflow for adding or editing a component.

#### Scenario: Contributor follows the README to add a component

- **WHEN** a new contributor wants to add `kubernetes_pod` to the metadata library after the enum has been extended
- **THEN** the README explains the file location, schema, required fields, and tone guidance
- **AND** no Python knowledge is required to follow the steps
