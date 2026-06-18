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

## Recommended Next Tasks

1. CDE-A1-MODULE-MANIFEST-DRAFT
2. IDC-DCIM-A1-MODULE-MANIFEST-DRAFT
3. ESG-A1-MODULE-MANIFEST-DRAFT
4. MMS-A1-MODULE-MANIFEST-DRAFT
5. IBMS-CORE-A1-MODULE-MANIFEST-DRAFT
6. ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT
7. CONSOLE-A1-MODULE-STATUS-CONTRACT-DRAFT

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
