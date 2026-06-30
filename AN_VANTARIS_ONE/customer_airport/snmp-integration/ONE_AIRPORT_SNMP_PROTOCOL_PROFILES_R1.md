# ONE Airport SNMP Protocol Profiles R1

## 1. Purpose

This document summarizes three customer-airport SNMP protocol profiles prepared for VANTARIS ONE integration:

1. DTS4160 / Mobatime Clock System SNMP Profile
2. BHE BRTL32 / Radio System SNMP Profile
3. NEC PABX / Telephony System SNMP Profile

This is a derived protocol-profile document only. It does not include customer raw PDF, MIB, Excel, ZIP, screenshots, or binary artifacts. It does not implement runtime decoder logic and does not modify frontend, backend, API, menu, route, or database schema.

VANTARIS ONE remains a cross-industry unified operations platform. The airport case is treated only as a customer-specific industry projection.

## 2. Common Integration Boundary

All three profiles follow the same integration chain:

Device / Subsystem SNMP Source  
-> EDGE SNMP Connector  
-> LINK Normalized Event  
-> ONE Alarm Console  
-> Fault Candidate / Fault Operations  
-> Work Management / MMS  
-> HMI Map / Location Context where available  
-> Evidence Center  
-> Export Report

EDGE is responsible for SNMP polling, trap intake, SNMP version handling, raw OID/value capture, connector diagnostics, local protocol health, and raw event envelope preparation.

LINK is responsible for normalized event shaping, source identity mapping, asset/system binding, event delivery consistency, retry/DLQ behavior where applicable, and standard event envelope alignment.

ONE is responsible for Alarm Console visibility, fault candidate creation, work order recommendation, operational context, evidence timeline, export report, and customer-facing operational assurance.

## 3. Profile A - DTS4160 / Mobatime Clock System

### System Role

DTS4160 / Mobatime Clock System provides time synchronization and Master Clock visibility. In airport operations, this line supports event timeline trust, event ordering, CCTV timestamp interpretation, access control sequence validation, BMS/EMS timestamp alignment, and work order timing.

### Protocol Type

Protocol: SNMP  
System Type: Clock System / Time Synchronization / Master Clock  
Vendor/System: Mobatime DTS4160  
Integration Readiness: R1 evidence completed  
Runtime Decoder Status: Not production-claimed

### Existing Evidence Artifacts

- DTS4160_SNMP_ALARM_DECODER_R1.md
- dts4160-alarm-bit-mapping.v1.json
- dts4160-snmp-fixtures.v1.json
- dts4160-one-normalized-events.v1.json

### Current Value

DTS4160 is valuable because it affects timestamp reliability and evidence timeline trust across CCTV, ACS, BMS, EMS, fault cases, and work orders.

### Pending Verification

- Exact MIB bit order
- SNMP polling versus trap behavior
- SNMPv2c versus SNMPv3
- Optical/LAN naming confirmation
- Customer-approved severity mapping

### Recommended Next Step

Prepare DTS4160 Decoder R2 only as a controlled synthetic fixture decoder task. Bit-order assumptions must be explicitly marked. Do not claim live production validation.

## 4. Profile B - BHE BRTL32 / Radio System

### System Role

BHE BRTL32 / Radio System supports radio communication availability. In airport operations, radio health can affect field coordination, maintenance dispatch, incident response, supervisor communication, and operational readiness.

### Protocol Type

Protocol: SNMP  
System Type: Radio System / Radio Repeater  
Vendor/System: BHE BRTL32  
Integration Readiness: Vendor request pack completed  
Runtime Decoder Status: Blocked until MIB/OID/trap/alarm mapping is received

### Existing Evidence Artifacts

- bhe-brtl32-r2/BHE_BRTL32_SNMP_VENDOR_REQUEST_R2.md
- bhe-brtl32-r2/bhe-brtl32-snmp-request-email-r2.md
- bhe-brtl32-r2/bhe-brtl32-one-field-mapping.v1.json
- bhe-brtl32-r2/bhe-brtl32-snmp-test-plan.v1.json
- bhe-brtl32-r2/BHE_BRTL32_SNMP_MAPPING_R2_SUMMARY.md

### Current Value

BHE BRTL32 is valuable because it supports radio communication availability, dispatch readiness, and field response coordination.

### Pending Customer/Vendor Information

- MIB file
- OID list
- Trap definition
- Alarm mapping
- RF parameter mapping
- RSSI / signal quality mapping
- Output power mapping
- Alarm acknowledge and clear behavior
- RS232-to-TCP/IP converter behavior
- SNMP exposure model
- SNMP version and security requirements

### Recommended Next Step

Send the prepared BHE vendor request email and checklist. Do not start BHE decoder implementation until MIB, OID, trap, and alarm mapping are returned and verified.

## 5. Profile C - NEC PABX / Telephony System

### System Role

NEC PABX / Telephony System supports airport telephony service and communication readiness. Major/minor alarm lamps, supervisor lamp state, and failure message traps can support alarm visibility, fault candidate creation, work order recommendation, and evidence timeline generation.

### Protocol Type

Protocol: SNMP  
System Type: PABX / Telephony  
Vendor/System: NEC PABX  
Integration Readiness: R1 evidence completed, committed, tagged, and pushed  
Runtime Decoder Status: Not started; R2 requires exact OID verification

### Existing Evidence Artifacts

- nec-pabx-r1/NEC_PABX_SNMP_EVIDENCE_R1.md
- nec-pabx-r1/nec-pabx-snmp-oid-mapping.v1.json
- nec-pabx-r1/nec-pabx-snmp-fixtures.v1.json
- nec-pabx-r1/nec-pabx-one-normalized-events.v1.json
- nec-pabx-r1/NEC_PABX_ONE_INTEGRATION_PLAN_R1.md
- nec-pabx-r1/NEC_PABX_SNMP_EVIDENCE_R1_SUMMARY.md

Commit: 948e71a docs(one): add nec pabx snmp evidence pack  
Tag: one-airport-nec-pabx-snmp-evidence-r1-freeze-20260630

### Confirmed OID Coverage

- Lamp Status and Lamp Clear
- Major Alarm Lamp
- Minor Alarm Lamp
- Supervisor Alarm Lamp
- Failure Message

### Group-Level Pending Coverage

- CPU
- Traffic
- Port
- Terminal
- System message
- Registration information

### Known Value Semantics

Major / Minor lamp:

- 0 = lamp off
- 1 = lamp lighting

Supervisor lamp:

- 0 = Not available
- 1 = Supervisor lamp off
- 2 = Supervisor lamp lighting

Failure Message:

- String up to 255 characters
- Sent as trap to SNMP Manager

### Pending Verification

- Exact child OIDs for CPU, traffic, port, terminal, sysMessage, and registrationInfo
- Trap payload structure
- Severity mapping
- Device/site/zone/asset identity mapping
- Polling versus trap behavior
- SNMP version and security requirements
- Whether failure messages should become alarms only or fault candidates

### Recommended Next Step

NEC R2 should only expand mapping after exact MIB/OID verification. NEC R3 should only create decoder or fixture validator logic after explicit approval.

## 6. Three-Profile Comparison

| Profile | System | Protocol Readiness | Main Value | Current Blocker | Decoder Readiness |
| --- | --- | --- | --- | --- | --- |
| DTS4160 | Clock / Time Sync | R1 evidence completed | Evidence timeline trust | Bit order and SNMP behavior confirmation | Controlled R2 fixture possible |
| BHE BRTL32 | Radio System | Vendor request pack completed | Radio communication availability | MIB/OID/trap/alarm mapping missing | Not ready |
| NEC PABX | Telephony / PABX | R1 evidence completed and pushed | Telephony service alarm visibility | Exact child OIDs and trap samples | R2 mapping expansion only after verification |

## 7. Development Control

Do not start broad decoder implementation until source mappings are verified.

Recommended order:

1. Send BHE vendor request email.
2. Prepare DTS4160 controlled R2 decoder fixture only if bit-order assumptions are explicitly marked.
3. Prepare NEC R2 mapping expansion only after exact child OIDs and trap samples are verified.
4. Align all three profiles with EDGE SNMP Connector and LINK normalized event contract after source data is verified.

## 8. Boundary Statement

This protocol-profile document is a derived integration document. It does not include raw customer files and does not represent live production validation.

VANTARIS ONE remains a cross-industry unified operations platform. The customer airport case is an industry projection and must not redefine the platform as airport-only.
