# IDC / DCIM A0 Risk Review

## 1) IDC / DCIM becomes another monolithic operations platform

- description: IDC/DCIM expands to absorb unrelated platform domains.
- impact: module boundaries blur and delivery complexity increases.
- control: enforce IDC/DCIM business scope and explicit ownership exclusions.
- current status: controlled by A0 boundary documents.
- next mitigation task: IDC-DCIM-A1-MODULE-MANIFEST-DRAFT.

## 2) IDC / DCIM overlaps with IBMS Core dashboard

- description: IDC/DCIM takes ownership of general building operations dashboard.
- impact: duplicated UI ownership and inconsistent operator experience.
- control: keep IBMS Core for general building dashboard; IDC/DCIM for data-center specialization.
- current status: open but bounded.
- next mitigation task: IBMS-CORE-A1-MODULE-MANIFEST-DRAFT alignment review.

## 3) IDC / DCIM overlaps with MMS work order lifecycle

- description: IDC/DCIM attempts to own work order state transitions.
- impact: duplicated maintenance workflow ownership.
- control: IDC/DCIM provides handoff context only; MMS owns lifecycle.
- current status: controlled at governance level.
- next mitigation task: MMS-A1-MODULE-MANIFEST-DRAFT.

## 4) IDC / DCIM overlaps with ESG carbon reporting

- description: IDC/DCIM starts owning carbon-reporting interpretation outputs.
- impact: ESG ownership conflicts and inconsistent sustainability reporting.
- control: IDC/DCIM provides energy/PUE context; ESG owns carbon reporting model.
- current status: open but bounded.
- next mitigation task: ESG-A1-MODULE-MANIFEST-DRAFT.

## 5) IDC / DCIM overlaps with CDE evidence chain

- description: IDC/DCIM attempts to own evidence chain core behavior.
- impact: duplicated traceability logic and audit inconsistency.
- control: IDC/DCIM provides evidence references only; CDE owns chain core.
- current status: open.
- next mitigation task: CDE-A0-EVIDENCE-CONSUMER.

## 6) IDC / DCIM reimplements Edge/Link runtime

- description: IDC/DCIM introduces protocol or delivery runtime behavior.
- impact: shared foundation duplication and operational risk.
- control: block Edge/Link runtime responsibilities in IDC/DCIM rules.
- current status: controlled.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT.

## 7) IDC / DCIM redefines shared contracts

- description: IDC/DCIM introduces local schema variants outside shared governance.
- impact: contract drift and compatibility failures.
- control: consume shared contracts through approved adapter/contracts only.
- current status: controlled.
- next mitigation task: shared compatibility review during A1 planning.

## 8) IDC / DCIM imports UFMS runtime source

- description: direct UFMS backend/runtime source import is introduced.
- impact: boundary contamination and release coupling.
- control: strict no-import policy and approved adapter boundary only.
- current status: controlled.
- next mitigation task: UFMS boundary checklist for IDC-DCIM A1.

## 9) IDC / DCIM creates capacity DB model before boundary is approved

- description: data model implementation starts before module boundary stabilization.
- impact: rework and migration churn.
- control: A0 remains docs-only and blocks DB work.
- current status: controlled.
- next mitigation task: defer data modeling to post-A1 approved stage.

## 10) IDC / DCIM loses traceability from telemetry/event/alarm to incident/capacity view

- description: traceability fields are dropped during IDC/DCIM transformations.
- impact: poor observability and weak incident forensics.
- control: preserve messageId/traceId/correlationId as mandatory fields.
- current status: partially controlled pending runtime enforcement.
- next mitigation task: define traceability test matrix in IDC-DCIM A1.

## 11) IDC / DCIM is mistaken as full certified DCIM engine too early

- description: stakeholders treat A0 as full certified production-grade DCIM engine.
- impact: expectation mismatch and compliance/operational risk.
- control: explicitly mark A0 as boundary-definition stage only.
- current status: controlled by documentation.
- next mitigation task: add A1 scope disclaimer and readiness criteria.
