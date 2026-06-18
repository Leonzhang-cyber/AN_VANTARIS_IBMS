# ESG A0 Risk Review

## 1) ESG becomes another monolithic analytics platform

- description: ESG scope expands beyond energy/sustainability interpretation into a broad analytics platform.
- impact: module boundaries collapse and governance complexity increases.
- control: enforce ESG as a focused business module with explicit ownership limits.
- current status: controlled by A0 boundary and rules documents.
- next mitigation task: ESG-A1-MODULE-MANIFEST-DRAFT.

## 2) ESG overlaps with IBMS Core operations dashboard

- description: ESG starts owning operational dashboards intended for IBMS Core.
- impact: duplicated views and product ownership conflicts.
- control: keep operations dashboard ownership in IBMS Core; ESG consumes context only.
- current status: open but bounded.
- next mitigation task: IBMS-CORE-A1-MODULE-MANIFEST-DRAFT alignment checkpoint.

## 3) ESG overlaps with MMS maintenance lifecycle

- description: ESG attempts to own maintenance action lifecycle instead of maintenance impact interpretation.
- impact: duplicated workflow ownership and process ambiguity.
- control: keep work order lifecycle in MMS and let ESG consume maintenance outcome references.
- current status: open but bounded.
- next mitigation task: MMS-A1-MODULE-MANIFEST-DRAFT boundary reinforcement.

## 4) ESG overlaps with CDE evidence chain

- description: ESG attempts to own evidence chain core functionality.
- impact: audit lineage inconsistency and duplicated compliance logic.
- control: ESG consumes evidence references only; CDE owns evidence chain core.
- current status: open.
- next mitigation task: CDE-A0-EVIDENCE-CONSUMER.

## 5) ESG reimplements Edge/Link runtime

- description: ESG introduces data ingestion or delivery runtime responsibilities.
- impact: shared foundation duplication and integration instability.
- control: prohibit Edge/Link runtime ownership in ESG governance.
- current status: controlled by A0 module rules.
- next mitigation task: architecture compliance checks before ESG A1 runtime planning.

## 6) ESG redefines shared contracts

- description: ESG creates local schema variants outside shared contracts governance.
- impact: contract drift and cross-module incompatibility.
- control: consume shared contracts through ONE adapter/approved boundaries only.
- current status: controlled.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT.

## 7) ESG imports UFMS runtime source

- description: ESG implementation directly imports UFMS backend/runtime code.
- impact: boundary contamination and release coupling risks.
- control: strict no-import rule and adapter boundary enforcement.
- current status: controlled.
- next mitigation task: add UFMS boundary checklist into ESG A1 design review.

## 8) ESG creates carbon DB model before boundary is approved

- description: early DB model implementation is started before boundary and contracts are frozen.
- impact: migration churn and costly rework.
- control: A0 remains docs-only and blocks DB changes.
- current status: controlled.
- next mitigation task: defer data model implementation to approved A1/A2 stage.

## 9) ESG loses traceability from telemetry/event/alarm to ESG report

- description: traceability fields are lost during metric/report transformation.
- impact: weak explainability and auditability of ESG outputs.
- control: preserve messageId/traceId/correlationId throughout ESG interpretation paths.
- current status: partially controlled pending runtime enforcement.
- next mitigation task: define traceability preservation tests in ESG A1.

## 10) ESG is mistaken as certified carbon accounting engine too early

- description: stakeholders treat A0 ESG as a finance-grade certified accounting engine.
- impact: compliance risk and incorrect external claims.
- control: explicitly mark A0 as boundary/model only and exclude formal certification engine scope.
- current status: controlled by A0 documentation language.
- next mitigation task: ESG-A1 scope note with certification boundary disclaimer.
