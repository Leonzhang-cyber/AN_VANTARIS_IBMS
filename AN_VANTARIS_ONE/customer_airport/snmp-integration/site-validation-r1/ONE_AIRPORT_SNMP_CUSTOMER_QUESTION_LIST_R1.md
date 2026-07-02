# ONE Airport SNMP Customer Question List R1

## Purpose

This question list groups the open questions required before DTS4160, BHE BRTL32, and NEC PABX SNMP validation can be completed at site.

## 1. Customer Project / IT / OT Network Team

| Question | Applies To | Why It Matters |
| --- | --- | --- |
| What are the device or gateway IP addresses, VLANs, and routing paths? | DTS, BHE, NEC | Required for SNMP polling/trap intake. |
| Which ONE / EDGE source IPs are allowed to poll or receive traps? | DTS, BHE, NEC | Required for firewall and allow-listing. |
| Which SNMP versions and security modes are approved at site? | DTS, BHE, NEC | Required for security configuration. |
| Are SNMPv2c communities or SNMPv3 credentials managed by customer IT/OT? | DTS, BHE, NEC | Required for credential ownership and handling. |
| What are the maintenance windows for active alarm testing? | DTS, BHE, NEC | Required to avoid operational disruption. |
| What are the customer asset IDs, site, zone, room, rack, and panel locations? | DTS, BHE, NEC | Required for ONE asset/location mapping. |
| Who signs off severity and work order routing policy? | DTS, BHE, NEC | Required before ONE operational recommendations. |

## 2. DTS / Mobatime Vendor

| Question | Why It Matters |
| --- | --- |
| What is the exact bit order and byte order for OID `1.3.6.1.4.1.13842.4.4160.1.8`? | Required for production decoder correctness. |
| Provide the full per-bit DTS4160 alarm mapping. | Required to decode beyond sample-confirmed labels. |
| Are alarm changes available by polling, trap, or both? | Required for EDGE connector mode. |
| What SNMP versions are supported? | Required for site security design. |
| Does `No DTS Link` map to optical, LAN, or another link name at this site? | Required for customer-facing label accuracy. |
| What is the recommended test procedure for active and clear alarm samples? | Required for safe site validation. |

## 3. BHE Vendor

| Question | Why It Matters |
| --- | --- |
| Which BRTL32 access mode will be used: direct SNMP, RS-232 bridge, serial-over-IP, built-in modem TCP, or vendor NMS relay? | Direct Ethernet SNMP must not be assumed. |
| Who provides and supports the bridge/gateway? | Required for ownership and failure handling. |
| Which `BRTL36.mib` objects are supported by BRTL32? | Not all MIB parameters may be supported. |
| Provide numeric OIDs for AlarmMom, RF metrics, serial number, identifier, trap masks, and dry contact masks. | Required for polling and decoder configuration. |
| Provide active, clear, and heartbeat trap samples for `bheBRTL36Trap`. | Required for trap normalization. |
| What are RF metric units and scaling for forward power, reflected power, return loss, and RSSI? | Required for correct display and thresholds. |
| What is the gateway failure behavior? | Required to distinguish radio alarm from bridge failure. |

## 4. NEC Vendor

| Question | Why It Matters |
| --- | --- |
| Provide exact child OIDs for CPU, traffic, port, terminal, sysMessage, and registrationInfo. | R1 has only group-level coverage for these areas. |
| Provide trap payload structure for Failure Message and system messages. | Required for trap parsing and evidence. |
| Provide example failure message strings and severity mapping. | Required for ONE Alarm Console and Fault Operations. |
| Confirm polling vs trap behavior for major/minor/supervisor alarms. | Required for lifecycle handling. |
| Confirm SNMP version and security modes. | Required for site security configuration. |
| Confirm active, clear, and latching behavior for alarm lamps. | Required for lifecycle validation. |

## 5. Vector / Integration Partner, If Applicable

| Question | Applies To | Why It Matters |
| --- | --- | --- |
| Will Vector provide any SNMP bridge, relay, NMS, or serial-over-IP gateway? | BHE, possibly others | Required for integration ownership. |
| Who captures packet evidence and test logs? | DTS, BHE, NEC | Required for evidence traceability. |
| Who maintains OID-to-asset mapping workbook or register? | DTS, BHE, NEC | Required for ONE asset binding. |
| What format will validation evidence be handed over in? | DTS, BHE, NEC | Required for Evidence / Reports ingestion. |

## 6. ONE / EDGE / LINK Implementation Team

| Question | Applies To | Why It Matters |
| --- | --- | --- |
| Which EDGE connector mode is planned for each system? | DTS, BHE, NEC | Required before runtime implementation. |
| What normalized event envelope fields are mandatory for site acceptance? | DTS, BHE, NEC | Required for LINK / ONE consistency. |
| What severity policy will be provisional vs customer-approved? | DTS, BHE, NEC | Prevents overclaiming. |
| How will communication loss be represented separately from equipment alarms? | DTS, BHE, NEC | Avoids false equipment fault candidates. |
| What evidence fields are required for export reports? | DTS, BHE, NEC | Required for customer handover. |
