# BHE BRTL32 SNMP MIB Analysis R3

## Scope

This document summarizes derived BHE BRTL32 MIB evidence from the vendor response. It does not include or reproduce the raw `BRTL36.mib` file.

## Applicability

The vendor package readme states:

| Item | Value |
| --- | --- |
| Device | BRTL32 |
| MIB | `BRTL36.mib` |
| MIB family | BRTLxx / BRTMxx series / BRTS28 |
| Support boundary | Not all MIB parameters may be supported by BRTL32. |

## Priority Monitoring Objects

R3 prioritizes these MIB object families:

| Object / Symbol | Purpose | R3 Status |
| --- | --- | --- |
| `CenterAlarmMom` | Center/system alarm bitmap. | Primary controlled mapping. |
| `SdrUlAlarmMom` | Uplink SDR alarm bitmap. | Primary controlled mapping. |
| `SdrDlAlarmMom` | Downlink SDR alarm bitmap. | Candidate mapping, exact bit formatting requires live validation. |
| `bheBRTL36SerialNumber` | Device serial identity. | Candidate asset identity field. |
| `bheBRTL36Iden` | Device identifier. | Candidate asset identity field. |
| Forward power | RF telemetry. | Candidate metric. |
| Reflected power | RF telemetry. | Candidate metric. |
| Return loss | RF telemetry. | Candidate metric. |
| RSSI | RF telemetry. | Candidate metric. |
| Power manager status | Device/power health. | Candidate status metric. |
| Trap masks | Trap routing / alarm mask evidence. | Candidate trap evidence. |
| Dry contact masks | External alarm evidence. | Candidate external alarm mapping. |

## CenterAlarmMom Controlled Bit Mapping

| Bit | Alarm |
| --- | --- |
| BIT0 | External Alarm 1 |
| BIT1 | External Alarm 2 |
| BIT2 | External Alarm 3 |
| BIT3 | External Alarm 4 |
| BIT4 | Tamper |
| BIT5 | Supply Voltage A |
| BIT6 | Center Supply Current |
| BIT7 | Fan Error |
| BIT8 | Modem |
| BIT9 | Downlink Low Power |
| BIT10 | Uplink Supply Voltage |
| BIT11 | Downlink Supply Voltage |
| BIT12 | Uplink SAW Current |
| BIT13 | Downlink SAW Current |
| BIT14 | Uplink PAM Current |
| BIT15 | Downlink PAM Current |
| BIT16 | Uplink Overdrive over 30 min |
| BIT17 | Downlink Overdrive over 30 min |
| BIT18 | Reserved always 0 |
| BIT19 | Downlink Overpower |
| BIT20 | Uplink VSWR |
| BIT21 | Downlink VSWR |
| BIT22 | Uplink Temperature |
| BIT23 | Downlink Temperature |
| BIT24 | Uplink Synthesizer Unlocked |
| BIT25 | Downlink Synthesizer Unlocked |
| BIT26 | Uplink Overdrive Level |
| BIT27 | Downlink Overdrive Level |
| BIT28 | Low Battery Voltage |
| BIT29 | Low Main Supply Voltage |
| BIT30 | Reserved |
| BIT31 | Supply Voltage B |

## SdrUlAlarmMom Controlled Bit Mapping

| Bit | Alarm |
| --- | --- |
| BIT0 | Current |
| BIT1 | Temperature |
| BIT2 | Overdrive |
| BIT3 | FPGA Error |
| BIT4-BIT12 | Reserved |

## SdrDlAlarmMom Mapping Boundary

The downlink SDR alarm mom includes channel low-power bits and band low-power bits according to `BRTL36.mib`. Because the exact bit formatting is not present in the task prompt and the raw MIB is not committed, R3 marks downlink channel/band mapping as vendor-MIB-derived and requiring live validation.

## Trap Analysis

`bheBRTL36Trap` should be validated for active alarm, clear alarm, heartbeat, trap mask, external alarm, and numeric alarm identifier behavior. The expected included fields are documented in `bhe-brtl32-decoder-contract.v2.json`.

## Production Caveat

MIB availability reduces the R2 blocker, but it does not complete production validation. BRTL32 support for individual `BRTL36.mib` objects must be proven with site SNMP GET and trap samples.
