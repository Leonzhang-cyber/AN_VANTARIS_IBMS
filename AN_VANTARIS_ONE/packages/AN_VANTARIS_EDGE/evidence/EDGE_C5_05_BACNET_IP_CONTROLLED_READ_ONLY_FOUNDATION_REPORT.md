# EDGE C5-05 BACnet/IP Controlled Read-only Foundation Report

## Scope

`UFMS-EDGE-C5-05` introduces local controlled read-only BACnet/IP foundation for the `bacnet` connector only.

## Baseline

- `3032027 feat(edge): add modbus tcp readonly foundation`

## BACnet connector current maturity

- `currentMaturity=FOUNDATION_READY`
- `requestedMode=FOUNDATION_ONLY`
- `permittedMode=SYNTHETIC_ONLY`
- `syntheticFixtureOnly=true`
- `realConnectivityEnabled=false`
- `productionDependencyIncluded=false`
- `supportsWriteback=false`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`

## Policy summary

- transport: `BACNET_IP`
- allowed services: READ_PROPERTY, READ_PROPERTY_MULTIPLE
- synthetic target: `bacnet.fixture.invalid:47808`
- device instance allowlist: `[1001]`
- broadcast/BBMD/FDR/COV disabled
- max objects/properties/APDU/response limits enforced
- synthetic transport only; network access disabled

## Service enforcement

- Read services allowed; write/create/delete/COV/DCC/reinitialize denied
- Who-Is/I-Am discovery disabled (`BACNET_DISCOVERY_DISABLED`)

## Target/port policy

- Allowlisted synthetic hostname and port 47808 only
- Loopback/private/link-local/multicast/metadata/broadcast rejected

## Broadcast/BBMD/FDR restrictions

- `broadcastAllowed=false`, `bbmdAllowed=false`, `foreignDeviceRegistrationAllowed=false`

## Device instance policy

- Range 0–4194302; wildcard 4194303 rejected; policy allowlist `[1001]`

## Object/property allowlist

- Read-type objects allowed; OUTPUT types denied by default
- Present Value read-only; PRIORITY_ARRAY and write-sensitive properties denied

## Request/response limits

- Object/property count, APDU size, invoke ID, segmentation (disabled), duplicate detection

## Error/Reject/Abort handling

- Error, Reject, Abort responses fail validation; not parsed as normal data

## Retry/backoff

- Deterministic exponential backoff; transport errors retryable; policy errors non-retryable

## Synthetic transport proof

- `executeSyntheticBacnetFixture()` → `SYNTHETIC_TRANSPORT_ONLY`
- No UDP socket, broadcast, Who-Is, or BACnet tools

## BACnet/IP native security limitations

BACnet/IP lacks native encryption and strong authentication. Foundation models reference-only credentials and rejects plaintext credential fields.

## Dry-run result

- `edge-c5-bacnet-ip-readonly-dry-run.sh`: **124/124 PASS**
- Readiness key: `UFMS_EDGE_C5_05_BACNET_IP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`

## Smoke result

- `edge-c5-bacnet-ip-readonly-smoke.sh`: **PASS**

## Package validation

- `validate-edge-package.sh`: **PASS**

## Boundary scan

- `edge-boundary-scan.sh`: **PASS**

## Isolation result

- `validate-ufms-ibms-isolation.sh`: **PASS** (`hard_fail_count=0`)

## Connector blocked state

- Unchanged: `BLOCKED_NOT_PRODUCTION_READY`

## Limitations

- No real BACnet/IP connectivity
- No UDP socket or broadcast
- Synthetic point table only
- `readOnlyEnforcementGate=DEFERRED`

## Acceptance result

`BACNET_IP_READ_ONLY_FOUNDATION_ACCEPTED`

## Readiness key

`UFMS_EDGE_C5_05_BACNET_IP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
