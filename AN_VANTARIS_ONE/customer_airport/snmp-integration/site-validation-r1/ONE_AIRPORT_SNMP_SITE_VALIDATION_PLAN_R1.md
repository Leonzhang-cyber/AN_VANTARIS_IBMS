# ONE Airport SNMP Site Validation Plan R1

## Purpose

This plan consolidates site validation for the airport SNMP integration lines:

1. DTS4160 / Mobatime Clock System
2. BHE BRTL32 / Radio System
3. NEC PABX / Telephony System

It is a derived documentation and JSON planning pack only. It does not implement runtime decoders, does not modify EDGE / LINK / ONE runtime, and does not modify frontend, backend, API, schema, routes, or menu.

## Common Validation Chain

```text
Device / subsystem SNMP source
  -> network and security validation
  -> SNMP polling and/or trap sample capture
  -> raw OID / trap evidence
  -> controlled decode / interpretation
  -> LINK normalized event candidate
  -> ONE Alarm Console / Fault Operations
  -> Work Management / MMS recommendation
  -> Evidence / Reports export proof
```

## Validation Scope

| Scope Area | Required Outcome |
| --- | --- |
| Network readiness | Device or gateway reachability, source/destination IPs, ports, firewall, and routing confirmed. |
| SNMP security | SNMP version, community/SNMPv3 mode, access scope, rejection behavior, and credential handling confirmed. |
| Device identity | Serial number, identifier, IP/gateway identity, customer asset ID, site, zone, and location mapping confirmed. |
| OID validation | Normal, active, and clear polling samples captured for priority OIDs. |
| Trap validation | Active, clear, heartbeat, and failure-message trap payloads captured where supported. |
| Alarm lifecycle | Active and clear behavior confirmed for each system. |
| Gateway validation | Bridge, modem TCP, serial-over-IP, or vendor NMS relay behavior confirmed where applicable. |
| ONE mapping | Expected event key, severity, route, work order implication, and evidence fields confirmed. |

## DTS4160 / Mobatime Clock System

Known evidence:

- Device: DTS4160 grandmaster
- System: Clock System / Time Synchronization / Master Clock
- Alarm OID: `1.3.6.1.4.1.13842.4.4160.1.8`
- Active sample: `00408080.00000000`
- Clear sample: `00000000.00000000`
- Controlled decoded labels:
  - GNSS Sync Lost
  - No valid Time Source
  - No DTS Link

Site validation must confirm:

- Bit order.
- Byte order.
- Per-bit vendor mapping.
- Active / clear stability.
- Polling vs trap behavior.
- SNMP version and security.
- Device IP / network access.
- Asset / site / zone / location mapping.
- Communication loss handling.

## BHE BRTL32 / Radio System

Known evidence:

- Vendor resource package received.
- `BRTL36.mib` available.
- BRTL32 uses `BRTL36.mib`, but not all MIB parameters may be supported.
- AlarmMom is the first-priority monitoring strategy.
- `CenterAlarmMom`, `SdrUlAlarmMom`, and `SdrDlAlarmMom` mappings exist as controlled vendor-MIB-derived mappings.
- `bheBRTL36Trap` is available as `NOTIFICATION-TYPE`.
- SimpleSNMPSerialBridge / gateway mode evidence exists.
- Direct Ethernet SNMP polling must not be assumed.

Site validation must confirm:

- Actual access mode: direct SNMP, RS-232 bridge, serial-over-IP, built-in modem TCP, or vendor NMS relay.
- Who provides and supports the bridge or gateway.
- SNMP version and security.
- Actual SNMP GET samples for AlarmMom normal / active / clear.
- Actual trap samples.
- RF metric units and value format: forward power, reflected power, return loss, RSSI.
- Supported OID subset for BRTL32.
- Serial number / identifier / asset identity mapping.
- Gateway failure behavior.

## NEC PABX / Telephony System

Known evidence:

- Major Alarm Lamp.
- Minor Alarm Lamp.
- Supervisor Alarm Lamp.
- Failure Message.
- Lamp Status / Lamp Clear.
- Failure Message max 255 characters as trap to SNMP Manager.

Site validation must confirm:

- Exact child OIDs.
- Trap payload structure.
- Failure message examples.
- Severity mapping.
- CPU exact child OIDs.
- Traffic exact child OIDs.
- Port exact child OIDs.
- Terminal exact child OIDs.
- sysMessage exact child OIDs.
- registrationInfo exact child OIDs.
- Polling vs trap behavior.
- SNMP version and security.
- PABX asset / site / zone / location mapping.

## Site Session Sequence

1. Confirm system owners, vendor contacts, and maintenance/test windows.
2. Confirm network reachability and allowed source/destination paths.
3. Confirm SNMP version and security mode per system.
4. Capture identity samples before alarm samples.
5. Capture normal polling samples.
6. Trigger safe controlled active conditions where vendor/customer permits.
7. Capture active polling samples and trap payloads.
8. Capture clear samples and clear traps.
9. Test communication loss and gateway failure behavior.
10. Map each validated sample to expected ONE route and evidence fields.
11. Record remaining blockers before any production decoder or runtime integration task.

## Boundary Statement

This plan prepares validation only. It is not live validation, not production integration, and not a claim that any decoder is ready for runtime use.
