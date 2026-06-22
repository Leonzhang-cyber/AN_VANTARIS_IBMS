# EDGE C5-04 Modbus TCP Controlled Read-only Foundation Report

## Scope

`UFMS-EDGE-C5-04` introduces local controlled read-only Modbus TCP foundation for the `modbus` connector only.

## Baseline

- `0a18fe0 feat(edge): add snmp readonly foundation`

## Modbus connector current maturity

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

- transport: `MODBUS_TCP` only
- allowed function codes: 1, 2, 3, 4 (read-only)
- denied function codes: 5, 6, 15, 16, 22, 23 (write)
- synthetic target: `modbus.fixture.invalid:502`
- unit ID allowlist: `[1]`
- register spaces and synthetic address ranges only
- max registers per request: 125
- max coils per request: 2000
- max response bytes: 1048576
- timeout: 3000ms
- synthetic transport only; network access disabled

## Read/write function enforcement

- FC 01/02/03/04 accepted as read-only operations
- FC 05/06/15/16/22/23 rejected with `MODBUS_WRITE_FUNCTION_PROHIBITED`
- Unknown/invalid function codes rejected

## Target/port policy

- Allowlisted synthetic hostname and port 502 only
- localhost/loopback/private/link-local/multicast/metadata/unspecified rejected
- IPv4 bypass forms and IPv4-mapped IPv6 rejected
- No DNS, TCP connect, or socket usage

## Unit ID policy

- Protocol range 0–247 with policy allowlist (default unitId=1)
- Broadcast unit ID not used for write operations

## Register spaces

| FC | Space |
|----|-------|
| 01 | COIL (0–99) |
| 02 | DISCRETE_INPUT (100–199) |
| 03 | HOLDING_REGISTER (1000–1099) |
| 04 | INPUT_REGISTER (2000–2099) |

## Address/quantity limits

- Numeric boundary checks; no string comparison
- End address overflow and request limit enforcement
- Register-space/function-code mapping enforced

## Response frame validation

- Transaction ID, protocol ID (0), unit ID, function code consistency
- Byte count vs payload length
- Oversize, malformed, short, and trailing frame rejection
- Exception responses (`functionCode | 0x80`) rejected

## Exception handling

- Modeled exception codes (01, 02, 03, 04, 06, 10, 11) marked as `MODBUS_EXCEPTION_RESPONSE` failure

## Decode model

- `decodeModbusRegisters()` for UInt16, Int16, UInt32, Int32, Float32, Boolean, RAW
- Explicit byteOrder and wordOrder modeling; no script execution or engineering unit conversion

## Retry/backoff

- Deterministic exponential backoff with clamp
- Retryable: TIMEOUT, CONNECTION_RESET, CONNECTION_REFUSED, SERVER_BUSY, GATEWAY_TARGET_FAILED
- No sleep or real retry

## Synthetic transport proof

- `executeSyntheticModbusFixture()` processes validation-session JSON only
- Output: `SYNTHETIC_TRANSPORT_ONLY`
- Write function fixtures rejected at policy gate

## No-network/no-DNS/no-socket proof

- Source scan: no `net.createConnection`, `dgram`, `dns.lookup`, `modpoll`, `mbpoll`, `nc`, `telnet`

## Modbus TCP native security limitations

Modbus TCP lacks native encryption and strong authentication. This foundation rejects plaintext credential fields and does not claim native Modbus TCP security. Production use requires additional transport security and operator approval.

## Dry-run result

- `edge-c5-modbus-tcp-readonly-dry-run.sh`: **104/104 PASS**
- Readiness key: `UFMS_EDGE_C5_04_MODBUS_TCP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`

## Smoke result

- `edge-c5-modbus-tcp-readonly-smoke.sh`: **PASS**

## Package validation

- `validate-edge-package.sh`: **PASS**

## Boundary scan

- `edge-boundary-scan.sh`: **PASS**

## Isolation result

- `validate-ufms-ibms-isolation.sh`: **PASS** (`hard_fail_count=0`)

## Connector blocked state

- Unchanged: `BLOCKED_NOT_PRODUCTION_READY`

## Limitations

- No real Modbus TCP connectivity
- No TCP socket or Modbus protocol library
- No DNS or network I/O
- Synthetic register map only; not production device mapping
- `readOnlyEnforcementGate=DEFERRED`

## Acceptance result

`MODBUS_TCP_READ_ONLY_FOUNDATION_ACCEPTED`

## Readiness key

`UFMS_EDGE_C5_04_MODBUS_TCP_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
