# Airport SNMP Systems Integration Overview R1

## Purpose

This derived evidence pack summarizes the airport MMS systems integration scope for ONE, with emphasis on SNMP-based integrations requiring confirmed MIB, OID, trap, and alarm mapping information.

No raw customer PDF, ZIP, Excel, or MIB files are included in this pack. The content below is sanitized and derived from the customer-provided integration context.

## Customer Airport MMS Integration Scope

| System | Vendor | Protocol / Status | ONE Integration Readiness |
| --- | --- | --- | --- |
| CCTV | Bosch | OPC Ready | EDGE OPC connector can be mapped after endpoint details are confirmed. |
| PA | Bosch | OPC Ready | EDGE OPC connector can be mapped after endpoint details are confirmed. |
| ACS | Bosch | OPC Ready | EDGE OPC connector can be mapped after endpoint details are confirmed. |
| Facial Recognition | Cognitec | API Ready | EDGE/API integration can be mapped after API contract and credentials are confirmed. |
| IPTV | Tonna | SNMP TBA | SNMP scope and technical data pending. |
| Clock System | Mobatime | SNMP, necessary information in progress | DTS 4160 alarm OID and sample values are captured in this evidence pack; full MIB confirmation remains required. |
| Radio System | BHE | SNMP, information required | Requires RS232-to-TCP/IP converter and request to BHE for MIB file, OID list, trap definition, and alarm mapping. |
| PABX | NEC | SNMP, necessary information in progress | SNMP scope and technical data pending. |
| Toll Carpark | Not confirmed | Modbus-to-SNMP TBA | Gateway approach and SNMP exposure pending. |

## Protocol Summary

| Protocol | Role in Airport Integration | Key Evidence Required |
| --- | --- | --- |
| OPC | Integration path for Bosch CCTV, PA, and ACS systems marked OPC Ready. | OPC endpoint, tag list, alarm/event semantics, security and network details. |
| API | Integration path for Cognitec Facial Recognition marked API Ready. | API contract, authentication model, event payloads, rate limits, and test samples. |
| SNMP | Integration path for IPTV, Clock System, Radio System, and PABX. | SNMP version, community or SNMPv3 credentials, MIB, OID list, trap definitions, alarm mapping, polling/trap behavior. |
| Modbus-to-SNMP | Candidate integration path for Toll Carpark. | Gateway model, Modbus register map, generated SNMP MIB/OIDs, alarm mapping, polling/trap behavior. |

## ONE Mapping

| ONE Layer | Mapping |
| --- | --- |
| EDGE protocol connector | Connects to OPC, API, SNMP, or Modbus-to-SNMP endpoints at the airport system boundary. |
| LINK normalization | Converts vendor-specific points, OIDs, traps, and payloads into consistent ONE event, alarm, asset, and evidence records. |
| ONE Alarm Console | Presents active and cleared alarms with raw evidence and decoded alarm labels. |
| ONE Fault/Event | Converts normalized alarms into event timelines and fault candidates. |
| ONE Work Management | Supports MMS work order recommendations and field response routing. |
| ONE Evidence/Reports | Preserves raw OID/value evidence, decoder versions, source references, and exportable integration proof. |

## Integration Risk

| Risk | Impact | Required Mitigation |
| --- | --- | --- |
| Missing MIB, OID, or trap mapping | ONE cannot reliably decode vendor alarms or certify event semantics. | Request vendor MIB, full OID list, trap definitions, and alarm mapping. |
| SNMPv2c vs SNMPv3 uncertainty | Security design and credential handling cannot be finalized. | Confirm supported SNMP versions and required security mode for each device. |
| Polling vs trap uncertainty | EDGE connector behavior, event latency, and clear detection cannot be finalized. | Confirm whether each system supports polling, traps, or both. |
| Device location and asset ID unknown | Alarms cannot be reliably tied to HMI map locations or MMS assets. | Confirm asset IDs, site locations, and hierarchy mapping. |
| BHE converter requirement | SNMP availability may depend on RS232-to-TCP/IP converter behavior rather than native radio equipment exposure. | Confirm converter model, protocol translation capability, network setup, and SNMP exposure after conversion. |
