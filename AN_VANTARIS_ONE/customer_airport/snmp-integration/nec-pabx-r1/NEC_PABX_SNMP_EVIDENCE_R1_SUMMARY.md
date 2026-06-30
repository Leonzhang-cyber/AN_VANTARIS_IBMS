# NEC PABX SNMP Evidence R1 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `NEC_PABX_SNMP_EVIDENCE_R1.md` | Main derived evidence document for NEC PABX SNMP coverage. |
| `nec-pabx-snmp-oid-mapping.v1.json` | Structured OID mapping with exact known OIDs and pending group-level coverage. |
| `nec-pabx-snmp-fixtures.v1.json` | Synthetic fixture set for alarm lamps, failure message, CPU candidate, and port candidate. |
| `nec-pabx-one-normalized-events.v1.json` | Example ONE normalized events derived from synthetic fixtures. |
| `NEC_PABX_ONE_INTEGRATION_PLAN_R1.md` | ONE integration plan and R1/R2/R3 roadmap. |
| `NEC_PABX_SNMP_EVIDENCE_R1_SUMMARY.md` | Summary of scope, boundary, confirmed OIDs, pending verification, and next step. |

## Scope

This R1 pack is documentation and JSON evidence only for the customer_airport NEC PABX SNMP projection. It supports planning for EDGE SNMP Connector, LINK normalized events, ONE Alarm Console, Fault Candidate, Work Order recommendation, Evidence Center, and export reports.

## Boundary

This pack does not:

- Modify frontend, backend, API, routes, menu, or database schema.
- Create runtime decoder logic.
- Add raw customer PDF, ZIP, Excel, or MIB files.
- Claim live NEC PABX production integration.
- Turn VANTARIS ONE into an airport-only system.

Synthetic fixtures and normalized event examples are clearly marked as synthetic and are not live customer readings.

## Confirmed OIDs

| Point | OID |
| --- | --- |
| Alarm Group | `1.3.6.1.4.1.119.2.3.76.2.1` |
| Lamp Status and Lamp Clear | `1.3.6.1.4.1.119.2.3.76.2.1.1.0` |
| Major Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.2.0` |
| Minor Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.3.0` |
| Supervisor Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.4.0` |
| Failure Message | `1.3.6.1.4.1.119.2.3.76.2.2.1.0` |

Known value semantics:

- Major / Minor lamp status: `0 = lamp off`, `1 = lamp lighting`.
- Supervisor lamp: `0 = Not available`, `1 = Supervisor lamp off`, `2 = Supervisor lamp lighting`.
- Failure Message: string up to 255 characters, sent as a trap to SNMP Manager.

## Pending Verification

- Exact MIB/OID children for CPU, traffic, port, terminal, sysMessage, and registrationInfo groups.
- Exact system message trap and failure message trap payload formats.
- SNMP version, access mode, polling interval, trap receiver configuration, and security settings.
- NEC PABX model, firmware version, and site deployment details.
- Customer asset ID, site/zone/location mapping, and HMI map linkage.
- Severity policy, active/clear behavior, latching behavior, and work order thresholds.

## Recommended Next Step

Proceed to NEC PABX R2 only after exact NEC MIB/OID/trap verification is available. R2 should expand the mapping for CPU, traffic, port, terminal, sysMessage, and registrationInfo. R3 should add optional decoder or SNMP fixture validation only after explicit user approval.
