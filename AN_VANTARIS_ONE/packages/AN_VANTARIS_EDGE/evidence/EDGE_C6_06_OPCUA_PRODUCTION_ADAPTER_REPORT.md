# EDGE C6-06 OPC UA Production Adapter Report

## Scope

`UFMS-EDGE-C6-06` introduces the OPC UA production read-only adapter under `src/connectors/opcua/production/`. The adapter exposes controlled read-only operations (`readOnce`, `browseOnce`, `healthProbeOnce`) using a validation-only OPCQ/OPCR TCP fixture protocol. It is isolated from runtime registration and does not introduce `node-opcua` or other external OPC UA dependencies.

## Baseline

- `6ef5a47 feat(edge): add bacnet production readonly adapter`

## Modified / added files

- `src/connectors/opcua/production/opcua-production-adapter.types.ts`
- `src/connectors/opcua/production/opcua-production-target-policy.ts`
- `src/connectors/opcua/production/opcua-production-response-normalizer.ts`
- `src/connectors/opcua/production/opcua-production-readonly-adapter.ts`
- `src/connectors/opcua/production/index.ts`
- `deploy/offline-bundle/scripts/verify-opcua-production-readonly-adapter-edge.sh`
- `scripts/validation/lib/opcua-production-adapter-dry-run-cases.cjs`
- `scripts/validation/edge-c6-opcua-production-adapter-dry-run.sh`
- `scripts/validation/edge-c6-opcua-production-adapter-smoke.sh`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_06_OPCUA_PRODUCTION_ADAPTER_REPORT.md`

## Production read-only boundary

- Allowed public API: `readOnce()`, `browseOnce()`, `healthProbeOnce()`
- Rejected: write, call, subscribe, monitored items, history update, register/unregister nodes, raw service executors
- `supportsWriteback=false`
- `realConnectivityEnabled=false`
- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `controlledPilotGate=DEFERRED`
- `readOnlyEnforcementGate=DEFERRED`
- Not registered in runtime index, connector-manager, or connector-registry

## No runtime registration / no package dependency

- No changes to `package.json` or `package-lock.json`
- No `node-opcua` or third-party OPC UA client libraries
- No `child_process` shell execution
- Adapter uses Node built-in `node:net` TCP only for validation fixture transport

## Validation-only fixture protocol

The OPCQ/OPCR wire layout is a local smoke/dry-run fixture only. It is **not** a complete OPC UA binary/BER stack and must not be interpreted as production OPC UA wire compatibility.

Future pilot approval may introduce a vetted OPC UA client dependency or formal SDK adapter.

## Foundation integration

Reuses existing OPC UA foundation validators:

- `validateOpcUaReadRequest`, `validateOpcUaBrowseRequest`
- `validateOpcUaResponse`, `validateOpcUaReadOnlyPolicy`
- `validateOpcUaSecurityProfile`, `validateOpcUaIdentityModel`
- `validateOpcUaEndpoint`, `evaluateOpcUaEndpointRisk`

## Endpoint / target policy

- Endpoint reference IDs only (`endpointReferenceId`); no inline credentials, certificates, or private keys
- Metadata hosts denied; DNS default deny unless injected resolver in test mode
- Loopback/private production rejected unless explicit test mode or policy allow
- Port range 1–65535 enforced
- `opc.tcp` modeled transport only; ws/http discovery not production default

## Node / attribute policy

- Node allowlist via `nodeAllowlistReferenceId`
- Attributes limited to VALUE, DISPLAY_NAME, BROWSE_NAME, DESCRIPTION, DATA_TYPE, STATUS_CODE, SOURCE_TIMESTAMP, SERVER_TIMESTAMP
- Write attributes, method calls, subscriptions, and history update rejected

## Normalization

- Canonical fields include `connectorType=OPCUA`, `sourceSystem=EDGE`
- Node reference and endpoint hash redaction support
- No credential, raw packet, or endpoint host leakage in errors unless explicitly allowed
- Formula-prefix and dangerous-key rejection on string outputs

## Verification

| Check | Result |
| --- | --- |
| Verifier | PASS — `verify-opcua-production-readonly-adapter-edge.sh --dry-run` |
| Smoke | PASS — `edge-c6-opcua-production-adapter-smoke.sh` |
| Dry-run | PASS — 200 cases, `edge-c6-opcua-production-adapter-dry-run.sh` |
| Verifier negatives | PASS — 36/36 rejected |
| Typecheck | Pending terminal verification |
| Package/boundary/isolation | Pending terminal verification |

Fixes applied during C6-06 validation closure:

- Empty OPCR ERROR/BAD frames are 13 bytes; adapter minimum response length corrected from 16 to 13
- Fixture node allowlist prefix uses `ns=1;s=UFMS` (not `UFMS.`) to satisfy foundation `stringNodeIdHasPrefix` rules for `UFMS.*` nodes
- Verifier negative mutations aligned to adapter/targetPolicy/normalizer enforcement sites (same pattern as C6-05A)


| Field | Value |
| --- | --- |
| decision | BLOCKED_NOT_PRODUCTION_READY |
| realConnectivityEnabled | false |
| supportsWriteback | false |
| controlledPilotGate | DEFERRED |
| readOnlyEnforcementGate | DEFERRED |

## Approval disclaimer

**Code Complete ≠ Pilot Approval**

**Code Complete ≠ Production Approval**
