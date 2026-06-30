# DTS 4160 SNMP Alarm Decoder R1

## Device Context

| Field | Value |
| --- | --- |
| Device | DTS 4160 grandmaster |
| Vendor / Source Context | Mobatime / DTS |
| System | Clock System / Time Synchronization / Master Clock |
| Alarm OID | `1.3.6.1.4.1.13842.4.4160.1.8` |
| Raw active sample | `00408080.00000000` |
| Raw clear sample | `00000000.00000000` |

## Decoded Sample Alarms

The active sample is associated with the following decoded alarms:

| Decoded Alarm |
| --- |
| GNSS Sync Lost |
| No valid Time Source |
| No DTS Link |

The clear sample is associated with no active decoded alarms.

## 8-Byte / 64-Bit Alarm Mask Principle

The DTS 4160 alarm value is treated as an 8-byte / 64-bit alarm mask. Each asserted bit is expected to represent a specific alarm condition. The provided active sample `00408080.00000000` indicates a non-zero active alarm state, while `00000000.00000000` indicates a cleared state.

The exact bit order, byte ordering, and per-bit alarm labels must be verified against the vendor MIB and customer sample mapping before production decoder implementation. This R1 evidence pack therefore records only the decoded alarm labels confirmed by the supplied sample context and does not assign unsupported bit indexes.

## ONE Mapping

| ONE Layer | Mapping |
| --- | --- |
| EDGE SNMP Connector | Polls or receives trap data for OID `1.3.6.1.4.1.13842.4.4160.1.8`, subject to confirmed SNMP access mode. |
| LINK normalized event | Converts raw SNMP value into normalized alarm state, decoded alarms, source evidence, and device context. |
| Faults & Events | Creates event timeline entries and fault candidates for time synchronization degradation. |
| Assets & Locations | Links the grandmaster clock to confirmed site, building, room, rack, or equipment asset ID. |
| Work Management / MMS | Recommends investigation of time source, GNSS synchronization, and DTS link condition when active. |
| HMI Map | Displays Clock System / Master Clock alarm state at the confirmed airport location. |
| Evidence / Reports | Stores raw OID, raw value, decoder version, and source document reference for audit and report export. |

## Assumptions And Confirmation Items

| Item | Status |
| --- | --- |
| Exact bit order must be verified against MIB/customer sample. | customerToConfirm |
| Optical vs LAN naming for DTS link requires customer confirmation. | customerToConfirm |
| SNMP version and polling/trap approach require confirmation. | customerToConfirm |
| Site/location/asset ID must be confirmed. | customerToConfirm |
| Full MIB and alarm definition remain required for complete decoder coverage. | vendorToProvide |
