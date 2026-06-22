# EDGE C6-04 SNMP Production Adapter Report

## Scope

`UFMS-EDGE-C6-04` introduces the first real-connectivity production adapter for the `snmp` connector: a controlled, read-only, SNMPv3 authPriv client (GET/GETNEXT/GETBULK/WALK only) isolated from runtime registration.

## Baseline

- `bea6f0d feat(edge): add modbus production readonly adapter`

## Modified files

- `src/connectors/snmp/production/snmp-production-adapter.types.ts`
- `src/connectors/snmp/production/snmp-production-target-policy.ts`
- `src/connectors/snmp/production/snmp-production-response-normalizer.ts`
- `src/connectors/snmp/production/snmp-production-readonly-adapter.ts`
- `src/connectors/snmp/production/index.ts`
- `deploy/offline-bundle/scripts/verify-snmp-production-readonly-adapter-edge.sh`
- `scripts/validation/lib/snmp-production-adapter-dry-run-cases.cjs`
- `scripts/validation/edge-c6-snmp-production-adapter-dry-run.sh`
- `scripts/validation/edge-c6-snmp-production-adapter-smoke.sh`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_04_SNMP_PRODUCTION_ADAPTER_REPORT.md`

## Adapter architecture

Production code lives under `src/connectors/snmp/production/` and is isolated from foundation modules under `src/connectors/snmp/`.

Call chain:

1. SNMP production configuration validation
2. Target reference resolution (`targetReferenceId` → controlled hostname/port via provider)
3. Target policy validation (allowlist, metadata denylist, port policy)
4. DNS resolution (production default deny; injected resolver in validation mode) with all-result IP revalidation
5. OID allowlist resolution via `oidAllowlistReference`
6. Credential reference resolution via `credentialReferenceId` / protocol references
7. Foundation request validation (version, operation, OID, credential model)
8. Read-only GET/GETNEXT/GETBULK request via Node built-in `node:dgram` UDP
9. Controlled PDU encode/decode with SNP3/SNR3 fixture boundary
10. Request ID match, errorStatus, varbind count, and response size enforcement
11. Foundation response validation and varbind normalization
12. Bounded WALK via repeated GETNEXT within allowlisted subtree
13. Canonical normalized result returned to explicit caller only

Public interface exposes `readOnce()` and `walkOnce()` only. Not registered in runtime index, connector-manager, or connector-registry.

## GET/GETNEXT/GETBULK/WALK only

- Allowed operations: `GET`, `GETNEXT`, `GETBULK`, bounded `WALK` (GETNEXT composition)
- Rejected: `SET`, `TRAP`, `INFORM`, `TRAP_SEND`, and unknown operations
- No write/set/trap/inform/sendRawPdu/executeArbitraryPdu/mutate APIs exported
- No third-party SNMP libraries (`net-snmp`, `snmp-native`) or shell `snmpwalk`/`snmpget`

## SNMPv3 authPriv reference-only boundary

- Production requires `snmpVersion: '3'` and `securityMode: 'authPriv'`
- Tracked config stores reference IDs only: `credentialReferenceId`, `authProtocolReference`, `privProtocolReference`, optional `engineIdReference`
- No plaintext username, auth password, privacy password, community string, PEM, or inline secrets in tracked config
- Validation harness uses in-memory fixture credential provider (`secret://edge/snmp/validation-session`) with no real secrets

## Target and network policy

- Tracked config stores `targetReferenceId`, `targetPort`, `oidAllowlistReference`, credential references only
- Production mode requires foundation target validation via `validateSnmpTarget` / `evaluateSnmpTargetRisk` / `normalizeSnmpTarget`
- Validation test mode: `udpMode: LOOPBACK_TEST` allows explicit loopback fixtures only (`127.0.0.1`, `::1`, `localhost`)
- Rejects metadata hosts, non-allowlisted targets, invalid ports, and private/link-local ranges unless explicit test-mode or `allowPrivateNetworkReference` policy applies
- Opaque error references: `snmp-target:<targetReferenceId>:<sha256-16>`, host hash via `createTargetHash()`

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
- DNS errors use stable codes only (`SNMP_DNS_NOT_ALLOWED`, `SNMP_DNS_RESULT_REJECTED`)

## OID allowlist

- Configuration references allowlist via `oidAllowlistReference` (resolved by deployment provider; harness resolves to `1.3.6.1.2.1`)
- Numeric OID only through foundation `validateSnmpOid`
- Walk constrained to allowlisted subtree via `oidWithinAllowlistedSubtree`
- Hard caps: `maxOids`, `maxVarbinds`, `maxOidLength`, `maxWalkDepth`, `maxWalkRows`, `maxBulkRepetitions`

## UDP and port policy

- Transport: SNMP over UDP via `node:dgram` only (no `node:net` TCP misuse)
- Rejected APIs: `net-snmp`, `snmp-native`, `child_process`, shell snmp tools
- Port range: 1–65535; validation loopback fixture binds port from resolver only
- Connect and response timeouts bounded; `maxRetries` must be zero (fail closed)

## PDU validation

Enforced on fixture boundary (SNP3 request / SNR3 response):

- Minimum PDU size and magic validation
- Request ID match (`SNMP_REQUEST_ID_MISMATCH`)
- errorStatus must be zero (`SNMP_ERROR_STATUS`)
- Varbind count and response byte limits
- Malformed or truncated PDU rejected (`SNMP_PDU_INVALID`)
- Oversized response rejected (`SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED`)

## Resource limits

Enforced with hard caps from `SNMP_PRODUCTION_LIMIT_CAPS`:

- `connectTimeoutMs`, `responseTimeoutMs`, `maxResponseBytes`
- `maxOids`, `maxVarbinds`, `maxWalkDepth`, `maxWalkRows`, `maxBulkRepetitions`, `maxOidLength`
- `maxRetries` (must be 0)
- Invalid config (non-integer, NaN, Infinity, string numbers, over-cap) fails closed with `SNMP_CONFIG_INVALID`

## Foundation integration

Production adapter calls existing SNMP foundation modules:

- `validateSnmpTarget` / `evaluateSnmpTargetRisk` / `normalizeSnmpTarget`
- `validateSnmpReadOnlyPolicy`
- `validateSnmpOperation`
- `validateSnmpVersion`
- `validateSnmpOid`
- `validateSnmpCredentialModel`
- `validateSnmpResponse`
- `calculateResponseBytes`

Foundation files were not modified. No LINK/DB direct access.

## Error redaction

Errors use stable codes only. They do not include raw hostnames from production targets, resolved sensitive IPs, credential references with secret values, community strings, auth/privacy passwords, raw PDU bytes, or certificate content.

## Local UDP fixture server (validation)

- Binds `127.0.0.1` on ephemeral port only (never `0.0.0.0`)
- Implemented in `snmp-production-adapter-dry-run-cases.cjs` with deterministic GET/GETNEXT/GETBULK responses using SNP3/SNR3 PDU format
- Negative fixture modes: short PDU, bad magic, requestId mismatch, errorStatus nonzero, oversized response, malformed tail, slow response
- Server closed after tests; no public network; no external DNS in harness

## Verifier

`deploy/offline-bundle/scripts/verify-snmp-production-readonly-adapter-edge.sh` verifies:

- Production directory and required files
- GET/GETNEXT/GETBULK/WALK only; no SET/TRAP/INFORM; no write APIs or third-party SNMP clients
- Metadata/DNS/target/port/OID/walk/bulk/response/PDU controls
- Credential reference-only boundary; community string rejection path
- Foundation integration; runtime isolation; package drift vs HEAD
- Connector matrix and freeze gates unchanged

Adapter dry-run matrix: **90/90 PASS, 0 failures**

Adapter dry-run negative matrix: **30/30 rejected, 0 leaked**

## Validation results

| Check | Result |
|-------|--------|
| `npm run typecheck:edge` | Pending operator run |
| `snmp-production-adapter-dry-run-cases.cjs` | PASS (90/90) |
| `verify-snmp-production-readonly-adapter-edge.sh` | PASS |
| `validate-edge-package.sh` | Pending operator run |
| `edge-boundary-scan.sh` | Pending operator run |
| `validate-ufms-ibms-isolation.sh` | Pending operator run |

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
- Node built-in modules only: `node:dgram`, `node:crypto`

## Remaining limitations

- SNMP Production Adapter Code Complete ≠ Pilot Approval
- SNMP Production Adapter Code Complete ≠ Production Approval
- `realConnectivityEnabled` remains `false`
- No writeback, no polling scheduler, no TRAP listener, no INFORM sender
- Verifier uses static heuristics supplemented by adapter dry-run negative fixtures
- Production target/credential/OID allowlist providers deferred to deployment phase
- Controlled PDU format is fixture-oriented, not a full production BER stack

## Readiness keys

- `UFMS_EDGE_C6_04_SNMP_PRODUCTION_ADAPTER_PASS`
- `SNMP_PRODUCTION_READONLY_ADAPTER_VERIFIED`
- `SNMP_GET_GETNEXT_GETBULK_WALK_ONLY`
- `SNMP_WRITE_OPERATIONS_REJECTED`
- `SNMP_V3_CREDENTIAL_REFERENCES_ONLY`
- `SNMP_COMMUNITY_STRING_REJECTED`
- `SNMP_TARGET_ALLOWLIST_ENFORCED`
- `SNMP_METADATA_TARGETS_REJECTED`
- `SNMP_DNS_DEFAULT_DENY`
- `SNMP_PORT_POLICY_ENFORCED`
- `SNMP_OID_ALLOWLIST_ENFORCED`
- `SNMP_WALK_BULK_LIMITS_ENFORCED`
- `SNMP_RESPONSE_LIMITS_ENFORCED`
- `SNMP_PDU_VALIDATION_ENFORCED`
- `SNMP_FOUNDATION_VALIDATION_INTEGRATED`
- `SNMP_ERROR_REDACTION_VERIFIED`
- `NO_SNMP_WRITE_API`
- `NO_PUBLIC_NETWORK_ACCESS`
- `NO_EXTERNAL_DNS`
- `NO_RUNTIME_REGISTRATION`
- `CONNECTOR_STILL_BLOCKED`
