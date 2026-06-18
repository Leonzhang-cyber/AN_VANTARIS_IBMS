# VANTARIS ONE Module Manifest Baseline

## 1. Purpose

This document defines the current A0 module manifest baseline for VANTARIS ONE and serves as the baseline for subsequent A1 module manifest drafts.

## 2. Current Modules

- ONE Adapter
- UCore
- UMMS
- UESG
- UDOC
- UCDE
- UConsole
- Reports
- Analytics
- Nexus AI Consumer, future

## 3. Shared Foundation Dependencies

AN_VANTARIS_Contracts, AN_VANTARIS_EDGE, and AN_VANTARIS_LINK are UFMS-led Shared Foundation dependencies.
VANTARIS ONE consumes these dependencies and does not privately fork runtime.

Foundation Layer is reference-only in this task. This task does not modify AN_VANTARIS_EDGE, AN_VANTARIS_LINK, AN_VANTARIS_DB, AN_VANTARIS_Contracts, contracts, or schemas.

## 4. A1 Manifest Rule

Each A1 manifest must define:

- moduleId
- module owner scope
- consumed objects
- provided objects
- status model
- traceability fields
- integration boundary
- forbidden ownership
- API/DB/menu impact, if any
- runtime readiness

## 5. Current Boundary

A0 manifest does not represent runtime ready status, does not create real modules, and does not modify API/DB/frontend.

## 6. UDOC A1 Realignment

UDOC A1 module manifest draft is established.
Historical A0 wording `idc-dcim` is realigned to UDOC as the primary module name.
UDOC remains `runtimeReady: false`.
UDOC impact remains `none-in-a1-draft` for API, DB, menu, runtime, and schema.

## 7. UESG UMMS UCore A1 Draft Alignment

UESG A1 module manifest draft is established with primary name UESG and historical ESG wording marked as deprecated primary naming.
UMMS A1 module manifest draft is established with primary name UMMS and historical MMS wording marked as deprecated primary naming.
UCore A1 module manifest draft is established with primary name UCore and historical IBMS Core wording marked as deprecated primary naming.

All three modules remain `runtimeReady: false`.
All three modules remain docs-only and keep API/DB/menu/runtime/schema impact as `none-in-a1-draft`.

## 8. ONE Adapter and UConsole A1 Platform Draft Alignment

ONE Adapter A1 consumer contract draft is established as docs-level platform boundary guidance.
UConsole A1 module status contract draft is established as docs-level platform status guidance.

Both modules remain `runtimeReady: false`.
Both modules remain docs-only and keep API/DB/menu/runtime/schema impact as `none-in-a1-draft`.

## 9. UCDE A2 Evidence Contract Draft Alignment

UCDE-A2 docs-level evidence contract draft is completed in VANTARIS ONE documentation scope.
UCDE does not own real contracts, real schemas, or runtime implementation.
`AN_VANTARIS_Contracts`, `contracts/`, and `schemas/` remain untouched in this task.
UCDE remains `runtimeReady: false`.

## 10. U Modules A2 Readiness Review Completion

Business modules A1 docs-level manifests are complete.
Platform A1 docs-level drafts are complete.
UCDE A2 docs-level evidence contract draft is complete.
No runtime/API/DB/schema/contracts readiness is claimed in this review.

## 11. U Modules A3 Implementation Gate Plan Completion

Docs-level readiness has been reviewed and implementation gate plan has been created.
No runtime/API/DB/schema/contracts readiness is claimed by A3 planning outputs.
Next recommended task is ONE-ADAPTER-A2-FOUNDATION-CONSUMER-GATE.

## 12. ONE Adapter A2 Foundation Consumer Gate Completion

ONE Adapter A2 Foundation Consumer Gate is completed as docs-level consumer boundary planning.
ONE Adapter remains consumer boundary only and does not own EDGE/LINK/DB/CONTRACTS runtime or schema.
No runtime/API/DB/schema/contracts implementation is authorized.
Next task is UCDE-A3-FORMAL-CONTRACT-PROMOTION-GATE.

## 13. UCDE A3 Formal Contract Promotion Gate Completion

UCDE-A3 formal contract promotion gate is completed as docs-level gate review.
Promotion is not executed in this task.
Formal contract/schema/OpenAPI/runtime remain blocked.
Next task is UCDE-A4-FORMAL-CONTRACT-PROMOTION-PLAN.
