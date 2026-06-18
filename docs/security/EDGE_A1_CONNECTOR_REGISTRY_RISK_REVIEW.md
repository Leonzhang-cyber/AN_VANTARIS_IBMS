# EDGE A1 Connector Registry Risk Review

## 1) Registry mistaken as real device runtime

- description: Teams may assume connector registry equals production edge runtime.
- impact: premature deployment expectation and wrong integration assumptions.
- control: explicit dry-run-only scope and readiness marker.
- current status: Controlled.

## 2) Connector lifecycle not tied to real driver lifecycle yet

- description: In-memory lifecycle state does not control actual protocol drivers.
- impact: operational mismatch when runtime adapters are introduced.
- control: document that current lifecycle is dry-run simulation only.
- current status: Open by design.

## 3) Future driver adapter may reintroduce DAO coupling

- description: Legacy extraction could add DAO/model dependencies into EDGE.
- impact: breaks package isolation and portability.
- control: validation + governance rule for no DAO/model imports.
- current status: Controlled at A1 baseline.

## 4) Future SSE/API coupling risk

- description: Adapter integration may reintroduce direct SSE/API calls.
- impact: transport/runtime boundary violation.
- control: enforce Link envelope path and forbid direct UI/API push from EDGE.
- current status: Controlled at A1 baseline.

## 5) Future credential handling risk

- description: Real connector onboarding may expose credentials in package code.
- impact: secret leakage/security incidents.
- control: no credential fields in dry-run fixtures; security review gate in future tasks.
- current status: Controlled at A1 baseline.

## 6) LINK runtime mixed too early

- description: EDGE A1 scope might drift into LINK runtime creation.
- impact: phase-order violation and architecture confusion.
- control: explicit prohibition and validation checks.
- current status: Controlled.

## 7) Dry-run status mistaken as production health

- description: simulated statuses may be interpreted as live runtime health.
- impact: false operational confidence.
- control: report and code clearly label dry-run data as non-runtime.
- current status: Controlled.

## 8) UFMS direct runtime call risk

- description: Future adapters could attempt direct UFMS runtime invocation.
- impact: boundary contamination and governance breach.
- control: UFMS references only as boundary restriction; no direct runtime call allowed.
- current status: Controlled.
