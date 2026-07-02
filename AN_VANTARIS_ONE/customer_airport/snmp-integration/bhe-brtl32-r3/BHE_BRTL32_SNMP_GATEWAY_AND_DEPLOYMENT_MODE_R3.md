# BHE BRTL32 SNMP Gateway And Deployment Mode R3

## Purpose

This document records the integration-mode boundary for BHE BRTL32. It prevents the integration team from assuming direct Ethernet SNMP polling when the vendor package indicates bridge/gateway or framed-message operation may be required.

## Key Finding

BRTL32 SNMP is not treated as simple direct Ethernet SNMP in R3. The vendor materials indicate SNMP messages may use a custom protocol frame over RS-232 or built-in modem TCP. The package includes `SimpleSNMPSerialBridge.exe` as an example bridge from UDP 161 to serial.

## Candidate Mode 1: EDGE SNMP Manager Through Serial Bridge

```text
EDGE SNMP Manager
  -> UDP 161
  -> SimpleSNMPSerialBridge / equivalent gateway
  -> RS-232
  -> BRTL32
```

Validation required:

- Bridge host, IP, and UDP 161 binding.
- Serial port settings.
- BRTL32 serial framing behavior.
- SNMP GET behavior for `AlarmMom` and identity fields.
- Trap behavior through bridge, if supported.

## Candidate Mode 2: Built-In Modem TCP Packet-Switched Mode

```text
BRTL32 built-in modem packet-switched mode
  -> TCP client
  -> NMS/server
  -> framed SNMP/trap intake
```

Validation required:

- TCP connection owner and direction.
- NMS/server endpoint.
- Framed SNMP message format.
- Trap or alarm-change behavior.
- Heartbeat behavior.

## Candidate Mode 3: Customer/Vendor Gateway To EDGE Adapter

```text
Customer/vendor NMS or serial-over-IP gateway
  -> EDGE adapter intake
  -> LINK normalization
  -> ONE operational surfaces
```

Validation required:

- Gateway product/model and ownership.
- Whether gateway emits SNMP, TCP socket payloads, files, API, or another protocol.
- Mapping between BRTL32 serial number/identifier and customer asset.
- Operational support boundary for gateway failure.

## Do Not Assume Direct Polling

If no bridge/gateway/NMS mode is confirmed, EDGE must not assume it can directly SNMP poll a BRTL32 IP address.

## Evidence Fields To Capture During Site Validation

- Connection mode.
- Bridge/gateway model and version.
- SNMP version/security/community behavior.
- Source IP, destination IP, and UDP/TCP ports.
- Serial parameters if RS-232 is used.
- Normal GET sample.
- Active alarm GET sample.
- Trap sample.
- Clear sample.
- Gateway failure behavior.
- Unsupported OID behavior.
