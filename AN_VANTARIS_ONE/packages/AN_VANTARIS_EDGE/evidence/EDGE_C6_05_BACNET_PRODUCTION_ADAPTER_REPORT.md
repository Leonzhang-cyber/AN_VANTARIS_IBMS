# EDGE C6-05 BACnet/IP Production Adapter Report

## Scope

`UFMS-EDGE-C6-05` introduces the first real-connectivity production adapter for the `bacnet` connector: a controlled, read-only BACnet/IP client (ReadProperty / ReadPropertyMultiple only) isolated from runtime registration.

## Baseline

- `136b589 feat(edge): add snmp production readonly adapter`

## Modified files

- `src/connectors/bacnet/production/bacnet-production-adapter.types.ts`
- `src/connectors/bacnet/production/bacnet-production-target-policy.ts`
- `src/connectors/bacnet/production/bacnet-production-response-normalizer.ts`
- `src/connectors/bacnet/production/bacnet-production-readonly-adapter.ts`
- `src/connectors/bacnet/production/index.ts`
- `deploy/offline-bundle/scripts/verify-bacnet-production-readonly-adapter-edge.sh`
- `scripts/validation/lib/bacnet-production-adapter-dry-run-cases.cjs`
- `scripts/validation/edge-c6-bacnet-production-adapter-dry-run.sh`
- `scripts/validation/edge-c6-bacnet-production-adapter-smoke.sh`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_05_BACNET_PRODUCTION_ADAPTER_REPORT.md`

## Adapter architecture

Production code lives under `src/connectors/bacnet/production/` and is isolated from foundation modules under `src/connectors/bacnet/`.

Call chain:

1. BACnet production configuration validation
2. Enablement/gate check (matrix remains blocked; adapter not registered)
3. Target reference resolution (`targetReferenceId` → controlled hostname/port via provider)
4. Target network policy validation (allowlist, metadata denylist, port policy)
5. DNS resolution (production default deny; injected resolver in validation mode) with all-result IP revalidation
6. Object/property allowlist resolution via `objectReferenceId` / `propertyReferenceId`
7. Foundation request validation (`validateBacnetRequest`, `validateBacnetReadOnlyPolicy`)
8. Read-only ReadProperty / ReadPropertyMultiple request via Node built-in `node:dgram` UDP
9. Controlled BVLC/NPDU/APDU encode/decode with BACN/BACR fixture boundary
10. Invoke ID match, service match, error/reject/abort handling, and response size enforcement
11. Foundation response validation and property normalization
12. Canonical normalized result returned to explicit caller only

Public interface exposes `readPropertyOnce()`, `readPropertyMultipleOnce()`, and test-only `discoverOnce()`. Not registered in runtime index, connector-manager, or connector-registry.

## ReadProperty / ReadPropertyMultiple only

- Allowed services: `READ_PROPERTY`, `READ_PROPERTY_MULTIPLE` (bounded)
- Rejected: `WRITE_PROPERTY`, `WRITE_PROPERTY_MULTIPLE`, `SUBSCRIBE_COV`, `SUBSCRIBE_COV_PROPERTY`, `DEVICE_COMMUNICATION_CONTROL`, `REINITIALIZE_DEVICE`, `ACKNOWLEDGE_ALARM`, `PRIVATE_TRANSFER`, and unknown services
- No writeProperty / writePropertyMultiple / subscribeCov / ackAlarm / deviceControl / sendRawApdu / executeArbitraryService / mutate APIs exported
- No third-party BACnet libraries (`bacstack`, `node-bacnet`) or shell BACnet tools

## Target and network policy

- Tracked config stores reference IDs only: `targetReferenceId`, `deviceInstanceReferenceId`, `objectReferenceId`, `propertyReferenceId`
- No raw arbitrary host/IP, password, bearer token, or device credential in tracked config
- Production mode requires foundation target validation via `validateBacnetTarget` / `evaluateBacnetTargetRisk` / `normalizeBacnetTarget`
- Validation test mode: `udpMode: LOOPBACK_TEST` allows explicit loopback fixtures only (`127.0.0.1`, `::1`, `localhost`)
- Rejects metadata hosts, non-allowlisted targets, invalid ports, private/link-local ranges unless explicit test-mode or `allowPrivateNetworkReference` policy applies
- Opaque error references: `bacnet-target:<targetReferenceId>:<sha256-16>`, host hash via `createTargetHash()`

## Object / property allowlist

- `objectType`, `objectInstance`, `propertyIdentifier`, optional `arrayIndex` validated against resolved allowlists
- ReadPropertyMultiple bounded by `maxObjects` / `maxProperties`
- Vendor-specific object/property defaults rejected unless future allowlist explicitly approves

## Broadcast policy

- Production default: `broadcastMode: DENY` — Who-Is broadcast rejected (`BACNET_BROADCAST_NOT_ALLOWED`)
- Test discovery: `broadcastMode: TEST_DISCOVERY_ONLY` with `testMode` and loopback fixture only

## BVLC / NPDU / APDU validation

- BVLC type must be BACnet/IP (`0x81`), function in allowed set, length matches packet
- NPDU version legal; routing/source-routing control flags rejected
- APDU invoke ID and service choice matched to request; error/reject/abort not treated as success
- Segmentation default denied; APDU/response size capped by `maxApduBytes` / `maxResponseBytes`

## Foundation integration

- Reuses existing foundation policy, request validator, response validator, and canonical normalization boundary
- Does not bypass foundation validators; does not write outbox, call LINK, or access DB

## Error redaction

Errors expose only `targetReferenceId`, opaque target hash, safe object/property references, and safe error codes. No host/IP plaintext, customer endpoints, raw BVLC/NPDU/APDU payload, credentials, or stack traces.

## Local UDP fixture server constraints

- Validation harness binds `127.0.0.1:0` only (never `0.0.0.0`)
- Unique validation session under `.runtime/validation-sessions/c6-05/`
- Fixture closes socket on completion; no public network or external DNS

## C6-05A wire layout consistency fix

Initial smoke/dry-run failures were caused by inconsistent BACnet/IP fixture wire layout versus production adapter encode/decode:

- Request `encodeRequestPacket` total size omitted BVLC length field (+2) and overstated payload header (+4)
- Fixture `decodeRequest` did not always skip the 4-byte request `arrayIndex` slot when `hasArrayIndex == 0`
- Response encoders wrote 4-byte `arrayIndex` when `hasArrayIndex == 0` (production decoder expects no extra bytes)
- Empty ERROR/REJECT/ABORT responses are 21 bytes; adapter minimum length check incorrectly required 24
- Signed numeric `-15` was rejected by formula-prefix policy (false positive on `-` prefix)
- Verifier negative mutations leaked when checks matched type-definition tokens in `combined` text instead of adapter enforcement sites
- UDP delayed fixture callbacks could call `send` on a closed socket

Fixes applied:

- Unified request/response layout against production `encodeRequestPacket` / `decodeResponsePacket` (reads at offset 28, results at offset 21)
- Response encoder `hasArrayIndex == 0` writes only 1 byte flag (no trailing uint32)
- Request decoder always skips 4-byte arrayIndex slot to match request encoder
- Encoder end-of-buffer `offset === total` guard (`BACNET_TEST_ENCODER_SIZE_MISMATCH`)
- `decodeResponsePacket` minimum frame length corrected to 21
- Formula-prefix rejection limited to string-like value types
- Verifier checks moved to `adapterText` / `targetPolicyText` / `normalizerText` enforcement patterns
- Fixture server uses captured `activeServer` with safe delayed send/close

## Verifier negative cases

Verifier script: `deploy/offline-bundle/scripts/verify-bacnet-production-readonly-adapter-edge.sh`

Supports `EDGE_BACNET_PRODUCTION_DIR` and related path overrides for negative fixtures.

Dry-run verifier negative matrix: **36/36 rejected**, **0 leaked**.

Success token: `BACNET_PRODUCTION_READONLY_ADAPTER_VERIFIED`.

## Dry-run / smoke results

- `edge-c6-bacnet-production-adapter-dry-run.sh`: **PASS** — **192 cases**, `UFMS_EDGE_C6_05_BACNET_PRODUCTION_ADAPTER_PASS`, `UFMS_EDGE_C6_05A_VERIFICATION_CLOSURE_PASS`, `VERIFIER_NEGATIVE_TESTS_36_OF_36_REJECTED`
- `edge-c6-bacnet-production-adapter-smoke.sh`: **PASS** — `UFMS_EDGE_C6_05_BACNET_PRODUCTION_ADAPTER_PASS`

## Runtime / package / gate status

- Production adapter **not** registered in runtime index, connector-manager, or connector-registry
- `package.json` / `package-lock.json` unchanged (no third-party BACnet dependency)
- Gate state preserved:
  - `readOnlyFoundationEnforcementGate=PASS`
  - `controlledPilotGate=DEFERRED`
  - `readOnlyEnforcementGate=DEFERRED`
  - `decision=BLOCKED_NOT_PRODUCTION_READY`
  - `realConnectivityEnabled=false`
  - `supportsWriteback=false`
- `.runtime` remains untracked

## Remaining limitations

- Minimal BACnet/IP PDU codec for fixture compatibility only (not full BER/ASN.1 stack)
- No ReadRange, COV, alarm ack, or device control paths
- No production Who-Is broadcast; discovery limited to test-mode loopback
- No runtime polling scheduler or connector-manager registration
- Target resolution provider not wired to deployment enablement in this task

## Approval boundary

**BACnet Production Adapter Code Complete ≠ Pilot Approval**

**BACnet Production Adapter Code Complete ≠ Production Approval**

`realConnectivityEnabled` remains `false`. Connector matrix decision remains `BLOCKED_NOT_PRODUCTION_READY`.
