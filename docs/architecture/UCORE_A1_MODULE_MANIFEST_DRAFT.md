# UCORE A1 Module Manifest Draft

## 1. Module Identity

- moduleId: ucore
- moduleName: UCore
- fullName: Unified Core Operations
- chineseName: 全向核心运营
- status: draft-a1
- runtimeReady: false

## 2. Scope

UCore A1 defines core operation coordination references for site/asset/event/alarm, command-center references, readiness references, and cross-module orchestration references.

## 3. Non-scope

- Edge/Link runtime ownership
- DB/Contracts schema ownership
- backend/frontend runtime implementation
- command center runtime implementation and auth/login/RBAC runtime in A1

## 4. OwnerScope

UCore owner scope includes operation coordination references, module orchestration references, adapter boundary references, and readiness context.

## 5. ForbiddenOwnership

UCore must not own Edge runtime, Link runtime, DB schema, Contracts schema, backend runtime, frontend runtime, or credential/secret/token material.

## 6. ConsumedObjects

UCore consumes operational references, readiness references, and cross-module linkage references through approved boundaries.

## 7. ProvidedObjects

UCore provides operation coordination, orchestration, status snapshot, and readiness context objects.

## 8. Dependency Model

UCore depends on one-adapter, umms, uesg, udoc, ucde, uconsole, reports, analytics, and foundation references as reference-only dependencies.

## 9. Impact Model

- apiImpact: none-in-a1-draft
- dbImpact: none-in-a1-draft
- menuImpact: none-in-a1-draft
- runtimeImpact: none-in-a1-draft
- schemaImpact: none-in-a1-draft

## 10. Next Task

ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT

UCORE-A1 is a module manifest draft only. It does not create runtime, API, DB schema, frontend page, Edge connector, Link connector, or Contracts schema.
