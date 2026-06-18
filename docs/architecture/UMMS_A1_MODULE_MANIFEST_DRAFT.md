# UMMS A1 Module Manifest Draft

## 1. Module Identity

- moduleId: umms
- moduleName: UMMS
- fullName: Unified Maintenance Management System
- chineseName: 全向维护管理系统
- status: draft-a1
- runtimeReady: false

## 2. Scope

UMMS A1 defines maintenance context references including work order, preventive/corrective maintenance, SLA/assignment/escalation references, and cross-module linkages.

## 3. Non-scope

- Edge/Link runtime ownership
- DB/Contracts schema ownership
- backend/frontend runtime implementation
- real work order engine and technician scheduling implementation in A1

## 4. OwnerScope

UMMS owner scope includes maintenance context references, asset/location linkage references, energy linkage references, evidence linkage references, and readiness context.

## 5. ForbiddenOwnership

UMMS must not own Edge runtime, Link runtime, DB schema, Contracts schema, backend runtime, frontend runtime, or credential/secret/token material.

## 6. ConsumedObjects

UMMS consumes maintenance, work order, assignment, asset, fault, and cross-module linkage references through approved boundaries.

## 7. ProvidedObjects

UMMS provides maintenance, work-order, SLA/escalation, technician, and readiness context objects.

## 8. Dependency Model

UMMS depends on one-adapter, ucore, uesg, udoc, ucde, uconsole, reports, analytics, and foundation references as reference-only dependencies.

## 9. Impact Model

- apiImpact: none-in-a1-draft
- dbImpact: none-in-a1-draft
- menuImpact: none-in-a1-draft
- runtimeImpact: none-in-a1-draft
- schemaImpact: none-in-a1-draft

## 10. Next Task

UCORE-A1-MODULE-MANIFEST-DRAFT

UMMS-A1 is a module manifest draft only. It does not create runtime, API, DB schema, frontend page, Edge connector, Link connector, or Contracts schema.
