# EDGE C5-03 SNMP Controlled Read-only Foundation Report

## Scope

`UFMS-EDGE-C5-03` introduces local controlled read-only SNMP foundation for the `snmp` connector only.

## Baseline

- `0f63917 feat(edge): add http polling readonly foundation`

## SNMP connector current maturity

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

- preferred version: `3` (SNMPv3)
- production allowed versions: `3` only
- allowed operations: `GET`, `GETNEXT`, `GETBULK`
- denied operations: `SET`, `INFORM`, `TRAP_SEND`
- synthetic allowlisted target: `snmp.fixture.invalid`
- OID prefix allowlist: `1.3.6.1.2.1` (component-boundary enforced)
- denied OID prefix: `1.3.6.1.6.3.15`
- max varbinds: `100`
- max response bytes: `1048576`
- walk depth/rows: `32` / `1000`
- timeout: `3000ms`
- retry: max `3`, exponential backoff base `100ms`, multiplier `2`, max `5000ms`
- credential mode: `REFERENCE_ONLY`
- synthetic transport only; network access disabled

## Version policy

- SNMPv3 accepted in foundation model
- v1/v2c rejected with `SNMP_LEGACY_VERSION_PRODUCTION_BLOCKED`
- v1/v2c not production approved; no plaintext community

## Operation enforcement

- GET / GETNEXT / GETBULK accepted
- SET rejected with `SNMP_SET_NOT_ALLOWED`
- INFORM / TRAP_SEND rejected with `SNMP_OPERATION_NOT_ALLOWED`
- No SET execution path in synthetic transport

## Target allowlist

- synthetic hostname allowlist only (`snmp.fixture.invalid`)
- localhost/loopback/private/link-local/multicast/metadata/unspecified rejected
- IPv4-mapped IPv6 and decimal/octal/hex bypass forms rejected
- Pure logic validation; no DNS, UDP, or socket

## Target risk model

- `normalizeSnmpTarget()` + `evaluateSnmpTargetRisk()` classify loopback, private, link-local, multicast, metadata, non-allowlisted, and malformed targets
- Embedded credential syntax in target rejected

## Credential model

- `credentialRef` only (e.g. `secret://edge/snmp/example`)
- Plaintext community/auth/priv/username rejected
- No `.env`, keychain, or credential store resolution

## OID normalization/allowlist

- `normalizeSnmpOid()` strips leading dots; canonical form `1.3.6.1.2.1...`
- `oidHasPrefix()` uses component-boundary matching (e.g. `1.3.6.1.2.10` not allowed under `1.3.6.1.2.1`)
- Denied prefixes checked before allowlist

## Response validation

- Varbind count, response bytes, OID format/allowlist, value type allowlist, error status, duplicate OID, walk row/depth limits
- Allowed types: INTEGER, OCTET_STRING, OBJECT_IDENTIFIER, IP_ADDRESS, COUNTER32, GAUGE32, TIMETICKS, COUNTER64, NULL

## Retry/backoff

- `calculateSnmpRetryBackoff()` deterministic exponential backoff with clamp
- `evaluateSnmpRetryDecision()` distinguishes retryable (TIMEOUT, TRANSPORT_RETRYABLE) vs non-retryable (AUTH_FAILURE, OID_NOT_ALLOWED, POLICY_VIOLATION)
- No sleep or real retry

## Synthetic transport proof

- `executeSyntheticSnmpFixture()` processes validation-session JSON fixtures only
- Output mode: `SYNTHETIC_TRANSPORT_ONLY`
- Can simulate timeout, malformed, oversize, and policy violations deterministically

## No-network/no-DNS/no-socket proof

- `networkAccessAllowed=false`, `dnsResolutionMode=MODELED_ONLY`, `syntheticTransportOnly=true`
- Source scan: no `dgram`, `createSocket`, `dns.lookup`, `snmpget`, `snmpwalk`, or SNMP library imports

## Dry-run result

- `edge-c5-snmp-readonly-dry-run.sh`: **81/81 PASS**
- Readiness key: `UFMS_EDGE_C5_03_SNMP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`

## Smoke result

- `edge-c5-snmp-readonly-smoke.sh`: **PASS**

## Package validation

- `validate-edge-package.sh`: **PASS**

## Boundary scan

- `edge-boundary-scan.sh`: **PASS**

## Isolation result

- `validate-ufms-ibms-isolation.sh`: **PASS** (`hard_fail_count=0`)

## SNMP Connector blocked state

- Unchanged: `BLOCKED_NOT_PRODUCTION_READY`
- Enablement matrix not promoted to pilot or production

## Limitations

- No real SNMP agent connectivity
- No UDP transport or SNMP protocol library
- No DNS resolution or network I/O
- Credential references are modeled strings only
- v1/v2c legacy risk recorded but not production approved
- `readOnlyEnforcementGate=DEFERRED`

## Acceptance result

`SNMP_READ_ONLY_FOUNDATION_ACCEPTED`

## Readiness key

`UFMS_EDGE_C5_03_SNMP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
