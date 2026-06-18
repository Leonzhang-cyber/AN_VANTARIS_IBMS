# VANTARIS ONE Transition Index

Completed stages:

- ONE-TRANSITION-A0 — 65f55b6
- ONE-TRANSITION-A1 — e6979ff
- ONE-TRANSITION-A2 — ad997d4
- ONE-TRANSITION-A3 — d111c62
- ONE-TRANSITION-A4 — 3e817aa
- ONE-TRANSITION-A5 — 78b1434
- ONE-TRANSITION-A6 — cc60063
- ONE-TRANSITION-A7 — 80759ee
- REBRAND-ONE-R0 — d880ece
- REBRAND-ONE-R1 — current task
- CONTRACTS-A0-MANIFEST-BASELINE — ab2e953
- CONTRACTS-A1-EDGE-LINK-SCHEMAS — cc7f4c6
- EDGE-SOURCE-AUDIT — 307a92a
- EDGE-A0-SKELETON-PACKAGE — 5846642
- EDGE-A0.1-TYPECHECK-TOOLCHAIN-BASELINE — 362e756
- EDGE-A1-CONNECTOR-REGISTRY-DRYRUN — d0f5181
- SHARED-FOUNDATION-A0-SCOPE-REALIGNMENT — current task
- ONE-SHARED-FOUNDATION-CONSUMER-A0 — current task
- ONE-ADAPTER-A0-SHARED-FOUNDATION-INTERFACE — current task
- IBMS-CORE-A0-BUSINESS-MODULE-BOUNDARY — current task
- MMS-A0-MODULE-BOUNDARY — current task
- ESG-A0-MODULE-BOUNDARY — current task
- IDC-DCIM-A0-MODULE-BOUNDARY — current task
- CDE-A0-EVIDENCE-CONSUMER — current task
- CONSOLE-A0-SHARED-FOUNDATION-HEALTH-VIEW — current task
- MODULE-MANIFEST-A0-CROSS-MODULE-BASELINE — current task
- CDE-A1-MODULE-MANIFEST-DRAFT — current task
- U-MODULES-A0-NAMING-AND-LAYER-REALIGNMENT — current task
- UDOC-A1-MODULE-MANIFEST-DRAFT — current task
- UESG-A1-MODULE-MANIFEST-DRAFT — current task
- UMMS-A1-MODULE-MANIFEST-DRAFT — current task
- UCORE-A1-MODULE-MANIFEST-DRAFT — current task
- ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT — current task
- UCONSOLE-A1-MODULE-STATUS-CONTRACT-DRAFT — current task
- UCDE-A2-EVIDENCE-CONTRACT-DRAFT — current task
- U-MODULES-A2-READINESS-REVIEW — current task
- U-MODULES-A3-IMPLEMENTATION-GATE-PLAN — current task
- ONE-ADAPTER-A2-FOUNDATION-CONSUMER-GATE — current task
- UCDE-A3-FORMAL-CONTRACT-PROMOTION-GATE — current task
- UCDE-A4-FORMAL-CONTRACT-PROMOTION-PLAN — current task
- ONE-ADAPTER-A1-CANCEL-AND-FUNCTION-REALLOCATION — current task
- REPORTS-A1-MODULE-MANIFEST-DRAFT — current task
- REPORTS-A2-API-DATA-MODEL-GATE — current task

## Current Allowed Work

- docs-only brand alignment
- metadata alignment
- ONE consumer-governance realignment
- adapter/business-module planning

## Current Forbidden Work

- runtime rename
- backend/frontend move
- API path rename
- DB table rename
- package migration
- ONE-private expansion of Edge/Link/Contracts runtime
- direct UFMS runtime/source/auth/login/seed/migration copy into ONE

## Next Recommended Task

- REPORTS-A3-REPORT-CATALOG-SPEC-DRAFT

## Historical Name Mapping

- ESG -> UESG
- esg -> uesg
- MMS -> UMMS
- mms -> umms
- IBMS Core -> UCore
- ibms-core -> ucore
- Console -> UConsole
- console -> uconsole
- IDC/DCIM -> UDOC
- idc-dcim -> udoc
- Data Center Operations -> UDOC
- DATA-CENTER-A1 -> UDOC-A1-MODULE-MANIFEST-DRAFT
- IDC-DCIM-A1 -> UDOC-A1-MODULE-MANIFEST-DRAFT
- CDE-A2 -> UCDE-A2-EVIDENCE-CONTRACT-DRAFT
- CDE evidence contract -> UCDE evidence contract draft

Old wording is historical only, and primary name in this phase is UCDE-A2.

## Shared Foundation Runtime Continuation

Shared runtime tasks continue under UFMS-led roadmap: `SHARED-CONTRACTS`, `SHARED-EDGE`, `SHARED-LINK`.

## ONE Consumer Rule

After this point, VANTARIS ONE does not expand Edge/Link/Contracts as private runtime.
VANTARIS ONE work focuses on adapters and business modules.
VANTARIS ONE adapter is consumer boundary only; runtime implementation requires separate A1 approval.
IBMS Core is now defined as VANTARIS ONE business module, not as the entire platform and not as owner of Edge / Link / Contracts.
MMS is now defined as VANTARIS ONE maintenance business module, not as owner of Edge / Link / Contracts and not as owner of UFMS RCA/correlation runtime.
ESG is now defined as VANTARIS ONE energy and sustainability business module, not as owner of Edge / Link / Contracts, not as owner of UFMS RCA/correlation runtime, not as MMS workflow owner, and not as CDE evidence chain owner.
IDC / DCIM is now defined as VANTARIS ONE data center infrastructure operations business module, not as owner of Edge / Link / Contracts, not as owner of UFMS RCA/correlation runtime, not as MMS workflow owner, not as ESG carbon reporting owner, and not as CDE evidence chain owner.
CDE is now defined as VANTARIS ONE evidence and traceability consumer module, not as owner of Edge / Link / Contracts, not as owner of UFMS RCA/correlation runtime, not as owner of MMS workflow, ESG calculation model, or IDC/DCIM capacity/PUE model.
Console is now defined as VANTARIS ONE platform control and health view module, not as owner of Edge / Link / Contracts, not as owner of UFMS RCA/correlation runtime, and not as owner of business module logic.
VANTARIS ONE now has cross-module manifest baseline for ONE Adapter, IBMS Core, MMS, ESG, IDC/DCIM, CDE, Console, Reports, Analytics and future Nexus AI Consumer.
CDE now has module manifest draft and evidence object draft, both docs-only and runtimeReady false.
VANTARIS ONE module naming and layer model is realigned to U-series names: UCore, UMMS, UESG, UCDE, UDOC, and UConsole, while Foundation Layer remains reference-only in this task.
Promotion from docs-level planning to implementation requires explicit approval in a separate authorized task.
Direct runtime implementation remains blocked after A3.
Contract/schema promotion remains blocked unless separately authorized.
Direct Foundation modification remains blocked.
ONE Adapter implementation remains blocked unless separately authorized.
Formal contract creation remains blocked.
ONE Adapter is cancelled as module and retained only as deprecated historical docs.
consumer boundary responsibility is reallocated to governance/module manifest/UConsole.
contract routing responsibility is reallocated to Contracts + LINK.
object mapping responsibility is reallocated to EDGE + Contracts.
identity preservation responsibility is reallocated to EDGE + LINK + UCDE + DB.
traceability preservation responsibility is reallocated to LINK + UCDE + DB.
external ingress responsibility is reallocated to EDGE Fleet.
Reports is defined as Reporting Workspace (`报表工作台`) in platform layer draft scope.
Reports runtime/API/DB/frontend implementation remains blocked unless separately authorized.
Reports API/data model is currently gate-level candidate planning only.
Reports backend/frontend/API/DB/export/schedule implementation remains blocked unless separately authorized.
