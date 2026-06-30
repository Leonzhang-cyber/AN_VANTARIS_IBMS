# ONE Airport SNMP Integration Evidence R1 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `AIRPORT_SNMP_SYSTEMS_INTEGRATION_OVERVIEW_R1.md` | Airport MMS integration overview and ONE mapping. |
| `DTS4160_SNMP_ALARM_DECODER_R1.md` | DTS 4160 SNMP alarm decoder notes, samples, and assumptions. |
| `dts4160-alarm-bit-mapping.v1.json` | Sanitized DTS 4160 alarm label mapping fixture with unverified bit indexes left null. |
| `dts4160-snmp-fixtures.v1.json` | Active and clear DTS 4160 SNMP sample fixtures. |
| `dts4160-one-normalized-events.v1.json` | Sample ONE normalized event objects for active and clear DTS 4160 samples. |
| `BHE_BRTL32_SNMP_REQUIREMENTS_R1.md` | Formal BHE BRTL32 SNMP requirements and request checklist. |
| `bhe-brtl32-snmp-request-checklist.v1.json` | Structured BHE checklist for vendor/customer evidence collection. |

## Scope

This pack creates derived, sanitized documentation and JSON fixtures for airport SNMP integration evidence covering:

- DTS 4160 grandmaster Clock System alarm OID and sample values.
- BHE BRTL32 Radio System SNMP evidence request requirements.
- ONE mapping from EDGE SNMP ingestion through LINK normalization, Alarm Console, Fault Operations, Work Management, HMI Map, Evidence Center, and report export.

## What Is Confirmed

| Item | Confirmed Value |
| --- | --- |
| DTS device | DTS 4160 grandmaster |
| DTS system context | Clock System / Time Synchronization / Master Clock |
| DTS vendor/source context | Mobatime/DTS |
| DTS alarm OID | `1.3.6.1.4.1.13842.4.4160.1.8` |
| DTS active sample | `00408080.00000000` |
| DTS clear sample | `00000000.00000000` |
| DTS decoded sample alarms | GNSS Sync Lost; No valid Time Source; No DTS Link |
| BHE system context | Radio System / BHE / BRTL32 |
| BHE integration constraint | Requires RS232-to-TCP/IP converter and vendor/customer SNMP details. |

## What Remains Pending

| Pending Item | Owner |
| --- | --- |
| DTS MIB, bit order, byte order, and full alarm bit mapping. | vendorToProvide |
| DTS SNMP version, polling/trap approach, and access credentials. | customerToConfirm |
| DTS asset, site, and location IDs. | customerToConfirm |
| BHE MIB file, full OID list, trap definition, and alarm mapping. | vendorToProvide |
| BHE RF parameters including input RSSI and output power. | vendorToProvide |
| BHE acknowledgement and clear alarm behavior. | vendorToProvide |
| BHE RS232-to-TCP/IP converter model and SNMP exposure behavior. | customerToConfirm |
| BHE exact asset/location mapping. | customerToConfirm |

## Why This Supports ONE Airport Integration

The pack separates confirmed evidence from pending assumptions. It gives ONE a traceable starting point for DTS 4160 SNMP alarm decoding, while preventing unsupported bit mappings or BHE OID/alarm invention. It also defines how derived SNMP evidence should flow into ONE operational surfaces: EDGE connectors, LINK normalization, Alarm Console, Fault Operations, Work Management, HMI Map, Evidence Center, and Reports.

## Recommended Next Tasks

1. `ONE-AIRPORT-DTS4160-SNMP-DECODER-R2`
2. `ONE-AIRPORT-BHE-BRTL32-SNMP-MAPPING-R2`
3. `EDGE-SNMP-CONNECTOR-READINESS-Rx`
4. `ONE-ALARM-EVIDENCE-SNMP-VIEW-Rx`

## Confidentiality Note

This evidence pack contains only derived documentation and JSON fixtures/specifications. Raw customer PDF, ZIP, Excel, and MIB files must remain outside git.
