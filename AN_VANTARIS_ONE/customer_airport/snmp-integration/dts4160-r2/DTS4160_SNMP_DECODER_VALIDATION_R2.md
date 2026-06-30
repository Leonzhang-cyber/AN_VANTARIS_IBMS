# DTS4160 SNMP Decoder Validation R2

## Purpose

This R2 pack defines a controlled validation boundary for DTS 4160 SNMP alarm decoding based on the existing derived R1 evidence and the known alarm samples. It is documentation and JSON evidence only.

This pack does not implement runtime decoder logic, does not claim production validation, and does not include raw customer PDF, MIB, Excel, or ZIP files.

## R1 Evidence Inputs

| Evidence Item | Value |
| --- | --- |
| Device | DTS 4160 grandmaster |
| Vendor / source context | Mobatime/DTS |
| System | Clock System / Time Synchronization / Master Clock |
| Alarm OID | `1.3.6.1.4.1.13842.4.4160.1.8` |
| Active sample | `00408080.00000000` |
| Clear sample | `00000000.00000000` |
| Active decoded alarms | GNSS Sync Lost; No valid Time Source; No DTS Link |
| Clear decoded alarms | none |

## Controlled Validation Boundary

R2 validates only the behavior that is supported by R1 evidence:

- The known alarm OID is preserved exactly.
- The known active sample maps to alarm state `ACTIVE`.
- The known clear sample maps to alarm state `CLEARED`.
- The active sample returns the three sample-confirmed decoded labels.
- The clear sample returns an empty decoded alarm list.
- Evidence fields preserve raw OID, raw value, decoder contract version, source reference, and verification status.

R2 does not validate:

- Full DTS 4160 alarm coverage.
- Exact bit indexes.
- Byte order or bit order.
- Trap payload behavior.
- SNMP version, polling interval, security mode, or live device access.
- Production asset/location mapping.

## Alarm Mask Handling Principle

The DTS 4160 alarm value is treated as an 8-byte / 64-bit alarm mask string. The R1 active sample is non-zero and therefore represents an active alarm state. The R1 clear sample is all zero and therefore represents a cleared state.

The active sample is allowed to decode only to the sample-confirmed labels:

1. GNSS Sync Lost
2. No valid Time Source
3. No DTS Link

Bit-level decoding remains gated until vendor MIB and customer bit-order confirmation are available.

## Validation Controls

| Control | Required Behavior |
| --- | --- |
| No invented bit indexes | Bit index must remain `null` until verified. |
| No expanded alarm table | Only sample-confirmed labels may appear in R2 expected decoded alarms. |
| Raw evidence retention | Raw OID and raw value must be preserved in every expected event. |
| Sample boundary | Fixtures must be marked derived/sample-controlled, not live customer readings. |
| Production boundary | Output must not claim live NEC, BHE, DTS, or airport production integration. |
| Customer confirmation gate | MIB, bit order, SNMP access, trap behavior, and asset/location mapping remain pending. |

## ONE Validation Chain

```text
EDGE SNMP sample input
  -> controlled DTS4160 decoder contract
  -> LINK normalized event envelope
  -> ONE Alarm Console candidate
  -> Fault/Event candidate
  -> Work Management recommendation
  -> Evidence / Reports sample output
```

This is a validation chain for derived sample evidence only. It is not a runtime implementation.

## R2 Acceptance Criteria

| Test | Acceptance Criteria |
| --- | --- |
| Active sample fixture | `00408080.00000000` produces `ACTIVE` and exactly the three sample-confirmed labels. |
| Clear sample fixture | `00000000.00000000` produces `CLEARED` and no decoded alarms. |
| Unknown non-zero sample | Marked `UNVALIDATED_NONZERO_SAMPLE`; no decoded labels invented. |
| Malformed sample | Marked invalid; no decoded labels returned. |
| Evidence envelope | Includes raw OID, raw value, contract version, source reference, and verification status. |

## Open Confirmation Items

- Vendor MIB and alarm table.
- Exact bit order and byte order.
- Whether `No DTS Link` naming should be Optical, LAN, or another site-specific label.
- SNMP v1/v2c/v3 support and credential model.
- Polling versus trap approach.
- Site asset ID, physical location, and HMI map linkage.
