# NEC PABX SNMP Evidence R1

## Scope

This R1 pack captures derived NEC PABX SNMP evidence for the customer airport MMS schedule. It is documentation and JSON evidence only. It does not create runtime decoder logic, claim live production integration, or include raw customer PDF, ZIP, Excel, or MIB files.

## Source Material Boundary

The source context used for this pack is limited to the customer airport MMS schedule and NEC S-148 SNMP material summarized in the task brief. The schedule lists `PABX / NEC - SNMP, information being collected`. NEC S-148 material indicates standard MIB-2 groups and NEC private MIB structure.

This pack is a customer_airport industry projection for VANTARIS ONE, not a change to ONE as a general product.

## Customer Airport MMS Schedule Alignment

NEC PABX appears in the airport MMS integration scope as an SNMP-based system with information still being collected. R1 therefore establishes the evidence boundary, known OID baseline, expected event semantics, and pending verification items required before implementation.

## NEC PABX SNMP Relevance

PABX monitoring matters because telephony availability can affect airport communication, operations coordination, maintenance escalation, and incident response. SNMP evidence can support alarm visibility, fault candidates, work order recommendations, and audit/report exports once exact site configuration and MIB/OID details are verified.

## Standard MIB-2 Groups

The NEC S-148 SNMP material indicates support for these standard MIB-2 groups:

| Group |
| --- |
| system |
| interface |
| ip |
| icmp |
| tcp |
| udp |
| snmp |

## NEC Private MIB Structure

The NEC private MIB structure is identified as:

```text
pbx(76).ipx(2)
```

Key groups:

| Group | Index |
| --- | --- |
| alarm | 1 |
| systemMessage | 2 |
| cpu | 3 |
| traffic | 4 |
| port | 5 |
| terminal | 6 |
| sysMessage | 7 |
| registrationInfo | 12 |

## R1 High-Value OID Coverage

| Monitoring Point | OID / Coverage | R1 Status |
| --- | --- | --- |
| Alarm Lamp Status / Lamp Clear | `1.3.6.1.4.1.119.2.3.76.2.1.1.0` | Confirmed exact OID |
| Major Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.2.0` | Confirmed exact OID |
| Minor Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.3.0` | Confirmed exact OID |
| Supervisor Alarm Lamp | `1.3.6.1.4.1.119.2.3.76.2.1.4.0` | Confirmed exact OID |
| Failure Message | `1.3.6.1.4.1.119.2.3.76.2.2.1.0` | Confirmed exact OID |
| System Message Trap | NEC private MIB system/sys message groups | Pending exact trap definition |
| CPU Usage | NEC private MIB cpu group | Pending exact child OID confirmation |
| Circuit Card / Port Status | NEC private MIB port group | Pending exact child OID confirmation |
| Terminal / Registration Info | NEC private MIB terminal and registrationInfo groups | Pending exact child OID confirmation |

## Alarm Lamp Semantics

Known value semantics:

| Point | Value | Meaning |
| --- | --- | --- |
| Major Alarm Lamp | 0 | lamp off |
| Major Alarm Lamp | 1 | lamp lighting |
| Minor Alarm Lamp | 0 | lamp off |
| Minor Alarm Lamp | 1 | lamp lighting |
| Supervisor Alarm Lamp | 0 | Not available |
| Supervisor Alarm Lamp | 1 | Supervisor lamp off |
| Supervisor Alarm Lamp | 2 | Supervisor lamp lighting |

## Failure Message Semantics

Failure Message is a string up to 255 characters and is sent as a trap to the SNMP Manager. The exact trap payload, severity derivation, and active/clear relationship require verification against customer/vendor material before production use.

## What Is Confirmed

- Customer airport MMS schedule includes `PABX / NEC - SNMP, information being collected`.
- NEC S-148 material indicates standard MIB-2 groups: system, interface, ip, icmp, tcp, udp, snmp.
- NEC private MIB structure includes `pbx(76).ipx(2)`.
- Alarm group baseline is `1.3.6.1.4.1.119.2.3.76.2.1`.
- Exact OIDs are known for lamp clear/status, major alarm lamp, minor alarm lamp, supervisor alarm lamp, and failure message.
- Major/minor/supervisor lamp value semantics are known at R1 level.

## What Remains To Verify

- Exact MIB/OID table for CPU, traffic, port, terminal, sysMessage, and registrationInfo child objects.
- Exact system message trap and failure message trap payload format.
- NEC PABX model, firmware, SNMP version, community/SNMPv3 support, polling interval, and trap configuration.
- Site asset IDs, location mapping, zone context, and HMI map coordinates.
- Alarm severity mapping, active/clear transitions, latching behavior, and work order thresholds.

## VANTARIS ONE Integration Chain

```text
EDGE SNMP Connector
  -> LINK normalized event
  -> ONE Alarm Console
  -> Fault Candidate
  -> Work Order recommendation
  -> Evidence Center
  -> Export report
```

The R1 pack prepares the evidence model for this chain. It does not claim live NEC PABX production integration.
