# EDGE C3-02 HTTP Polling Connector Foundation Report

## Scope

This phase adds local-safe HTTP polling connector foundation on top of C3-01, with synthetic fixture-driven polling and no real network delivery.

## Objective

Validate HTTP protocol connector ingestion path into existing EDGE pipeline while enforcing strict no-network default and no external system access.

## Files changed

- `src/runtime/http-polling-types.ts`
- `src/runtime/http-polling-reader.ts`
- `src/runtime/plugins/http-polling-protocol-plugin.ts`
- `src/runtime/protocol-plugin-registry.ts`
- `src/runtime/connector-manager.ts`
- `src/runtime/edge-diagnostics-cli.ts`
- `src/runtime/index.ts`
- `config/samples/http-polling-response.json`
- `config/connectors.example.json`
- `scripts/validation/edge-c3-http-polling-connector-dry-run.sh`
- `scripts/validation/edge-c3-http-polling-connector-smoke.sh`
- `evidence/EDGE_C3_02_HTTP_POLLING_CONNECTOR_FOUNDATION_REPORT.md`

## Behavior

- HTTP plugin implements protocol contract: `initialize/start/stop/pollOnce/diagnostics`.
- Poll flow reads synthetic fixture only and maps records into protocol plugin samples.
- No real HTTP request is executed in this phase.
- Validation and malformed handling return structured errors without runtime crash.

## Safe URL rules

Allowed URL forms:

- `mock://...`
- `https://example.invalid/...`
- `http://127.0.0.1/...`
- `http://localhost/...`

All other URL forms are rejected by validation. `networkEnabled` must be `false`.

## Fixture allowlist

Allowed fixture roots:

- `AN_VANTARIS_EDGE/config/samples/**`
- `AN_VANTARIS_EDGE/.runtime/input/**`

Other paths are rejected.

## No network policy

- Foundation mode requires `networkEnabled=false`.
- Plugin and reader do not perform outbound network calls.
- No LINK, DB, UFMS API, or device connectivity is introduced.

## Pipeline path

HTTP connector follows existing C2 pipeline:

Protocol Plugin Runtime
→ Normalization Pipeline
→ Edge Envelope
→ Local Buffer
→ Local Delivery Orchestrator
→ Delivery Audit Chain

## Validation matrix

- typecheck edge/link/edge-link
- c3 http polling dry-run
- c3 http polling smoke
- c3 file import smoke
- c3 readiness gate smoke
- c2 foundation freeze smoke
- validate-edge-package
- edge-boundary-scan
- validate-ufms-ibms-isolation

## Evidence paths

- `.runtime/evidence/edge-c3-http-polling-connector-evidence.json`
- `.runtime/evidence/edge-c3-http-polling-fixture-parse.json`
- `.runtime/evidence/edge-c3-http-polling-pipeline-summary.json`

## Runtime hygiene

- `.runtime` remains local and untracked.
- Runtime evidence files are not committed.

## Boundary result

- Changes remain within allowed `AN_VANTARIS_EDGE` scope.
- No prohibited package boundary references introduced.

## Limitations

- No production HTTP client integration.
- No credential handling implementation.
- No real endpoint polling.
- No writeback.

## Next phase

C3-03 SNMP Read-only Connector Gate.

## Readiness key

`UFMS_EDGE_C3_02_HTTP_POLLING_CONNECTOR_FOUNDATION_PASS`
