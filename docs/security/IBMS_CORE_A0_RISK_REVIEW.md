# IBMS Core A0 Risk Review

## 1) IBMS Core expands back into monolithic IBMS

- description: IBMS Core scope grows until it becomes the entire platform again.
- impact: module boundaries collapse and roadmap execution slows.
- control: enforce documented ownership boundary and separate module tasks.
- current status: controlled by A0 boundary documents.
- next mitigation task: IBMS-CORE-A1-MODULE-MANIFEST-DRAFT.

## 2) IBMS Core reimplements Edge runtime

- description: IBMS Core starts implementing protocol/connector runtime responsibilities.
- impact: duplicated runtime stack and shared foundation ownership conflict.
- control: prohibit Edge runtime ownership in IBMS Core governance rules.
- current status: controlled at A0 policy level.
- next mitigation task: architecture review checklist for Edge ownership exclusion.

## 3) IBMS Core reimplements Link semantics

- description: IBMS Core introduces ACK/DLQ/retry semantics locally.
- impact: delivery behavior divergence and integration instability.
- control: keep Link semantics owned by shared foundation only.
- current status: controlled at documentation level.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT.

## 4) IBMS Core redefines shared contracts

- description: IBMS Core proposes independent schema changes outside shared process.
- impact: contract drift and cross-module incompatibility.
- control: consume shared contracts through approved adapter/contracts only.
- current status: controlled by module rules.
- next mitigation task: shared compatibility gate definition in A1.

## 5) IBMS Core imports UFMS runtime source

- description: direct UFMS runtime/source import is introduced into IBMS Core implementation.
- impact: boundary contamination and deployment coupling.
- control: strict prohibition of UFMS runtime/source import and adapter-boundary-only consumption.
- current status: controlled by governance.
- next mitigation task: boundary compliance checks in future A1 implementation review.

## 6) IBMS Core maps data to DB before contract is stable

- description: premature DB mapping starts before consumption contract is frozen.
- impact: rework, schema churn, and migration risk.
- control: A0 remains docs-only with no DB mapping.
- current status: controlled.
- next mitigation task: defer mapping to approved post-A1 design.

## 7) IBMS Core loses traceability fields

- description: messageId/traceId/correlationId are dropped in presentation and business flow.
- impact: weak observability and incident forensic gaps.
- control: require preservation of traceability fields in module rules and adapter contract.
- current status: partially controlled pending runtime enforcement.
- next mitigation task: define traceability preservation test matrix in A1.

## 8) IBMS Core overlaps with MMS

- description: work-order and maintenance ownership boundaries become unclear.
- impact: duplicated workflows and ownership conflicts.
- control: define MMS handoff as boundary interaction, not IBMS Core ownership transfer.
- current status: open.
- next mitigation task: MMS-A0-MODULE-BOUNDARY.

## 9) IBMS Core overlaps with ESG

- description: sustainability and energy analytics responsibilities drift into IBMS Core scope.
- impact: KPI/report ownership confusion and duplicated metrics logic.
- control: keep ESG domain ownership explicit and IBMS Core as consumer/presenter only when applicable.
- current status: open.
- next mitigation task: ESG-A0-MODULE-BOUNDARY.

## 10) IBMS Core overlaps with CDE evidence chain

- description: IBMS Core attempts to own evidence-chain core capabilities.
- impact: duplication and governance/audit inconsistency.
- control: IBMS Core consumes evidence references while CDE owns evidence-chain core.
- current status: open.
- next mitigation task: CDE-A0-EVIDENCE-CONSUMER.
