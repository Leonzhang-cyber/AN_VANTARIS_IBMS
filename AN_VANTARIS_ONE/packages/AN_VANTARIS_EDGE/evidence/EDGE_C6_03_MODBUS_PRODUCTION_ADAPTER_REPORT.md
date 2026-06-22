# EDGE C6-03 Modbus Production Adapter Report

## Scope

`UFMS-EDGE-C6-03` introduces the first real-connectivity production adapter for the `modbus` connector: a controlled, read-only, Modbus TCP client (FC01–FC04 only) isolated from runtime registration.

## Baseline

- `6ac60cb feat(edge): add http production readonly adapter`

## Modified files

- `src/connectors/modbus/production/modbus-production-adapter.types.ts`
- `src/connectors/modbus/production/modbus-production-target-policy.ts`
- `src/connectors/modbus/production/modbus-production-response-normalizer.ts`
- `src/connectors/modbus/production/modbus-production-readonly-adapter.ts`
- `src/connectors/modbus/production/index.ts`
- `deploy/offline-bundle/scripts/verify-modbus-production-readonly-adapter-edge.sh`
- `scripts/validation/lib/modbus-production-adapter-dry-run-cases.cjs`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_03_MODBUS_PRODUCTION_ADAPTER_REPORT.md`

## Adapter architecture

Production code lives under `src/connectors/modbus/production/` and is isolated from foundation modules under `src/connectors/modbus/`.

Call chain:

1. Modbus production configuration validation
2. Target reference resolution (`targetReferenceId` → controlled hostname/port via provider)
3. Target policy validation (allowlist, metadata denylist, port policy)
4. DNS resolution (production default deny; injected resolver in validation mode) with all-result IP revalidation
5. Foundation request validation (function code, unit ID, address range, quantity limits)
6. Read-only FC01–FC04 request via Node built-in `node:net` TCP
7. MBAP/PDU frame parse and bounded read
8. Transaction ID, unit ID, and function code match enforcement
9. Foundation response validation and register decode
10. Canonical normalized result returned to explicit caller only

Public interface exposes `readOnce()` only. Not registered in runtime index, connector-manager, or connector-registry.

## FC01–FC04 only

- Allowed function codes: `1` (Read Coils), `2` (Read Discrete Inputs), `3` (Read Holding Registers), `4` (Read Input Registers)
- Rejected: `5`, `6`, `15`, `16`, `22`, `23`, and unknown function codes
- No write/send/writeCoil/writeRegister/writeMultiple/maskWrite/readWrite/mutate APIs exported
- No raw frame send API (`sendRawFrame`) exported

## Target policy

- Tracked config stores `targetReferenceId` only — no arbitrary hostnames, secrets, or inline credentials in adapter config
- Production mode requires foundation target validation via `validateModbusTarget` / `evaluateModbusTargetRisk` / `normalizeModbusTarget`
- Validation test mode: `tcpMode: LOOPBACK_TEST` allows explicit loopback fixtures only (`127.0.0.1`, `::1`, `localhost`)
- Rejects metadata hosts, non-allowlisted targets, invalid ports, and private/link-local ranges unless explicit test-mode or `allowPrivateNetworkReference` policy applies
- Opaque error references: `modbus-target:<targetReferenceId>:<sha256-16>`, host hash via `createTargetHash()`

## Metadata rejection

Explicit deny list includes:

- `169.254.169.254`, `100.100.100.200`
- `metadata.google.internal`, `metadata.azure.internal`
- `localhost`, `localhost.localdomain`

Also rejects link-local, loopback, and private ranges in production mode (fail closed unless test-mode loopback fixture or explicit private-network reference policy).

## DNS policy

- Production default: `dnsMode: DENY` — no external DNS resolution without injected provider
- Validation test mode: `dnsMode: INJECTED_TEST` with deterministic injected resolver (no external DNS)
- All resolved A/AAAA results validated via `validateAllResolvedIps` before connect
- DNS errors use stable codes only (`MODBUS_DNS_NOT_ALLOWED`, `MODBUS_DNS_RESULT_REJECTED`)

## MBAP validation

Enforced before and after TCP read:

- Minimum frame size (8 bytes)
- `protocolId === 0`
- MBAP `length` field consistent with buffer size (`buffer.length === 6 + length`)
- PDU byte-count consistency for normal responses
- Exception responses detected (`functionCode & 0x80`) and rejected as `MODBUS_EXCEPTION_RESPONSE`
- Post-read match checks: transaction ID, unit ID, function code (masked)
- Hard cap: `maxFrameBytes` (default cap 260)

## TCP and port policy

- Transport: Modbus TCP over `node:net` only
- Rejected transports/APIs: Modbus RTU, Modbus ASCII, UDP/dgram, `modbus-serial`, `jsmodbus`, `serialport`
- Port range: 1–65535; validation loopback fixture binds port from resolver only
- Connect and response timeouts bounded; `maxRetryCount` must be zero (fail closed)

## Credential and config security

- Tracked config stores reference IDs only (`targetReferenceId`); hostname/port resolved via in-memory provider in validation harness
- No plaintext credentials, PEM, or certificate values in tracked config or logs
- Secrets never logged or returned in errors

## Frame and quantity limits

Enforced with hard caps:

- `maxFrameBytes`, `maxQuantity`, `maxRegisterAddress`
- `connectTimeoutMs`, `responseTimeoutMs`, `maxProcessingMilliseconds`
- `maxRetryCount` (must be 0)
- FC01/FC02 coil max quantity: 2000; FC03/FC04 register max quantity: 125

Invalid config (non-integer, NaN, Infinity, string numbers, over-cap) fails closed with `MODBUS_CONFIG_INVALID`.

## Supported data types

- `uint16`, `int16`, `uint32`, `int32`, `float32`
- `boolean` (FC01/FC02)
- `raw` (register/coil raw values)

Rejects unsupported decode types and mismatched function-code/data-type pairings (for example boolean decode on FC03).

## Decode security

- No eval/Function — binary decode via foundation `decodeModbusRegisters` only
- Dangerous keys (`__proto__`, `prototype`, `constructor`) rejected in normalized output
- Formula prefix protection (`=`, `+`, `-`, `@`) when `formulaPrefixPolicy: REJECT`
- Byte order and word order configurable (`BIG_ENDIAN` / `LITTLE_ENDIAN`)

## Foundation integration

Production adapter calls existing Modbus TCP foundation modules:

- `validateModbusTarget` / `evaluateModbusTargetRisk` / `normalizeModbusTarget`
- `validateModbusReadOnlyPolicy`
- `validateModbusRequest`
- `validateModbusResponse`
- `decodeModbusRegisters`
- `registerSpaceForFunctionCode` / `validateModbusFunctionCode`

Foundation files were not modified. No LINK/DB direct access.

## Error redaction

Errors use stable codes only. They do not include raw hostnames from production targets, resolved sensitive IPs, request/response frame bytes, credentials, or certificate content.

## Local fixture server (validation)

- Binds `127.0.0.1` on ephemeral port only (never `0.0.0.0`)
- Implemented in `modbus-production-adapter-dry-run-cases.cjs` with deterministic FC01–FC04 responses
- Negative fixture modes: short MBAP, bad protocol ID, transaction/unit/function mismatch, exception PDU, byte-count mismatch, oversized frame, length mismatch, malformed PDU, slow response
- Server closed after tests; no public network; no external DNS in harness

## Verifier

`deploy/offline-bundle/scripts/verify-modbus-production-readonly-adapter-edge.sh` verifies:

- Production directory and required files
- FC01–FC04 only; no write APIs or third-party Modbus clients
- Metadata/DNS/target/port/MBAP/frame-limit controls
- Foundation integration; runtime isolation; package drift vs HEAD
- Connector matrix and freeze gates unchanged

Adapter dry-run negative matrix: **93/93 PASS, 0 failures**

## Validation results

| Check | Result |
|-------|--------|
| `npm run typecheck:edge` | PASS |
| `modbus-production-adapter-dry-run-cases.cjs` | PASS (93/93) |
| `verify-modbus-production-readonly-adapter-edge.sh` | PASS |
| `validate-edge-package.sh` | PASS |
| `edge-boundary-scan.sh` | PASS |
| `validate-ufms-ibms-isolation.sh` | PASS (`hard_fail_count=0`) |

## Gate state (unchanged)

- `readOnlyFoundationEnforcementGate=PASS`
- `controlledPilotGate=DEFERRED`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `realConnectivityEnabled=false`
- `supportsWriteback=false`
- `productionDependencyIncluded=false`

## Runtime and dependency posture

- No runtime registration
- No package.json / package-lock.json changes vs HEAD
- No npm install / no new dependencies
- Node built-in modules only: `node:net`, `node:crypto`

## Remaining limitations

- Modbus Production Adapter Code Complete ≠ Pilot Approval
- Modbus Production Adapter Code Complete ≠ Production Approval
- `realConnectivityEnabled` remains `false`
- No writeback, no polling scheduler, no connection pool, no Modbus RTU/ASCII
- Verifier uses static heuristics supplemented by adapter dry-run negative fixtures
- Production target/credential providers deferred to deployment phase
- Modbus TCP lacks native encryption; production use requires additional transport security and operator approval

## Readiness keys

- `UFMS_EDGE_C6_03_MODBUS_PRODUCTION_ADAPTER_PASS`
- `MODBUS_PRODUCTION_READONLY_ADAPTER_VERIFIED`
- `MODBUS_FC01_FC02_FC03_FC04_ONLY`
- `MODBUS_WRITE_FUNCTIONS_REJECTED`
- `MODBUS_TARGET_ALLOWLIST_ENFORCED`
- `MODBUS_METADATA_TARGETS_REJECTED`
- `MODBUS_DNS_DEFAULT_DENY`
- `MODBUS_PORT_POLICY_ENFORCED`
- `MODBUS_MBAP_VALIDATION_ENFORCED`
- `MODBUS_TRANSACTION_UNIT_FUNCTION_MATCH_ENFORCED`
- `MODBUS_FRAME_LIMITS_ENFORCED`
- `MODBUS_QUANTITY_ADDRESS_LIMITS_ENFORCED`
- `MODBUS_DECODE_VERIFIED`
- `MODBUS_FOUNDATION_VALIDATION_INTEGRATED`
- `MODBUS_ERROR_REDACTION_VERIFIED`
- `NO_MODBUS_WRITE_API`
- `NO_PUBLIC_NETWORK_ACCESS`
- `NO_EXTERNAL_DNS`
- `NO_RUNTIME_REGISTRATION`
- `CONNECTOR_STILL_BLOCKED`
