# EDGE C3-04 Modbus TCP Read-only Connector Foundation Report

## Scope

This phase introduces Modbus TCP read-only connector foundation in local-safe dry-run mode only, with synthetic fixture input and no real TCP activity.

## Objective

Validate Modbus connector data path into existing EDGE pipeline under strict no-TCP/no-port-502/no-device/no-writeback policy.

## Files changed

- `src/runtime/modbus-tcp-readonly-types.ts`
- `src/runtime/modbus-tcp-readonly-reader.ts`
- `src/runtime/plugins/modbus-tcp-readonly-protocol-plugin.ts`
- `src/runtime/protocol-plugin-registry.ts`
- `src/runtime/connector-manager.ts`
- `src/runtime/edge-diagnostics-cli.ts`
- `src/runtime/index.ts`
- `config/samples/modbus-tcp-readonly-response.json`
- `config/connectors.example.json`
- `scripts/validation/edge-c3-modbus-tcp-readonly-connector-dry-run.sh`
- `scripts/validation/edge-c3-modbus-tcp-readonly-connector-smoke.sh`
- `evidence/EDGE_C3_04_MODBUS_TCP_READONLY_CONNECTOR_FOUNDATION_REPORT.md`

## Behavior

- Modbus protocol plugin implements `initialize/start/stop/pollOnce/diagnostics`.
- `pollOnce` reads synthetic fixture only and maps register values into deterministic samples.
- No TCP socket open, no real port 502 access, and no real Modbus library call is executed.

## Modbus TCP read-only policy

- `networkEnabled` must be `false`.
- `supportsWriteback` must be `false`.
- connector runs in synthetic read-only mode only.
- no register write and no coil write behavior is implemented.

## Safe host rules

Allowed host values:

- `mock://synthetic-modbus-device`
- `127.0.0.1`
- `localhost`
- `example.invalid`

All other hosts are rejected.

## Fixture allowlist

Allowed fixture roots:

- `AN_VANTARIS_EDGE/config/samples/**`
- `AN_VANTARIS_EDGE/.runtime/input/**`

Other fixture paths are rejected.

## No TCP / no port 502 policy

- no TCP socket operations
- no port 502 access
- no real Modbus library/network behavior
- no LINK/DB/UFMS API access

## No writeback policy

- writeback remains disabled in config and plugin capability.
- no register write or coil write function is present in C3-04.

## Pipeline path

Modbus connector follows existing foundation pipeline:

Protocol Plugin Runtime
→ Normalization Pipeline
→ Edge Envelope
→ Local Buffer
→ Local Delivery Orchestrator
→ Delivery Audit Chain

## Validation matrix

- typecheck edge/link/edge-link
- c3 modbus tcp readonly dry-run
- c3 modbus tcp readonly smoke
- c3 snmp readonly smoke
- c3 http polling smoke
- c3 file import smoke
- c3 readiness gate smoke
- c2 foundation freeze smoke
- validate-edge-package
- edge-boundary-scan
- validate-ufms-ibms-isolation

## Evidence paths

- `.runtime/evidence/edge-c3-modbus-tcp-readonly-connector-evidence.json`
- `.runtime/evidence/edge-c3-modbus-tcp-readonly-fixture-parse.json`
- `.runtime/evidence/edge-c3-modbus-tcp-readonly-pipeline-summary.json`

## Runtime hygiene

- `.runtime` remains untracked.
- runtime evidence files are not committed.

## Boundary result

- changes are limited to `AN_VANTARIS_EDGE`
- no prohibited package modifications

## Limitations

- no real Modbus transport behavior
- no customer PLC polling
- no credential/device integration

## Next phase

C3-05 protocol hardening after explicit real-protocol gate approval.

## Readiness key

`UFMS_EDGE_C3_04_MODBUS_TCP_READONLY_CONNECTOR_FOUNDATION_PASS`
