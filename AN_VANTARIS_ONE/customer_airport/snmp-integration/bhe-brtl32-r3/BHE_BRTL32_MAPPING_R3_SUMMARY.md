# BHE BRTL32 Mapping R3 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `BHE_BRTL32_SNMP_VENDOR_RESPONSE_R3.md` | Vendor response evidence boundary, package inventory, integration modes, and ONE mapping. |
| `BHE_BRTL32_SNMP_MIB_ANALYSIS_R3.md` | Derived `BRTL36.mib` applicability and priority object analysis. |
| `BHE_BRTL32_SNMP_GATEWAY_AND_DEPLOYMENT_MODE_R3.md` | Bridge/gateway/deployment mode analysis and direct polling guardrail. |
| `bhe-brtl32-snmp-oid-candidates.v2.json` | Candidate MIB symbols and OID placeholders for later MIB extraction/live validation. |
| `bhe-brtl32-alarmmom-bit-mapping.v2.json` | Controlled AlarmMom bit mapping for Center, uplink SDR, and downlink SDR boundary. |
| `bhe-brtl32-decoder-contract.v2.json` | Controlled decoder contract without runtime implementation. |
| `bhe-brtl32-expected-normalized-events.v2.json` | Provisional normalized event examples for ONE routing. |
| `bhe-brtl32-site-validation-test-plan.v2.json` | Site validation plan for polling, traps, bridge failure, security rejection, unsupported OID, RF metrics, and asset identity. |
| `BHE_BRTL32_MAPPING_R3_SUMMARY.md` | Summary of R3 scope, outputs, knowns, and pending gates. |

## What Changed From R2

R2 requested missing vendor evidence. R3 records that the vendor/customer package now provides `BRTL36.mib`, BRTL32 documentation, SnmpB instructions, bridge example, hash sample code, and readme guidance. The MIB/OID/trap/alarm mapping blocker is partially reduced, but production decoder readiness is still gated by site validation.

## Key Confirmed Vendor Response Items

- Device: BRTL32.
- MIB: `BRTL36.mib`.
- MIB family: BRTLxx / BRTMxx series / BRTS28.
- Not all MIB parameters may be supported by BRTL32.
- SNMP may require custom protocol framing over RS-232 or built-in modem TCP.
- `SimpleSNMPSerialBridge.exe` is an example bridge from UDP 161 to serial.

## Critical Guardrails

- This is not a production decoder.
- This is not live SNMP validation.
- This does not connect to a real BRTL32 device.
- This does not modify EDGE, LINK, ONE runtime, frontend, backend, API, schema, routes, or menu.
- Numeric OIDs are not invented where the raw MIB tree is not committed.
- Raw vendor PDF, ZIP, EXE, source package, or MIB files are not committed.

## Recommended Next Step

Run the R3 site validation plan with vendor/customer support. After live SNMP GET samples, trap samples, actual connection mode, SNMP version/security, and asset identity mapping are verified, create a production-candidate R4 decoder specification or implementation task only with explicit user approval.
