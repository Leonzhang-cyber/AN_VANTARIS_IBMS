# ONE Airport SNMP Test Data Capture Template R1

Use this template for each site validation sample. Do not replace raw evidence with interpreted labels; capture both.

| Field | Value |
| --- | --- |
| Test ID |  |
| System | DTS4160 / BHE BRTL32 / NEC PABX |
| Device |  |
| Site / Zone / Location |  |
| Connection Mode | Direct SNMP / RS-232 bridge / serial-over-IP / built-in modem TCP / vendor NMS relay |
| SNMP Version | v1 / v2c / v3 / not confirmed |
| OID / Trap Name |  |
| Normal Sample |  |
| Active Sample |  |
| Clear Sample |  |
| Raw Value |  |
| Decoded Meaning |  |
| Expected ONE Event |  |
| Expected Severity |  |
| Expected Route | ONE Alarm Console / Fault Operations / Work Management / MMS / Evidence / Reports |
| Evidence Required | Screenshot / snmpget output / snmpwalk output / trap capture / bridge log / packet capture |
| Pass / Fail |  |
| Remarks |  |

## Evidence Capture Rules

- Record timestamp and timezone.
- Record source IP, destination IP, port, and gateway/bridge path where applicable.
- Redact credentials and communities before committing derived evidence.
- Preserve raw OID, raw trap name, raw value, and decoded meaning.
- Mark synthetic values clearly if any non-live sample is used for planning.
- Do not claim production validation until customer/vendor sign-off is complete.

## Recommended Sample Set Per System

| System | Minimum Samples |
| --- | --- |
| DTS4160 | Normal polling, active polling, clear polling, communication loss, bit/byte order evidence. |
| BHE BRTL32 | Gateway availability, AlarmMom normal/active/clear, trap payload, RF metric polling, unsupported OID, gateway failure. |
| NEC PABX | Major/minor/supervisor polling, Failure Message trap, clear validation, exact child OID discovery, severity mapping. |
