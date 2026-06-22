# EDGE C3-03 SNMP Read-only Connector Foundation Report

## Scope

This phase introduces SNMP read-only connector foundation in local-safe dry-run mode only, with synthetic fixture input and no real network activity.

## Objective

Validate SNMP connector data path into existing EDGE pipeline under strict no-UDP/no-device/no-external-network policy.

## Files changed

- `src/runtime/snmp-readonly-types.ts`
- `src/runtime/snmp-readonly-reader.ts`
- `src/runtime/plugins/snmp-readonly-protocol-plugin.ts`
- `src/runtime/protocol-plugin-registry.ts`
- `src/runtime/connector-manager.ts`
- `src/runtime/edge-diagnostics-cli.ts`
- `src/runtime/index.ts`
- `config/samples/snmp-readonly-response.json`
- `config/connectors.example.json`
- `scripts/validation/edge-c3-snmp-readonly-connector-dry-run.sh`
- `scripts/validation/edge-c3-snmp-readonly-connector-smoke.sh`
- `evidence/EDGE_C3_03_SNMP_READONLY_CONNECTOR_FOUNDATION_REPORT.md`

## Behavior

- SNMP protocol plugin implements `initialize/start/stop/pollOnce/diagnostics`.
- `pollOnce` reads synthetic fixture only and maps varbinds into deterministic samples.
- No UDP send, no device poll, and no network request is executed.

## SNMP read-only policy

- `networkEnabled` must be `false`.
- `supportsWriteback` must be `false`.
- connector operates in read-only synthetic mode only.

## Safe host rules

Allowed host values:

- `mock://synthetic-snmp-device`
- `127.0.0.1`
- `localhost`
- `example.invalid`

All other hosts are rejected.

## Community placeholder rules

- community must be placeholder value `synthetic-public-readonly`.
- non-placeholder values are rejected in validation.

## Fixture allowlist

Allowed fixture roots:

- `AN_VANTARIS_EDGE/config/samples/**`
- `AN_VANTARIS_EDGE/.runtime/input/**`

Other fixture paths are rejected.

## No network / no UDP policy

- no UDP socket operations
- no port 161 access
- no real SNMP library/network behavior
- no LINK/DB/UFMS API access

## Pipeline path

SNMP connector follows existing foundation pipeline:

Protocol Plugin Runtime
→ Normalization Pipeline
→ Edge Envelope
→ Local Buffer
→ Local Delivery Orchestrator
→ Delivery Audit Chain

## Validation matrix

- typecheck edge/link/edge-link
- c3 snmp readonly dry-run
- c3 snmp readonly smoke
- c3 http polling smoke
- c3 file import smoke
- c3 readiness gate smoke
- c2 foundation freeze smoke
- validate-edge-package
- edge-boundary-scan
- validate-ufms-ibms-isolation

## Evidence paths

- `.runtime/evidence/edge-c3-snmp-readonly-connector-evidence.json`
- `.runtime/evidence/edge-c3-snmp-readonly-fixture-parse.json`
- `.runtime/evidence/edge-c3-snmp-readonly-pipeline-summary.json`

## Runtime hygiene

- `.runtime` remains untracked.
- runtime evidence files are not committed.

## Boundary result

- changes are limited to `AN_VANTARIS_EDGE`
- no prohibited package modifications

## Limitations

- no real SNMP transport behavior
- no customer device polling
- no credential handling implementation

## Next phase

C3-04 SNMP Read-only Runtime.

## Readiness key

`UFMS_EDGE_C3_03_SNMP_READONLY_CONNECTOR_FOUNDATION_PASS`
