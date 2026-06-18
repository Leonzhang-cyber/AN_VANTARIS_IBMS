# CONSOLE A0 Risk Review

## 1) Console becomes hidden monolith

- description: Console scope grows to absorb platform and business implementation logic.
- impact: blurred boundaries and high maintenance complexity.
- control: enforce Console as visibility/control entry, not runtime owner.
- current status: controlled by A0 boundary and rules documents.
- next mitigation task: CONSOLE-A1-MODULE-STATUS-CONTRACT-DRAFT.

## 2) Console overlaps with business module logic

- description: Console starts implementing IBMS/MMS/ESG/IDC/CDE business behavior.
- impact: duplicated logic and ownership conflicts.
- control: Console shows status only; business modules own business logic.
- current status: controlled.
- next mitigation task: MODULE-MANIFEST-A0-CROSS-MODULE-BASELINE.

## 3) Console overlaps with Shared Foundation runtime

- description: Console begins owning shared runtime behaviors rather than status visualization.
- impact: architecture contamination and duplicated runtime paths.
- control: keep Shared Foundation runtime external; Console consumes status via adapter/contracts.
- current status: controlled.
- next mitigation task: adapter status contract alignment in A1.

## 4) Console reimplements Link health semantics

- description: Console adds local Link ACK/DLQ/retry semantics interpretation as source of truth.
- impact: inconsistent status semantics and incident confusion.
- control: use approved Link status contracts only; no local runtime semantics.
- current status: open but bounded.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT.

## 5) Console redefines contracts/status models

- description: Console introduces its own global contracts or status taxonomies outside governance.
- impact: contract drift and cross-module incompatibility.
- control: consume approved adapter/API/contracts and avoid redefining global contracts.
- current status: controlled.
- next mitigation task: MODULE-MANIFEST-A0-CROSS-MODULE-BASELINE.

## 6) Console imports UFMS runtime source

- description: direct UFMS runtime/backend import is introduced into Console implementation.
- impact: boundary contamination and release coupling.
- control: strict no-import rule and approved integration boundary only.
- current status: controlled.
- next mitigation task: UFMS boundary checklist in CONSOLE-A1.

## 7) Console exposes health before reliable source exists

- description: health indicators are shown before source quality/freshness is validated.
- impact: misleading operational decisions and false confidence.
- control: mark data as boundary-only in A0 and define source quality gates in A1.
- current status: open.
- next mitigation task: CONSOLE-A1-MODULE-STATUS-CONTRACT-DRAFT.

## 8) Console creates RBAC/menu changes before approval

- description: A0 work leaks into unauthorized RBAC/menu/runtime changes.
- impact: ungoverned permission drift and UI regressions.
- control: explicit prohibition of RBAC/menu/API/DB changes in A0.
- current status: controlled.
- next mitigation task: separate approved RBAC/menu task after A1.

## 9) Console loses traceability for integration status

- description: traceId/correlationId continuity is dropped in status displays.
- impact: weak troubleshooting and auditability.
- control: preserve traceability fields as required display metadata.
- current status: partially controlled pending runtime enforcement.
- next mitigation task: add traceability checks in CONSOLE-A1 contract draft.

## 10) Console is mistaken as production control plane too early

- description: stakeholders assume A0 equals production-ready control plane runtime.
- impact: expectation mismatch and operational risk.
- control: clearly label A0 as documentation/boundary stage only.
- current status: controlled by A0 wording.
- next mitigation task: readiness criteria and rollout gating in A1.
