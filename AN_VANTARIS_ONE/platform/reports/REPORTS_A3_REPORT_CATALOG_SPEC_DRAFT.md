# REPORTS A3 Report Catalog Spec Draft Summary

## 1. Current Baseline Commit

- baseline commit: `284af37`

## 2. A3 Purpose

Define reports catalog candidate groups and first-batch report candidates in docs-level form only.

## 3. A2 Gate Reviewed

Reports A2 API/data model gate outputs are reviewed and used as the input baseline for A3 catalog drafting.

## 4. Catalog Groups

- Fault & Alarm Reports
- Maintenance Reports
- Energy & Sustainability Reports
- Evidence & Audit Reports
- Data Operations Reports
- Operations Summary Reports
- Module Status Reports
- Governance & Compliance Reports

## 5. First-batch Report Candidates

First-batch candidates include UFMS fault/alarm reports, UMMS maintenance reports, UESG sustainability reports, UCDE evidence/audit reports, UDOC operations reports, UCore summary reports, module status reports, and governance/compliance reports.

## 6. Metadata Summary

A3 defines metadata candidate groups for identity, grouping, source references, filters, aggregation, export, schedule, permission, audit, evidence linkage, and retention.

## 7. Blocked Work List

- report engine implementation
- backend API implementation
- frontend page implementation
- DB schema implementation
- OpenAPI/JSON Schema implementation
- export runtime and scheduled runtime implementation

## 8. No-runtime/No-api/No-db/No-frontend Declaration

This task is docs-only and does not implement runtime/API/DB/frontend/export/schedule behavior.

## 9. Next Recommended Task

`REPORTS-A4-REPORT-IMPLEMENTATION-GATE-PLAN`
