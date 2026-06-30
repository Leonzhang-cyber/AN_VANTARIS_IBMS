# BHE BRTL32 SNMP Mapping R2 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `BHE_BRTL32_SNMP_VENDOR_REQUEST_R2.md` | Formal technical request document for BHE/customer. |
| `bhe-brtl32-snmp-request-email-r2.md` | Sendable professional email draft requesting BHE SNMP materials. |
| `bhe-brtl32-one-field-mapping.v1.json` | Structured ONE mapping template with OIDs and codes left pending. |
| `bhe-brtl32-snmp-test-plan.v1.json` | Structured test plan for SNMP access, telemetry, alarms, traps, converter behavior, and ONE evidence. |
| `BHE_BRTL32_SNMP_MAPPING_R2_SUMMARY.md` | Summary of scope, knowns, pending items, ONE mapping, and next actions. |

## What Is Known

The airport MMS Schedule lists the Radio System as BHE and SNMP-based. It also states that an RS232-to-TCP/IP converter is required and that BHE must be asked for:

- MIB file
- OID list
- Trap definition
- Alarm mapping

The exact BHE device context for this package is BRTL32.

## What Is Pending

| Pending Item | Owner |
| --- | --- |
| Whether BRTL32 natively supports SNMP or requires converter/gateway exposure. | vendor/customer |
| RS232-to-TCP/IP converter model and protocol behavior. | vendor/customer |
| SNMP v1/v2c/v3 support and preferred read-only security mode. | vendor |
| MIB file and full OID list. | vendor |
| Trap OIDs, varbind format, and active/clear trap behavior. | vendor |
| Alarm names, alarm codes, severity, active values, clear values, latching, and acknowledgement behavior. | vendor |
| RF parameter OIDs for input RSSI, output power, forward/reflected power, VSWR, RX/TX, PA, channel/frequency, temperature, power supply, and module health. | vendor |
| Site IP address, asset ID, and physical location mapping. | customer |
| Test alarm procedure, normal samples, active samples, clear samples, and restart/communication-loss behavior. | vendor/customer |

## Why BHE BRTL32 Matters To ONE

BHE BRTL32 is part of the airport Radio System integration scope. Without authoritative SNMP data, ONE cannot safely normalize radio alarms, display RF operating condition, route radio faults into operations, or preserve evidence for MMS reporting. This R2 pack prepares the exact vendor/customer request and gives the ONE integration team a field mapping and test structure ready to populate after technical data is received.

## How It Maps To VANTARIS ONE

| ONE Capability | BHE BRTL32 Mapping |
| --- | --- |
| EDGE SNMP Connector | Connects to the BHE endpoint or converter/gateway endpoint after SNMP exposure is confirmed. |
| LINK normalization | Converts raw polling responses or trap payloads into normalized radio telemetry, alarms, events, and evidence. |
| Alarm Console | Displays active and cleared BHE radio alarms with severity and source evidence. |
| Fault Operations | Groups repeated or correlated BHE radio conditions into fault candidates and event timelines. |
| Work Management / MMS | Uses vendor recommended actions and work-order implication fields to support maintenance workflows. |
| HMI Map | Links BHE alarm state and radio health to confirmed airport physical location and asset hierarchy. |
| Evidence / Reports | Exports raw OID/trap evidence, decoded values, mapping references, and test evidence. |

## Recommended Next Actions

1. Send vendor request email.
2. Collect MIB/OID/trap/alarm mapping.
3. Run SNMP test on site.
4. Create BHE decoder R3 after vendor data is received.

## Confidentiality And Evidence Boundary

This R2 package contains only derived documentation, templates, and test-plan JSON. It does not include raw customer PDF, ZIP, Excel, or MIB files, and it does not invent BHE OID values, alarm codes, or trap payload formats.
