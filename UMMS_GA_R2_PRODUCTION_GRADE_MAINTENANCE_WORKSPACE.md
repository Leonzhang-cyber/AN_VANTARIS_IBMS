# UMMS GA R2 Production-grade Maintenance Workspace

Task: UMMS-GA-R2
PASS marker: `UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE_PASS`

UMMS is the Unified Maintenance Management System and is the VANTARIS ONE Work Management / Maintenance capability. VANTARIS ONE is cross-industry and not airport-only.

R2 freezes production-grade customer demo readiness for a read-only UMMS workspace. R2 is not POC. R2 is not mock. R2 is not temporary demo. It presents a complete product module surface for customer review while preserving non-execution boundaries.

The workspace uses `VANTARIS_LIGHT_OPERATIONS_CONSOLE`: light app shell, white/off-white rounded cards, soft status badges, teal / mint accent, compact tables, and page-internal pill tabs.

R2 covers:
- Maintenance Overview
- Work Order Management
- Maintenance Task Board
- Preventive Maintenance Plan
- Corrective Maintenance Flow
- Engineer Dispatch
- Asset Maintenance Context
- Event / Fault Context
- UCDE Evidence Linkage
- UHMI Linkage
- Reports Linkage
- Customer Acceptance View
- Role-based Views
- Guardrails

R2 does not do real work order write. R2 does not do DB write. R2 does not do runtime activation. R2 does not do device control. R2 does not do EDGE/LINK command. R2 does not do production activation.

Server planning is recorded only:
- `192.168.60.21`: future APP/non-DB target
- `192.168.60.22`: future DB-only target

Future controlled action path is recorded and NOT EXECUTED in R2:
`UMMS / UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`
