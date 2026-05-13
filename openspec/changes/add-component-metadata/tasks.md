## 1. Schema

- [x] 1.1 Add `app/schemas/component.py` defining `ComponentMetadata` (type, label, description, typical_implementations, common_pairings, tradeoffs, anti_patterns, learning_resources, tags)
- [x] 1.2 `common_pairings` field uses `list[NodeType]` so unknown types fail validation
- [x] 1.3 Required string/list fields are validated as non-empty

## 2. Loader

- [x] 2.1 Add `app/services/components/__init__.py` and `app/services/components/loader.py`
- [x] 2.2 Implement `load_components()` that walks `components/`, parses each YAML, validates against `ComponentMetadata`, returns `dict[NodeType, ComponentMetadata]`
- [x] 2.3 Decorate with `@lru_cache`
- [x] 2.4 Implement `get_component(node_type: NodeType) -> ComponentMetadata`
- [x] 2.5 Implement `reset_for_tests()` that clears the cache

## 3. Component YAML files (one per NodeType)

- [x] 3.1 `components/frontend.yaml`
- [x] 3.2 `components/backend.yaml`
- [x] 3.3 `components/database.yaml`
- [x] 3.4 `components/auth.yaml`
- [x] 3.5 `components/storage.yaml`
- [x] 3.6 `components/external_service.yaml`
- [x] 3.7 `components/queue.yaml`
- [x] 3.8 `components/cache.yaml`

Each file MUST include `type`, `label`, `description`, `typical_implementations`, `common_pairings`, `tradeoffs`, `anti_patterns`. The `learning_resources` and `tags` fields are optional.

## 4. Dependency

- [x] 4.1 Add `pyyaml>=6.0` to `[project.dependencies]` in `backend/pyproject.toml`

## 5. Tests

- [x] 5.1 `tests/test_component_parity.py` — every `NodeType` value has a matching YAML; no extra files
- [x] 5.2 `tests/test_component_schema.py` — every YAML validates against `ComponentMetadata`
- [x] 5.3 `tests/test_component_loader.py` — loader caches, `reset_for_tests` clears cache, `get_component` returns correct object and raises on unknown

## 6. Documentation

- [x] 6.1 Add `components/README.md` describing the YAML schema, required/optional fields, tone guidance, and contribution workflow
- [x] 6.2 Add a "Component metadata" section to `backend/README.md` pointing at the components folder and the loader API

## 7. Verification

- [x] 7.1 `ruff format --check` clean across `backend/`
- [x] 7.2 `ruff check` clean across `backend/`
- [x] 7.3 `pytest` clean (existing 33 tests still pass + 11 new tests pass = 42 total)
- [x] 7.4 `openspec validate add-component-metadata --strict`
