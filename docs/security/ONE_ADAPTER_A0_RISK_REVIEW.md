# ONE Adapter A0 Risk Review

## 1) Adapter becomes hidden duplicate Link runtime

- description: adapter scope expands into ACK/retry/DLQ runtime behavior and duplicates shared link responsibilities.
- impact: duplicate runtime, ownership conflict, inconsistent delivery behavior.
- control: enforce consumer-only adapter scope and block Link runtime responsibilities in ONE.
- current status: controlled by A0 governance definition.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT with explicit runtime guardrails.

## 2) Adapter redefines shared contracts

- description: adapter introduces local schema variants instead of consuming shared contracts.
- impact: schema divergence and integration break risk.
- control: mandate consume-only contract policy and schemaVersion compatibility checks.
- current status: controlled by interface rules.
- next mitigation task: shared compatibility matrix with version pin policy.

## 3) Adapter imports UFMS runtime source

- description: implementation attempts direct import of UFMS runtime code.
- impact: boundary contamination and release coupling.
- control: prohibit UFMS runtime/source import and enforce adapter/API boundary.
- current status: controlled by A0 policy.
- next mitigation task: add code review checklist for UFMS boundary compliance in A1.

## 4) Adapter bypasses version validation

- description: adapter accepts payloads without schemaVersion or compatibility validation.
- impact: malformed payload acceptance and runtime failures downstream.
- control: require schemaVersion validation and rejection of unsupported versions.
- current status: open until A1 validation contract is drafted.
- next mitigation task: define adapter version gate specification in A1.

## 5) Adapter loses traceId/messageId

- description: adapter mapping drops traceability fields during transformation.
- impact: reduced observability and incident forensics capability.
- control: preserve messageId/traceId/correlationId as non-optional adapter behavior.
- current status: controlled by documented rules, pending runtime enforcement.
- next mitigation task: define field-preservation test matrix in A1.

## 6) Adapter maps data directly to DB too early

- description: direct DB mapping is introduced before contract/interface stabilization.
- impact: schema lock-in, migration churn, and premature coupling.
- control: A0 prohibits DB mapping and keeps model documentation-only.
- current status: controlled.
- next mitigation task: defer DB mapping decisions to post-A1 approved design stage.

## 7) Adapter creates security identity drift

- description: tenant/project/site/source identity semantics diverge from shared contracts.
- impact: authorization confusion and audit inconsistency.
- control: require tenantId/projectId/siteId/source identity validation at adapter boundary.
- current status: partially controlled by A0 rules.
- next mitigation task: define identity normalization contract tests in A1.

## 8) Adapter depends on unstable shared foundation draft

- description: ONE integration assumes non-frozen shared artifacts.
- impact: frequent breaking changes and repeated rework.
- control: stage-gate runtime implementation until shared ownership and versioning are frozen.
- current status: open.
- next mitigation task: align with UFMS-SHARED-FOUNDATION-A0-OWNERSHIP-FREEZE output.

## 9) Console shows health before reliable source exists

- description: Console integration displays adapter/foundation health before reliable source semantics are finalized.
- impact: misleading operational status and false confidence.
- control: mark health integration as later-stage and source-validated only.
- current status: open.
- next mitigation task: CONSOLE-A0-SHARED-FOUNDATION-HEALTH-VIEW with source quality criteria.

## 10) Fault intelligence output boundary unclear

- description: unclear ownership and semantics for optional UFMS fault intelligence outputs.
- impact: overlap between UFMS intelligence and ONE business interpretation layers.
- control: classify fault intelligence as optional input through explicit adapter contract boundary.
- current status: open.
- next mitigation task: ONE-ADAPTER-A1-CONSUMER-CONTRACT-DRAFT with optional FI output section.
