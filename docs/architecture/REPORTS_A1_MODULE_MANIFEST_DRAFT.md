# REPORTS A1 Module Manifest Draft

## Reports Module Identity

- moduleId: `reports`
- moduleName/displayName: `Reports`
- fullName: `Reporting Workspace`
- chineseName: `报表工作台`
- moduleType: `platform-module`
- status: `draft-a1`

## Scope

Reports A1 defines docs-level reporting workspace boundary and manifest semantics.

## Non-scope

- no runtime/report engine implementation
- no API implementation
- no DB schema/table implementation
- no frontend page implementation
- no export runtime implementation
- no scheduled job runtime implementation
- no OpenAPI/JSON Schema/contracts schema implementation

## ownerScope

- reporting workspace context
- report catalog context
- scheduled/custom/drill-down/export reference contexts
- compliance/module-status/evidence-linked/operational report references

## forbiddenOwnership

- backend report engine
- frontend report page
- export runtime
- scheduled runtime
- API route
- DB table
- OpenAPI/JSON Schema/contracts schema
- EDGE/LINK/DB runtime
- auth/login/RBAC

## consumedReferences

- UCore operations reference
- UFMS fault/alarm/event reference
- UMMS maintenance reference
- UESG sustainability reference
- UCDE evidence reference
- UDOC operations reference
- UConsole module status reference
- audit/module metadata/governance status references

## providedDraftObjects

- reportsWorkspaceContext
- reportsCatalogContext
- reportsScheduleContext
- reportsExportContext
- reportsDrilldownContext
- reportsComplianceContext
- reportsEvidenceLinkedContext

## Dependency Model

- business modules: `ucore`, `ufms`, `umms`, `uesg`, `ucde`, `udoc`
- platform modules: `uconsole`, `analytics`, `nexus-ai`
- foundation references only: `AN_VANTARIS_Contracts`, `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, `AN_VANTARIS_DB`

## Impact Model

- api/db/menu/runtime/schema/frontend impact: `none-in-a1-draft`

## Next Task

`REPORTS-A2-API-DATA-MODEL-GATE`

## A1 Declaration

REPORTS-A1 is a module manifest draft only. It does not create runtime, API, DB schema, frontend page, report engine, export engine, scheduled job, OpenAPI, JSON Schema, or Contracts schema.
