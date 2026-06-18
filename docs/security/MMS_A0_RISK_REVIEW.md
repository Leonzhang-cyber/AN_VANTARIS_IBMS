# MMS A0 Risk Review

## 1) MMS becomes another monolithic facility platform

- description: MMS scope expands beyond maintenance and absorbs unrelated platform capabilities.
- impact: blurred module boundaries and slower delivery.
- control: enforce MMS boundary as maintenance lifecycle only.
- current status: controlled by A0 boundary and rules docs.
- next mitigation task: MMS-A1-MODULE-MANIFEST-DRAFT.

## 2) MMS overlaps with IBMS Core operations dashboard

- description: MMS starts owning building operation dashboards and core operations views.
- impact: duplicated UX and ownership conflicts with IBMS Core.
- control: keep MMS focused on maintenance actions while IBMS Core owns operations dashboard.
- current status: open but documented.
- next mitigation task: IBMS-CORE-A1-MODULE-MANIFEST-DRAFT alignment review.

## 3) MMS overlaps with UFMS RCA/correlation engine

- description: MMS introduces fault correlation/RCA logic that belongs to UFMS.
- impact: duplicated analytics logic and boundary contamination.
- control: allow only approved UFMS intelligence outputs through adapter boundary.
- current status: controlled at governance level.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT with optional FI clause.

## 4) MMS reimplements Edge/Link runtime

- description: MMS adds protocol ingestion or delivery runtime behaviors.
- impact: duplicates shared foundation runtime and creates maintenance burden.
- control: prohibit Edge/Link runtime ownership in MMS rules.
- current status: controlled by A0 policy.
- next mitigation task: architecture compliance check before A1 runtime design.

## 5) MMS redefines shared contracts

- description: MMS creates module-specific contract variants outside shared process.
- impact: schema drift and incompatibility across modules.
- control: consume shared contracts only via approved adapter/contracts.
- current status: controlled.
- next mitigation task: shared compatibility gate definition in A1.

## 6) MMS imports UFMS runtime source

- description: direct UFMS runtime/backend source import is introduced.
- impact: coupling, contamination, and release risk.
- control: strict no-import policy and adapter boundary enforcement.
- current status: controlled.
- next mitigation task: add boundary checklist to MMS A1 design review.

## 7) MMS creates work order DB model before boundary is approved

- description: DB model implementation starts before module boundary and contracts stabilize.
- impact: rework and migration churn.
- control: A0 remains docs-only and blocks DB work.
- current status: controlled.
- next mitigation task: schedule data model phase after A1 approval.

## 8) MMS loses traceability from alarm/event/fault to work order

- description: traceability fields are dropped during conversion to maintenance context.
- impact: weak auditability and incident forensics.
- control: preserve messageId/traceId/correlationId as mandatory conversion fields.
- current status: partially controlled pending runtime tests.
- next mitigation task: define traceability conversion test matrix in MMS-A1.

## 9) MMS overlaps with CDE evidence chain

- description: MMS attempts to own evidence chain core capabilities instead of references.
- impact: governance overlap and evidence inconsistency.
- control: MMS uses evidence references; CDE owns evidence chain core.
- current status: open but bounded.
- next mitigation task: CDE-A0-EVIDENCE-CONSUMER.

## 10) MMS overlaps with ESG maintenance-to-carbon reporting

- description: MMS starts owning ESG carbon/accounting outcomes directly.
- impact: ESG ownership confusion and reporting inconsistency.
- control: MMS provides maintenance context; ESG owns carbon/accounting model.
- current status: open.
- next mitigation task: ESG-A0-MODULE-BOUNDARY.
