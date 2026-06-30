# BHE BRTL32 SNMP Request Email R2

Subject: BHE BRTL32 SNMP Integration Information Request for VANTARIS MMS

Dear BHE / Customer Team,

We are preparing the VANTARIS MMS integration for the airport Radio System and need the SNMP information for the BHE BRTL32 equipment.

Could you please provide the technical materials required for monitoring and alarm integration:

- Official MIB file for the applicable BRTL32 hardware and firmware version
- Full OID list, including object names, data types, units, scale/multiplier, normal values, alarm values, and clear values
- Trap definitions, including trap OIDs, varbind format, severity fields, and active/clear behavior
- Complete alarm mapping, including alarm names, alarm codes, severities, active/clear values, latching behavior, and recommended actions
- SNMP version and security details, including whether SNMP v1, v2c, or v3 is supported and the preferred read-only monitoring mode
- RF parameter mapping for input RSSI, output power, forward/reflected power, VSWR if available, RX/TX status, PA status, channel/frequency, temperature, power supply, and module health
- Sample SNMP responses and traps for normal, active alarm, cleared alarm, RSSI, and output power values
- Test procedure for generating sample alarms and verifying clear behavior

The MMS schedule notes that an RS232-to-TCP/IP converter is required. Please also confirm whether the BRTL32 supports SNMP natively, whether SNMP is exposed through the converter/gateway, or whether the converter provides TCP socket or serial-over-IP access only. If there is a vendor-recommended converter model, please include the model and setup guidance.

Read-only SNMP is sufficient for monitoring unless alarm acknowledgement is supported through SNMP. If acknowledgement is supported, please provide the relevant command OIDs, access requirements, and expected behavior.

## Requested Attachments / Inputs

1. BRTL32 MIB file
2. Full OID list
3. Trap definition document
4. Alarm mapping table
5. SNMP version/security configuration guide
6. RS232-to-TCP/IP converter specification and configuration guide
7. Sample `snmpwalk` output for normal condition
8. Active alarm and clear alarm polling samples
9. Active trap and clear trap packet samples
10. RF telemetry samples for RSSI and output power
11. Test alarm procedure and expected restart/communication-loss behavior

Thank you. These materials will allow the VANTARIS ONE integration team to configure the EDGE SNMP connector, normalize events into the ONE Alarm Console, support Fault Operations and Work Management / MMS, and preserve evidence for reports.

Best regards,

VANTARIS ONE Integration Team
