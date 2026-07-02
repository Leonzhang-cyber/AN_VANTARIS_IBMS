# BHE BRTL32 SNMP Vendor Response R3

## Purpose

This R3 evidence pack records the BHE BRTL32 vendor response and converts it into derived SNMP integration evidence for VANTARIS ONE. It updates the previous R2 state where MIB, OID tree, trap definition, and alarm mapping were requested from the vendor/customer.

This is not a production decoder, not live SNMP validation, and not a runtime integration change.

## Vendor Package Inventory

The customer/vendor BHE BRTL32 Monitoring Resources 20260630 package is reported to include:

| Package Item |
| --- |
| `Documentation/BRTL32-LM-K11414-V01.pdf` |
| `Documentation/BRTL32_manual_RevB_20231113.pdf` |
| `Documentation/SnmpB MIB Browser Instructions.pdf` |
| `Example Server/SimpleSNMPSerialBridge.exe` |
| `Hash/C/main.c` |
| `Hash/C/simple_hash.c` |
| `Hash/C/simple_hash.h` |
| `Hash/C#/SimpleHash.cs` |
| `MIB/BRTL36.mib` |
| `readme.txt` |

Raw PDF, EXE, source package, ZIP, and MIB files are not committed in this repository. This R3 pack contains only derived documentation and JSON evidence.

## MIB Applicability

| Field | Vendor Response |
| --- | --- |
| Device | BRTL32 |
| MIB | `BRTL36.mib` |
| MIB family | BRTLxx / BRTMxx series / BRTS28 |
| Applicability note | Not all MIB parameters may be supported by BRTL32. |

The R3 mapping therefore treats MIB symbols as candidate mappings until site SNMP GET samples, trap samples, connection mode, SNMP security mode, and asset identity data are verified.

## Integration Mode Boundary

BRTL32 SNMP is not assumed to be simple direct Ethernet SNMP. The vendor package indicates SNMP messages may be carried through custom protocol frames over RS-232 or built-in modem TCP, with `SimpleSNMPSerialBridge.exe` provided as an example bridge from UDP 161 to serial.

Candidate integration modes:

1. EDGE SNMP Manager -> UDP 161 -> SimpleSNMPSerialBridge / equivalent gateway -> RS-232 -> BRTL32
2. BRTL32 built-in modem packet-switched mode -> TCP client -> NMS/server -> framed SNMP/trap intake
3. Customer/vendor NMS or serial-over-IP gateway -> EDGE adapter intake

Site validation must confirm which mode is actually used. Without a bridge or gateway, EDGE must not assume it can directly SNMP poll a BRTL32 IP address.

## AlarmMom Strategy

`AlarmMom` is the first-priority monitoring object family for BHE BRTL32 R3 because it gives a compact fault state that can drive ONE Alarm Console, Fault Operations, Work Management / MMS, Evidence, and Reports.

R3 defines controlled bit mappings for:

- `CenterAlarmMom`
- `SdrUlAlarmMom`
- `SdrDlAlarmMom`

Center and uplink mappings are explicit from the supplied task context. Downlink channel and band low-power bits are treated as vendor-MIB-derived candidates requiring live validation where exact formatting is unclear.

## Trap Object

`bheBRTL36Trap` is documented as a `NOTIFICATION-TYPE` candidate. R3 captures the included fields for derived mapping and site validation:

- `bheTrapDeviceStatus`
- `bheTrapIdentifier`
- `bheTrapMask`
- `bheTrapAlarmValue`
- `bheTrapMasterType`
- `bheBRTL36SerialNumber`
- `bheBRTL36Iden`
- `bheBRTL36SdrUlAlarmMom`
- `bheBRTL36SdrDlAlarmMom`
- `bheBRTL36SdrUlAlarmTrapMask`
- `bheBRTL36SdrDlAlarmTrapMask`
- `bheTrapExternalAlarms`
- `bheTrapComment`
- `bheTrapNumericId`

## Remaining Gates Before Production Decoder

- Confirm actual connection mode at site.
- Capture SNMP GET samples for normal and active `AlarmMom` values.
- Capture trap samples for active, heartbeat, and clear behavior.
- Confirm SNMP version, community/security mode, and rejection behavior.
- Confirm unsupported OID behavior for BRTL32 against `BRTL36.mib`.
- Map serial number and identifier to customer asset identity.
- Confirm severity policy and work order routing with customer operations.

## ONE Mapping

| ONE Layer | R3 Mapping |
| --- | --- |
| EDGE SNMP Connector / Adapter | Connects through confirmed bridge, modem TCP path, NMS, or serial-over-IP gateway. |
| LINK normalization | Converts `AlarmMom`, trap fields, RF/status metrics, and identity fields into normalized event envelopes. |
| ONE Alarm Console | Displays provisional radio system alarms with raw evidence. |
| Fault Operations | Correlates repeated radio alarms and RF degradation into fault candidates. |
| Work Management / MMS | Recommends maintenance review only after live validation and severity policy confirmation. |
| HMI Map | Requires confirmed serial/identifier to asset/location mapping. |
| Evidence / Reports | Stores raw MIB symbol, raw OID when confirmed, raw value, bridge mode, decoder contract version, and validation status. |
