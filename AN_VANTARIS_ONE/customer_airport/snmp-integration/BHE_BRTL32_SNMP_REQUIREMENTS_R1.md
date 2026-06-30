# BHE BRTL32 SNMP Requirements R1

## Purpose

This document defines the formal request checklist required to integrate the BHE BRTL32 Radio System into ONE through SNMP. The current customer integration context indicates SNMP is required, but full SNMP integration details are not yet available.

No BHE OIDs, alarm codes, traps, or MIB details are invented in this R1 evidence pack.

## Device / System Context

| Field | Value |
| --- | --- |
| System | Radio System |
| Vendor | BHE |
| Device | BRTL32 |
| Integration protocol | SNMP, pending vendor/customer details |
| Additional requirement | RS232-to-TCP/IP converter required |

## Why Additional SNMP Information Is Required

ONE cannot reliably normalize BHE BRTL32 radio alarms, RF operating conditions, clear behavior, or work-management recommendations until the vendor/customer provides the authoritative SNMP implementation details.

The missing information affects:

| Area | Impact |
| --- | --- |
| SNMP version support | Determines security mode, credential handling, and connector configuration. |
| MIB and OID list | Determines which values can be polled or decoded. |
| Trap definition | Determines event-driven alarm ingestion behavior. |
| Alarm mapping | Determines alarm labels, severity, acknowledgement, and clear behavior. |
| RF parameters | Determines operational visibility for input RSSI, output power, and radio health. |
| RS232-to-TCP/IP converter | Determines whether SNMP is native to the device or exposed through a conversion layer. |

## Formal Request Checklist For BHE

| Section | Required Information |
| --- | --- |
| Device identity | Exact model, firmware version, serial number format, supported interface options, and device role. |
| SNMP version support | Supported SNMP versions, SNMPv2c community requirements, SNMPv3 authentication/privacy requirements, and access control rules. |
| SNMP communication details | IP addressing model, UDP ports, polling support, trap destination configuration, timeout/retry guidance, and network firewall requirements. |
| MIB/OID/trap definition | MIB file, full OID list, scalar/table structure, trap definitions, trap payload examples, and data types/units. |
| RF operational parameters | Available OIDs or traps for RF parameters, input RSSI, output power, channel/frequency, link status, and device health. |
| Alarm mapping | Alarm names, alarm codes, OID/trap source, severity, active condition, clear condition, debounce behavior, and maintenance states. |
| Acknowledgement/clear behavior | Whether alarms auto-clear, require acknowledgement, expose acknowledgement status through SNMP, or require operator action. |
| Integration testing samples | Active alarm sample, clear sample, nominal RF sample, degraded RF sample, trap samples, and polling response examples. |

## ONE Mapping

| ONE Layer | Mapping |
| --- | --- |
| EDGE SNMP Connector | Connects to BHE BRTL32 or converter-exposed SNMP endpoint after communication details are confirmed. |
| LINK normalization | Converts BHE OIDs/traps into normalized radio alarms, RF metrics, source evidence, and asset context. |
| Alarm Console | Presents active and cleared radio system alarms with raw SNMP evidence. |
| Fault Operations | Converts radio alarm sequences into fault candidates and event timelines. |
| Work Management | Supports MMS work order recommendations for radio link, RF, and device health issues. |
| HMI Map | Displays radio system state at confirmed airport asset/location mapping. |
| Evidence / Reports | Stores raw OID/trap data, decoder version, vendor references, and reportable integration evidence. |

## Open Questions For BHE / Customer

| Question | Owner |
| --- | --- |
| What RS232-to-TCP/IP converter model will be used? | customerToConfirm |
| Does the converter expose SNMP directly, or does it only transport serial data over TCP/IP? | vendorToProvide |
| Does BRTL32 support polling, traps, or both after conversion? | vendorToProvide |
| Which SNMP security mode is supported and required for site deployment? | vendorToProvide |
| What are the alarm clear semantics for each radio alarm? | vendorToProvide |
| What is the exact asset and location mapping for each BHE device? | customerToConfirm |
