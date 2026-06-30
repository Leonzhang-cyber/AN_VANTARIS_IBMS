# DTS4160 SNMP Decoder Validation R2 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `DTS4160_SNMP_DECODER_VALIDATION_R2.md` | Human-readable R2 validation boundary, controls, acceptance criteria, and open confirmations. |
| `dts4160-decoder-contract.v2.json` | Controlled decoder contract derived from R1 sample evidence. |
| `dts4160-decoder-validation-fixtures.v2.json` | Active, clear, unknown non-zero, and malformed-sample validation fixtures. |
| `dts4160-expected-normalized-events.v2.json` | Expected ONE normalized event examples for controlled validation. |
| `dts4160-validation-test-plan.v2.json` | JSON test plan for sample interpretation, guardrails, and event envelope checks. |

## Scope

This R2 pack is documentation and JSON only. It prepares a controlled validation frame for DTS4160 SNMP sample decoding based on existing R1 derived evidence.

## Confirmed From R1

| Item | Value |
| --- | --- |
| Device | DTS 4160 grandmaster |
| Vendor / source context | Mobatime/DTS |
| Alarm OID | `1.3.6.1.4.1.13842.4.4160.1.8` |
| Active sample | `00408080.00000000` |
| Clear sample | `00000000.00000000` |
| Active decoded alarms | GNSS Sync Lost; No valid Time Source; No DTS Link |

## Guardrails Preserved

- No runtime decoder implementation.
- No frontend, backend, API, menu, route, or schema changes.
- No raw customer PDF, MIB, Excel, or ZIP files.
- No production validation claim.
- No invented bit indexes.
- No invented additional DTS alarm labels.
- No trap behavior claims.

## Pending Before Implementation

- Vendor MIB and full alarm table.
- Exact bit order and byte order.
- Confirmation of DTS link naming.
- SNMP version and credential model.
- Polling versus trap approach.
- Site asset ID, physical location, and HMI map linkage.

## Recommended Next Step

Use this R2 pack as the basis for `ONE-AIRPORT-DTS4160-SNMP-DECODER-R3` only after vendor/customer MIB confirmation and explicit user approval for implementation or validator logic.
