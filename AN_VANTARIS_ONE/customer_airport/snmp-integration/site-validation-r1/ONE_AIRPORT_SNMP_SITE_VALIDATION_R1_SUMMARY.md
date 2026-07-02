# ONE Airport SNMP Site Validation R1 Summary

## Files Created

| File | Purpose |
| --- | --- |
| `ONE_AIRPORT_SNMP_SITE_VALIDATION_PLAN_R1.md` | Unified site validation plan for DTS4160, BHE BRTL32, and NEC PABX. |
| `ONE_AIRPORT_SNMP_CUSTOMER_QUESTION_LIST_R1.md` | Grouped customer/vendor/integration-team questions. |
| `ONE_AIRPORT_SNMP_VENDOR_DATA_REQUEST_MATRIX_R1.md` | Vendor data request matrix with blocking levels and owners. |
| `ONE_AIRPORT_SNMP_TEST_DATA_CAPTURE_TEMPLATE_R1.md` | Field template for polling/trap sample capture. |
| `one-airport-snmp-site-validation-checklist.v1.json` | Structured checklist for readiness, validation, mapping, and evidence capture. |
| `one-airport-snmp-customer-question-matrix.v1.json` | Structured customer/vendor question matrix. |
| `one-airport-snmp-test-cases.v1.json` | Unified test case matrix for DTS, BHE, and NEC. |
| `ONE_AIRPORT_SNMP_SITE_VALIDATION_R1_SUMMARY.md` | This summary. |

## Scope

This package unifies site validation planning across existing DTS4160 R2, BHE BRTL32 R3, NEC PABX R1, and SNMP Protocol Profiles R1 evidence. It is documentation and JSON only.

## Boundary

This package does not:

- Modify backend, frontend, API contracts, database schema, routes, or menu.
- Modify EDGE, LINK, or ONE runtime.
- Modify previous SNMP R1/R2/R3 files.
- Add raw customer ZIP, PDF, MIB, EXE, DOCX, XLSX, or other raw artifacts.
- Claim production decoder readiness or live validation completion.

## Systems Covered

| System | Validation Focus |
| --- | --- |
| DTS4160 / Mobatime Clock System | Alarm OID samples, bit/byte order, per-bit vendor mapping, polling/trap behavior, SNMP security, asset mapping. |
| BHE BRTL32 / Radio System | Gateway/access mode, AlarmMom normal/active/clear, trap payloads, RF metric units, supported OID subset, asset identity, gateway failure. |
| NEC PABX / Telephony System | Major/minor/supervisor lamp polling, Failure Message trap, exact child OIDs, severity mapping, polling/trap behavior, asset mapping. |

## Recommended Next Step

Use this R1 plan in a customer/vendor site validation workshop. Do not start production decoder or runtime integration work until the required samples, mappings, security details, and asset/location evidence are captured and signed off.
