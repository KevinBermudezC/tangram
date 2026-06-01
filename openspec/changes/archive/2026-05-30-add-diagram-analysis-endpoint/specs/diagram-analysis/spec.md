## ADDED Requirements

### Requirement: POST /analyze returns findings and feedback

The backend SHALL expose `POST /analyze` accepting a JSON body `{ "diagram": Diagram, "mode_id"?: str }` and returning, on success, `{ "findings": Finding[], "feedback": str }`. `findings` conforms to `app/schemas/finding.py`; `feedback` is a non-empty human-readable string.

#### Scenario: Happy path returns findings and feedback

- **WHEN** a client POSTs a valid `Diagram` to `/analyze`
- **THEN** the response is 200 with a body containing a `findings` array and a `feedback` string
- **AND** every item in `findings` validates against the `Finding` Pydantic model
- **AND** `feedback` is a non-empty string

#### Scenario: mode_id defaults to tutor

- **WHEN** a client POSTs a diagram without a `mode_id`
- **THEN** the request is processed using the `tutor` mode
- **AND** the response is 200

### Requirement: Findings are deterministic and LLM-independent

The `findings` in the response SHALL be the verbatim output of the rules engine (`check_all`) for the submitted diagram, identical across calls and independent of the LLM.

#### Scenario: A violating diagram surfaces the matching findings

- **WHEN** a client POSTs a diagram where the frontend connects directly to a database
- **THEN** `findings` contains a finding whose `rule_id` is the no-direct-frontend-to-database rule
- **AND** that finding lists the offending node ids in `node_ids`

#### Scenario: A clean diagram returns no findings

- **WHEN** a client POSTs a diagram that violates no rules
- **THEN** `findings` is an empty array
- **AND** `feedback` is still a non-empty string

#### Scenario: Findings do not depend on the LLM response

- **WHEN** the same diagram is analyzed with two different LLM responses (mocked)
- **THEN** the `findings` array is identical in both responses

### Requirement: Analysis is read-only

The endpoint SHALL NOT mutate the submitted diagram nor write to persistent storage. Only findings and feedback are produced; nothing is saved.

#### Scenario: No persistence side effect

- **WHEN** a client POSTs a diagram to `/analyze`
- **THEN** no diagram file is created or modified in storage
- **AND** the response body contains no diagram id assigned by the backend

### Requirement: Input validation before LLM call

The endpoint SHALL reject a request whose serialized diagram exceeds `MAX_INPUT_CHARS` before any LLM call is made. Malformed request bodies SHALL be rejected by schema validation.

#### Scenario: Oversized diagram is rejected with 413

- **WHEN** a client POSTs a diagram whose serialized JSON exceeds `MAX_INPUT_CHARS`
- **THEN** the response status is 413 with `code` set to `diagram_too_large`
- **AND** no LLM call is made

#### Scenario: Malformed body is rejected with 422

- **WHEN** a client POSTs a body that does not validate against `AnalyzeRequest`
- **THEN** the response status is 422
- **AND** no LLM call is made

### Requirement: Unknown mode is a client error

When `mode_id` does not correspond to a shipped mode, the endpoint SHALL return 422 with a stable `code`, distinct from the LLM error family.

#### Scenario: Unknown mode_id → 422

- **WHEN** a client POSTs a diagram with `mode_id` set to an unknown value
- **THEN** the response status is 422 with `code` set to `unknown_mode`
- **AND** no LLM call is made

### Requirement: HTTP error mapping for LLM failures

The endpoint SHALL map `LLMError` subclasses to HTTP responses using the same contract as `/generate`. Each response body SHALL include a stable `code` field so callers can branch programmatically.

#### Scenario: LLMConfigError → 503

- **WHEN** the LLM provider is misconfigured (e.g. missing API key)
- **THEN** the endpoint returns 503 with `code` set to `llm_config_error`

#### Scenario: LLMTimeoutError → 504

- **WHEN** the LLM call times out
- **THEN** the endpoint returns 504 with `code` set to `llm_timeout`

#### Scenario: LLMRateLimited → 429

- **WHEN** the provider rate-limits the request
- **THEN** the endpoint returns 429 with `code` set to `llm_rate_limited`

#### Scenario: LLMInvalidResponse → 502

- **WHEN** the provider returns content that fails validation
- **THEN** the endpoint returns 502 with `code` set to `llm_invalid_response`

#### Scenario: LLMInputTooLarge → 413

- **WHEN** the composed prompt exceeds the provider input cap
- **THEN** the endpoint returns 413 with `code` set to `llm_input_too_large`

#### Scenario: Unexpected LLMError → 500

- **WHEN** an unclassified `LLMError` is raised
- **THEN** the endpoint returns 500 with `code` set to `llm_error`
