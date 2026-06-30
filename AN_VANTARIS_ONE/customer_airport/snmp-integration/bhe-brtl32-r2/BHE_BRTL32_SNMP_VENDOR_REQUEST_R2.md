# BHE BRTL32 SNMP Vendor Request R2

## A. Purpose

VANTARIS ONE requires confirmed SNMP integration information for the BHE BRTL32 Radio System so the airport MMS integration can be configured, tested, and evidenced through:

- EDGE SNMP Connector
- LINK normalized event flow
- ONE Alarm Console
- Fault Operations
- Work Management / MMS
- HMI Map
- Evidence / Reports

This request is limited to technical data required for monitoring, alarm normalization, evidence capture, and operational handoff. Read-only SNMP is sufficient for monitoring unless BHE confirms supported acknowledgement or command behavior.

## B. Device Identity Required

Please provide the following identity details for each BHE BRTL32 device or gateway endpoint:

| Required Field | Notes |
| --- | --- |
| Manufacturer / vendor | Confirm BHE as manufacturer/vendor or provide exact OEM details. |
| Exact model | BRTL32. Confirm variant if applicable. |
| Device role | Confirm radio repeater / radio system component role. |
| Hardware revision | Required for supportability and MIB compatibility. |
| Firmware version | Required for MIB/OID compatibility. |
| Serial number | Required for asset identification. |
| Hostname / device name | Required for site operations and evidence correlation. |
| IP address after RS232-to-TCP/IP conversion if applicable | Required if SNMP endpoint is converter/gateway exposed. |
| Physical location | Site / building / floor / room / rack / panel. |
| Asset tag / customer asset ID if available | Required for ONE asset mapping and Work Management / MMS. |

## C. SNMP Version Support

Please confirm:

- SNMP v1 support
- SNMP v2c support
- SNMP v3 support
- Preferred security mode
- Read-only mode
- SNMP access enable procedure
- Whether SNMP is native to BRTL32 or exposed via converter/gateway

Do not assume SNMPv3 support unless explicitly confirmed by BHE or the customer.

## D. SNMP Communication Details

Please provide:

| Required Detail | Notes |
| --- | --- |
| Polling port | Normally UDP 161; confirm actual port. |
| Trap destination port | Normally UDP 162; confirm actual port. |
| Community string requirement for v1/v2c | Provide site-specific handling guidance through secure channel only. |
| SNMPv3 username/auth/privacy algorithms if supported | Confirm auth protocol, privacy protocol, and security level. |
| Source IP and destination IP requirements | Required for firewall and allow-listing. |
| IP whitelist / ACL | Confirm device-side or gateway-side access control. |
| Firewall requirements | Include inbound and outbound rules for polling and traps. |
| Recommended polling interval | Include safe operational interval. |
| Max polling frequency | Include device/gateway performance limits. |
| Trap receiver configuration | Include destination configuration steps and restart requirements. |
| Time sync requirements | Confirm whether device/gateway clock sync is required for trap timestamps. |

## E. MIB / OID / Trap Definition

Please provide the authoritative SNMP data package:

| Required Item | Notes |
| --- | --- |
| MIB file | Official MIB matching hardware/firmware version. |
| Full OID list | Include object name, OID, data type, access type, units, scale/multiplier, normal value, alarm value, and clear value. |
| Object name | Required for readable mapping. |
| OID | Required for polling/trap varbind mapping. |
| Data type | Integer, string, gauge, counter, bitmap, enum, or other. |
| Access type | Read-only, read-write, command, or trap-only. |
| Unit | dBm, W, C, enum, boolean, text, or other. |
| Scale / multiplier | Required to decode raw numeric values. |
| Normal value | Required for baseline monitoring. |
| Alarm value | Required for active alarm detection. |
| Clear value | Required for clear behavior. |
| Trap OID list | Include enterprise OID and specific trap OIDs. |
| Trap payload format | Include varbind order, object names, types, units, and examples. |
| Trap severity field | Confirm whether severity is explicit or derived. |
| Trap active/clear behavior | Confirm whether active and clear traps are both emitted. |

## F. Radio Operational Parameters

Please provide OID/trap mapping for the following radio operational parameters where available:

| Parameter | Requested Mapping |
| --- | --- |
| Repeater identification | Object name, OID, data type, and sample value. |
| Model | Object name, OID, data type, and sample value. |
| Serial number | Object name, OID, data type, and sample value. |
| Firmware version | Object name, OID, data type, and sample value. |
| Location | Object name, OID, data type, and sample value. |
| Input RSSI | OID, unit, scale, normal range, alarm threshold. |
| Output power | OID, unit, scale, normal range, alarm threshold. |
| Forward power | OID, unit, scale, normal range, alarm threshold. |
| Reflected power | OID, unit, scale, normal range, alarm threshold. |
| VSWR if available | OID, unit, scale, normal range, alarm threshold. |
| RX status | Enum values and status meaning. |
| TX status | Enum values and status meaning. |
| PA status | Enum values and status meaning. |
| Channel / frequency / band | OID, unit, and value format. |
| Temperature | OID, unit, scale, normal range, alarm threshold. |
| Power supply status | Enum values and status meaning. |
| Battery / backup power status if available | OID, unit/status, and alarm threshold. |
| Fan / module health if available | Enum values and status meaning. |

## G. Alarm Mapping

Please provide a complete alarm mapping table with:

| Required Field | Notes |
| --- | --- |
| Alarm name | Human-readable alarm label. |
| Alarm code | Vendor alarm code if available. |
| OID / trap OID | Polling OID, trap OID, or both. |
| Bit index if bitmap | Required if alarm source is a bitmap. |
| Severity | Vendor severity or recommended severity. |
| Active value | Value indicating active alarm. |
| Clear value | Value indicating cleared alarm. |
| Latching behavior | Latched, non-latched, or configurable. |
| Acknowledgement support | Confirm whether acknowledgement exists. |
| Acknowledge command OID if supported | Only if SNMP command acknowledgement is supported. |
| Alarm suppression / maintenance mode | Confirm any maintenance or inhibited state. |
| Recommended action | Vendor recommended operator action. |
| Fault category | Radio link, RF, power, hardware, communication, environment, or other. |
| Work order implication | Confirm whether this alarm should create or recommend MMS work order action. |

## H. Integration Testing Samples

Please provide the following evidence samples:

| Sample | Purpose |
| --- | --- |
| Normal snmpwalk sample | Establish baseline accessible OIDs and values. |
| Active alarm sample | Verify active alarm detection. |
| Cleared alarm sample | Verify clear behavior. |
| Trap packet sample | Verify trap parsing and event envelope. |
| RSSI / output power sample values | Verify RF telemetry unit, scale, and thresholds. |
| Screenshot from vendor tool if available | Cross-check SNMP values with vendor display. |
| Test alarm procedure | Repeatable procedure for site acceptance testing. |
| Device restart behavior | Expected polling/trap behavior during restart. |
| Communication loss behavior | Expected behavior when device or converter is unreachable. |

## I. Open Questions

1. Does BRTL32 natively support SNMP, or only through an RS232-to-TCP/IP converter?
2. Does the converter expose SNMP, TCP socket, serial-over-IP, or another protocol?
3. Is there a vendor-recommended converter model?
4. Does BHE provide a simulator or sample MIB?
5. Are traps supported, or polling only?
6. Are alarm acknowledgement commands supported through SNMP?
7. Are RF parameters exposed as scalar OIDs, table rows, traps, or vendor-specific payloads?
8. Are active and clear alarm states available through both polling and traps?
