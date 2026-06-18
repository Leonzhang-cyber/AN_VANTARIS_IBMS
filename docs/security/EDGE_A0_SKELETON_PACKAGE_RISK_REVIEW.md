# EDGE A0 Skeleton Package Risk Review

## 1) Skeleton mistaken as runtime

- description: New package may be misunderstood as production runtime.
- impact: premature deployment attempts and incorrect readiness assumptions.
- control: explicit `SKELETON_ONLY`, `runtimeReady=false`, `gaReady=false` markers.
- current status: Controlled.

## 2) Legacy driver copied too early

- description: Legacy driver files could be copied directly into new package.
- impact: hidden coupling and migration regression risk.
- control: explicit no-copy rules + validation script checks.
- current status: Controlled.

## 3) DAO/SSE/API coupling imported

- description: Skeleton may accidentally import backend DAO/SSE/API paths.
- impact: prevents isolation and clean extraction.
- control: validation grep checks for forbidden coupling strings.
- current status: Controlled.

## 4) LINK runtime mixed into EDGE

- description: task scope could drift and create LINK runtime artifacts.
- impact: boundary confusion and phase-order violation.
- control: explicit prohibition and scoped file creation plan.
- current status: Controlled.

## 5) DB direct write risk

- description: future edge runtime might write DB directly.
- impact: architecture boundary break and data integrity risk.
- control: README/scope docs explicitly prohibit direct DB writes.
- current status: Controlled at A0 docs level.

## 6) Credential handling risk

- description: copied or newly added credential paths could leak secrets.
- impact: security exposure in repository.
- control: no secret material in A0 files + scan validation.
- current status: Controlled.

## 7) Protocol thread/socket lifecycle risk

- description: old lifecycle patterns may re-enter without manager design.
- impact: unstable runtime behavior under load/restarts.
- control: delay implementation to EDGE-A1 with lifecycle foundation.
- current status: Open for future runtime phase.

## 8) Contract mismatch risk

- description: future output payload may diverge from contracts A1 schema.
- impact: integration break with Link and downstream modules.
- control: A0 types/examples reference edge normalized object contract target.
- current status: Controlled at skeleton level.

## 9) UFMS boundary bypass risk

- description: EDGE runtime may later call UFMS runtime directly.
- impact: cross-system contamination and governance breach.
- control: boundary rule documented: UFMS only through adapter/boundary contract.
- current status: Controlled.
