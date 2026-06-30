# NEC PABX ONE Integration Plan R1

## Purpose

This plan describes how derived NEC PABX SNMP evidence can map into VANTARIS ONE for the customer airport MMS projection. R1 is limited to documentation, JSON mappings, and synthetic examples. It does not create runtime decoder logic or claim live production integration.

## Why NEC PABX Matters In Airport MMS

PABX / telephony can support airport operations coordination, maintenance communication, incident response, and service desk escalation. Monitoring NEC PABX alarm lamps, failure messages, and later CPU/port/terminal status can help ONE surface communication-system risk in a structured operational flow.

## EDGE Responsibility

EDGE is responsible for SNMP connectivity once customer/vendor details are verified:

- SNMP version and credentials
- Polling endpoint and interval
- Trap receiver configuration
- Confirmed OID list and trap definitions
- Raw OID/value capture
- Communication-loss detection

## LINK Responsibility

LINK is responsible for normalization:

- Convert raw SNMP OID/value pairs into normalized event envelopes.
- Preserve raw OID, raw value, source endpoint, and decoder/mapping version.
- Map known lamp states into active/clear event status.
- Mark group-level candidates such as CPU and port status as pending until exact OIDs are verified.
- Avoid claiming service outage without confirmed event semantics and customer operational evidence.

## ONE Responsibility

ONE is responsible for presenting the normalized result in operational surfaces:

- Alarm Console
- Fault Operations
- Work Management / MMS
- Evidence Center
- Export reports
- HMI Map only when location data becomes available

## Alarm Console Behavior

The Alarm Console should display NEC PABX events with clear source evidence:

- Major Alarm Lamp active/clear
- Minor Alarm Lamp active/clear
- Supervisor Alarm Lamp not available/off/lighting
- Failure Message trap text
- Pending CPU/port/terminal candidates only after exact OIDs are confirmed

## Fault Operations Behavior

Fault Operations should correlate repeated NEC PABX alarm samples into candidate faults. Useful correlation signals include:

- Major/minor/supervisor lamp state
- Failure message text
- Communication-loss state
- Port or terminal status once exact OIDs are verified
- Customer telephony service indicators if available

## Work Management / MMS Behavior

Work Management / MMS should use NEC PABX events as recommendations, not automatic proof of outage. Recommended work order behavior should depend on:

- Severity mapping approved by customer
- Persistence and recurrence
- Failure message details
- Asset/location mapping
- Customer operational impact

## Evidence / Report Behavior

Evidence Center and export reports should include:

- Source system: NEC PABX
- Vendor: NEC
- Protocol: SNMP
- Raw OID
- Raw value
- Value interpretation
- Synthetic/live marker
- Mapping version
- Verification status
- Asset and location context when available

## HMI Map Relevance

HMI Map linkage is relevant only after customer asset and location data is available. Until then, NEC PABX events should retain `pending customer location mapping` rather than inventing site, room, panel, or zone context.

## R1 / R2 / R3 Roadmap

| Phase | Scope |
| --- | --- |
| R1 | Derived evidence pack only. Capture known OIDs, known semantics, synthetic fixtures, normalized examples, and verification gaps. |
| R2 | Expand OID mapping after exact MIB/OID verification, including CPU, traffic, port, terminal, sysMessage, registrationInfo, and trap payloads. |
| R3 | Optional decoder / SNMP fixture validator only after user approval and after verified MIB/OID/trap data is available. |
