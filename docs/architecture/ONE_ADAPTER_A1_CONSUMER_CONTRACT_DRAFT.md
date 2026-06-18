# ONE Adapter A1 Consumer Contract Draft

## 1. Module Identity

- moduleId: one-adapter
- moduleName: ONE Adapter
- fullName: VANTARIS ONE Shared Foundation Consumer Adapter
- chineseName: 共享基础消费适配边界
- moduleType: platform-module
- status: draft-a1
- runtimeReady: false

## 2. Scope

Define docs-level consumer boundary for shared foundation references and module consumption policy routing.

## 3. Non-scope

- runtime adapter implementation
- API route implementation
- DB schema or table implementation
- contracts/schemas ownership or modification
- backend/frontend runtime implementation

## 4. OwnerScope

ONE Adapter owns consumer boundary draft, reference mapping draft, module consumption policy draft, and readiness dependency reference draft.

## 5. ForbiddenOwnership

ONE Adapter must not own EDGE/LINK runtime, DB runtime/schema, contracts schemas, API routes, DB tables, migration, or auth runtime.

## 6. ConsumedReferences

ONE Adapter consumes foundation references plus module references for UCore, UMMS, UESG, UCDE, UDOC, UConsole, Reports, Analytics, and Nexus AI Consumer.

## 7. ProvidedDraftObjects

ONE Adapter provides docs-level draft objects for consumer boundary, reference mapping, consumption policy, readiness dependency map, and contract draft routing policy.

## 8. Impact Model

- apiImpact: none-in-a1-draft
- dbImpact: none-in-a1-draft
- menuImpact: none-in-a1-draft
- runtimeImpact: none-in-a1-draft
- schemaImpact: none-in-a1-draft

## 9. Next Task

UCONSOLE-A1-MODULE-STATUS-CONTRACT-DRAFT

ONE-ADAPTER-A1 is a docs-level contract draft only. It does not create runtime, API, DB schema, frontend page, OpenAPI spec, or JSON schema.
