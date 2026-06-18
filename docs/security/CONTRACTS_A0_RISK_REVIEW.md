# CONTRACTS A0 Risk Review

## 1) Manifest treated as runtime readiness

- description: Teams may interpret contract manifest publication as runtime migration approval.
- impact: Premature runtime rename/package migration and governance break.
- control: Manifest explicitly sets `runtimeReady: false` and `gaReady: false`.
- current status: Controlled.

## 2) Partial contracts mistaken as complete

- description: Baseline coverage can be mistaken for full production contract coverage.
- impact: Missing schema areas ignored during implementation.
- control: `missingP0Artifacts` backlog is explicit in manifest and A0 report.
- current status: Open but tracked.

## 3) Missing Edge/Link schemas block runtime work

- description: Edge normalized object and Link envelope/ACK/retry/DLQ schemas are not yet present.
- impact: Runtime extraction cannot proceed safely.
- control: Next task explicitly set to `CONTRACTS-A1-EDGE-LINK-SCHEMAS`.
- current status: Open and blocking runtime work.

## 4) API namespace policy applied before compatibility wrapper

- description: Future namespace policy may be applied directly without compatibility layer.
- impact: API clients break and rollback complexity increases.
- control: A0 policy requires wrapper first and forbids runtime API rename in this phase.
- current status: Controlled.

## 5) DB schema renamed without migration

- description: Contract naming updates can be misunderstood as DB rename authorization.
- impact: Schema drift, migration mismatch, and deployment risk.
- control: DB changes require AN_VANTARIS_DB migration contract and review.
- current status: Controlled.

## 6) Error/status codes drift across modules

- description: Modules may continue local code sets without centralized alignment.
- impact: Inconsistent observability and integration handling.
- control: Baseline `ERROR_CODES.md` and `STATUS_CODES.md` established for shared catalog.
- current status: Partially controlled; runtime adoption pending.

## 7) Secret accidentally added to contracts

- description: Contract samples may accidentally include credentials/tokens/private keys.
- impact: Secret leakage and security incident risk.
- control: No secret material rule in governance and validation scans before merge.
- current status: Controlled, no secret added in A0 outputs.

## 8) UFMS runtime contamination

- description: UFMS runtime/source/schema/auth/login/seed/migration logic could leak into contracts.
- impact: Boundary guard violation and cross-system contamination.
- control: UFMS allowed only as adapter/boundary reference; no runtime import rule enforced.
- current status: Controlled.

## 9) Contract version not enforced

- description: Changes may be merged without proper semantic version handling.
- impact: Compatibility ambiguity and artifact mismatch.
- control: `VERSION`, manifest version, and `VERSIONING_POLICY.md` establish version gates.
- current status: Controlled at baseline level.

## 10) Generated artifact mismatch

- description: Generated outputs may diverge from source contract definitions.
- impact: Runtime integration errors and audit failures.
- control: Governance requires generated artifacts to trace to source contract version/path.
- current status: Controlled by policy, tooling enforcement pending.
