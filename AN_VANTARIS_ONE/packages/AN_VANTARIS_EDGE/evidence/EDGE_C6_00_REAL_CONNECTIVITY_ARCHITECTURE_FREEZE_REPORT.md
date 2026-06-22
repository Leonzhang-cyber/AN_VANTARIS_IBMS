# EDGE C6-00 Real Connectivity Architecture Freeze Report

- **Task:** UFMS-EDGE-C6-00
- **Baseline:** `e3f31c1` feat(edge): close foundation readonly enforcement gate
- **Readiness key:** `UFMS_EDGE_C6_00_REAL_CONNECTIVITY_ARCHITECTURE_FREEZE_PASS`
- **Freeze result:** `REAL_CONNECTIVITY_ARCHITECTURE_FREEZE_VERIFIED`

## C5 completion state (unchanged)

| Gate / state | Value |
|--------------|-------|
| `readOnlyFoundationEnforcementGate` | `PASS` |
| `readOnlyEnforcementGate` | `DEFERRED` |
| `controlledPilotGate` | `DEFERRED` |
| `productionReadOnlyGate` | `DEFERRED` |
| `decision` | `BLOCKED_NOT_PRODUCTION_READY` |
| `realConnectivityEnabled` | `false` |
| `supportsWriteback` | `false` |
| `syntheticFixtureOnly` | `true` |
| `productionDependencyIncluded` | `false` |

C6-00 defines future enablement conditions only. No blocked-state promotion occurred.

## Architecture layers

### Connector Foundation (C5, frozen)

Policy, validators, canonical types, synthetic transport, deterministic tests. No network. No production dependency.

### Production Adapter (future, not implemented)

- Future path: `src/connectors/<connector>/production/`
- Isolated dependency, network capability, credential/certificate provider, lifecycle, read-only enforcement
- Default not loaded, not exported, not enabled
- Must not bypass foundation policy or validator

Target migration records `foundation/` split without moving files in C6-00.

## Invocation chain (frozen)

```
Configuration → Enablement Gate → Credential/Certificate Reference Resolution
→ Target Risk Validation → Production Adapter → Foundation Request Validation
→ Read-only Protocol Operation → Foundation Response Validation → Normalization → Buffer / Outbox
```

## Production adapter boundary

Production adapters are architecturally separate from foundation code. C6-00 documents boundaries only; no adapter code, exports, or runtime loading was added.

## Dependency admission

`REAL_CONNECTIVITY_DEPENDENCY_ADMISSION.edge.json` records candidate dependency **classes** per connector. All candidates:

- `approvalStatus=NOT_EVALUATED`
- `productionIncluded=false`
- Full review fields present (license, security, maintenance, SBOM, offline packaging, write API risk, native build risk)

No packages were installed. No fictional approved packages were recorded.

## Credential and certificate boundary

Reference-only model: `CredentialReference`, `CertificateReference`, `PrivateKeyReference`, `TrustAnchorReference`, `ServerFingerprintReference`.

Tracked config stores reference IDs only — no plaintext passwords, community strings, inline private keys, or inline PEM. No real provider implemented in C6-00.

## Network boundary

Default deny. Explicit target and port allowlists required. DNS disabled or approved resolver mode only. Resolved IP and redirect/endpoint discovery hops require revalidation. Outbound-only; no inbound listener; no connector management port. Data Diode reverse communication prohibited. No real network calls in C6-00.

## Read-only production gate requirements (future)

`productionReadOnlyGate=DEFERRED`. Required future evidence includes write API inventory, compile-time write exclusion, runtime write executor exclusion, config write disable, fail-closed unknown operations, dependency rescan on upgrade, negative integration tests, packet/request evidence, audit of rejected writes, and rollback verification.

## Connection lifecycle (model only)

States: `DISABLED`, `CONFIGURED`, `VALIDATING`, `CONNECTING`, `CONNECTED`, `DEGRADED`, `BACKOFF`, `CIRCUIT_OPEN`, `STOPPING`, `STOPPED`, `BLOCKED`.

Startup default `DISABLED`. Gate/credential/target failures → `BLOCKED`. Timeouts → `BACKOFF`. Repeated failures → `CIRCUIT_OPEN`. Bounded shutdown; no infinite reconnect or reconnect storm. State changes audited and diagnosed. Network state machine not implemented in C6-00.

## Buffer / outbox boundary

Connector → EDGE normalization/pipeline → buffer/outbox. No direct LINK or DB calls from connector. Backpressure handled by EDGE runtime. Canonical envelope required. LINK and Contracts unchanged.

## Diagnostics (future fields)

Each production adapter will report connectorId, adapterMode, lifecycleState, timing, circuit state, target/security references, counters, and lastErrorCategory — without logging secret values, certificate content, or full credentials.

## Implementation order

| Priority | Phase | Connector |
|----------|-------|-----------|
| 1 | C6-01 | File |
| 2 | C6-02 | HTTP |
| 3 | C6-04 | Modbus TCP |
| 4 | C6-03 | SNMPv3 |
| 5 | C6-05 | BACnet/IP |
| 6 | C6-06 | OPC UA |
| — | C6-07 | Credential/Certificate Provider Foundation |
| — | C6-08 | Production Read-only Gate Consolidation |

**File first** — lowest risk. **OPC UA last** — highest complexity (certificates, SecureChannel, Session).

## Connector-specific risks

| Connector | Risk focus |
|-----------|------------|
| file | Filesystem scope allowlist; no arbitrary shell watcher |
| http | TLS verification; redirect hop revalidation |
| modbus | Write function API isolation; MBAP timeout/recovery |
| snmp | SNMPv3 authPriv; v1/v2c not default production |
| bacnet | UDP/BBMD/FDR; write service encapsulation |
| opcua | Certificate trust; SecureChannel/Session; write/subscription prohibition |

## Current blocked state

All six connectors remain `BLOCKED_NOT_PRODUCTION_READY` with no real connectivity and no writeback.

## Validation

```bash
npm run typecheck:edge
bash AN_VANTARIS_EDGE/scripts/validation/edge-c6-real-connectivity-architecture-freeze-dry-run.sh
bash AN_VANTARIS_EDGE/scripts/validation/edge-c6-real-connectivity-architecture-freeze-smoke.sh
bash AN_VANTARIS_EDGE/deploy/offline-bundle/scripts/verify-real-connectivity-architecture-freeze-edge.sh
bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh
bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh
bash scripts/validate-ufms-ibms-isolation.sh
```

**Dry-run:** 154/154 PASS (after C6-00A verifier security-gate closure).  
**Isolation:** PASS with warnings — `hard_fail_count=0`, `soft_warn_count=137` (non-blocking historical domain mentions).

## Implementation order note

Phase IDs (C6-01..C6-08) are plan identifiers. **Actual startup priority** follows the `executionPriority` / priority table (File → HTTP → Modbus → SNMP → BACnet → OPC UA), not numeric phase ID order alone (e.g. C6-04 Modbus precedes C6-03 SNMP in execution priority).

## Limitations

- **Architecture Freeze ≠ Real Connectivity Complete**
- **Architecture Freeze ≠ Pilot Approval**
- **Architecture Freeze ≠ Production Approval**
- No production dependency installation
- No connector source or runtime changes
- No real network, DNS, socket, or credential access in C6-00

## Final decision

`REAL_CONNECTIVITY_ARCHITECTURE_FREEZE_VERIFIED` — real connectivity architecture, dependency admission, security gates, credential/network boundaries, lifecycle model, and implementation sequence frozen for six connectors; all remain blocked for production use.

### C6-00A verifier security-gate closure (UFMS-EDGE-C6-00A)

Independent verify (`UFMS-EDGE-C6-00-CURSOR-INDEPENDENT-VERIFY`) **Final decision: FAIL**.

Original negative matrix: **20/25 rejected, 5 leaked**:

1. `licenseReviewRequired=false`
2. `securityReviewRequired=false`
3. `SBOMRequired=false`
4. `inlinePemProhibited=false`
5. `retryBackoffPolicy.boundedRetryRequired=false`

Root cause: verifier checked field presence only for dependency review flags; credential boundary omitted `inlinePemProhibited` and `communityStringProhibited`; retry policy omitted strict `boundedRetryRequired` enforcement.

C6-00A fixes:

- Verifier adds `assertStrictTrue` / `assertStrictFalse` with strict `value === true|false` (rejects string `"true"`, `null`, `1`).
- All dependency review flags forced true: `licenseReviewRequired`, `securityReviewRequired`, `maintenanceReviewRequired`, `SBOMRequired`, `offlinePackagingRequired`.
- Credential boundary forced true: `plaintextPasswordProhibited`, `communityStringProhibited`, `privateKeyInlineProhibited`, `inlinePemProhibited`, `secretLoggingProhibited`, `evidenceSecretLoggingProhibited`, `trackedConfigStoresReferencesOnly`, `providerInjectedByDeployment`.
- Retry/resilience forced true: `retryBackoffPolicy.boundedRetryRequired`, `maxAttemptsRequired`, `infiniteRetryProhibited`; `circuitBreakerPolicy.requiredBeforeProduction`; `lifecycleModel.reconnectStormProhibited`, `boundedShutdownRequired`, `infiniteReconnectProhibited`.
- Dry-run adds 16 real-verifier negative fixtures (154 total cases); repair matrix **35/35 rejected, 0 leaked**.

No connector source, policy, matrix, or runtime changes. Foundation gate **PASS**; controlled pilot gate **DEFERRED**; production gate **DEFERRED**. No real connectivity; writeback disabled; all connectors `BLOCKED_NOT_PRODUCTION_READY`.

Isolation: PASS, `hard_fail_count=0`, `soft_warn_count=137` (non-blocking). Architecture Freeze ≠ Real Connectivity Complete ≠ Pilot Approval ≠ Production Approval.
