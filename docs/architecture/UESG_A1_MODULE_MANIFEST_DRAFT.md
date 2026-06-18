# UESG A1 Module Manifest Draft

## 1. Module Identity

- moduleId: uesg
- moduleName: UESG
- fullName: Unified ESG
- chineseName: 全向能源与可持续
- status: draft-a1
- runtimeReady: false

## 2. Scope

UESG A1 defines sustainability and energy context references, including carbon, utility, environmental performance, anomaly references, and cross-module linkage references.

## 3. Non-scope

- Edge/Link runtime ownership
- DB/Contracts schema ownership
- backend/frontend runtime implementation
- regulatory engine and carbon accounting engine implementation in A1

## 4. OwnerScope

UESG owner scope includes energy and sustainability context references, UDOC/UMMS/UCDE/UCore linkage references, and readiness context.

## 5. ForbiddenOwnership

UESG must not own Edge runtime, Link runtime, DB schema, Contracts schema, backend runtime, frontend runtime, or credential/secret/token material.

## 6. ConsumedObjects

UESG consumes energy, utility, environmental, carbon, maintenance, evidence, and operation context references through approved boundaries.

## 7. ProvidedObjects

UESG provides sustainability, energy, carbon, utility, anomaly, and readiness context objects.

## 8. Dependency Model

UESG depends on one-adapter, ucore, umms, udoc, ucde, uconsole, reports, analytics, and foundation references as reference-only dependencies.

## 9. Impact Model

- apiImpact: none-in-a1-draft
- dbImpact: none-in-a1-draft
- menuImpact: none-in-a1-draft
- runtimeImpact: none-in-a1-draft
- schemaImpact: none-in-a1-draft

## 10. Next Task

UMMS-A1-MODULE-MANIFEST-DRAFT

UESG-A1 is a module manifest draft only. It does not create runtime, API, DB schema, frontend page, Edge connector, Link connector, or Contracts schema.
