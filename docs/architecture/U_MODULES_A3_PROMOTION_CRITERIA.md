# U Modules A3 Promotion Criteria

This document defines promotion criteria from docs-level planning to implementation candidates.
Current task performs no promotion.

## 1) Docs-level -> formal contract candidate

- allowed precondition: gate-approved contract promotion plan and boundary validation complete.
- forbidden shortcut: writing directly to `AN_VANTARIS_Contracts` from docs task.
- required approval: explicit promotion authorization.
- required boundary check: no forbidden path changes.
- required validation: naming/version/ownership consistency review.
- rollback requirement: revert to docs-level draft and cancel promotion state.

## 2) Docs-level -> JSON Schema candidate

- allowed precondition: contract candidate approved and schema scope authorized.
- forbidden shortcut: creating schema artifacts without promotion gate.
- required approval: explicit schema authorization.
- required boundary check: no runtime path contamination.
- required validation: field model consistency and compatibility plan.
- rollback requirement: remove candidate schema and restore docs-only status.

## 3) Docs-level -> OpenAPI candidate

- allowed precondition: API gate approved and module boundary locked.
- forbidden shortcut: direct OpenAPI authoring from planning stage.
- required approval: explicit API design authorization.
- required boundary check: backend/frontend untouched unless authorized.
- required validation: endpoint scope, ownership, and versioning review.
- rollback requirement: withdraw OpenAPI candidate and return to docs plan.

## 4) Docs-level -> API design candidate

- allowed precondition: platform/module gate approval and dependency readiness confirmed.
- forbidden shortcut: implementing routes while design is unapproved.
- required approval: explicit API design gate approval.
- required boundary check: no runtime implementation changes.
- required validation: contract and integration impact review.
- rollback requirement: remove API design state and restore prior nextTask.

## 5) Docs-level -> DB design candidate

- allowed precondition: data ownership decision approved and schema gate approved.
- forbidden shortcut: direct table/model design without DB gate.
- required approval: explicit DB design authorization.
- required boundary check: no migration/prisma/runtime edits in planning gate.
- required validation: ownership, retention, and migration risk review.
- rollback requirement: drop DB design candidate and revert to docs-level.

## 6) Docs-level -> frontend design candidate

- allowed precondition: UI gate approved and API/status dependencies defined.
- forbidden shortcut: implementing pages/routes during planning.
- required approval: explicit frontend design authorization.
- required boundary check: no frontend source modifications in planning gate.
- required validation: boundary and permissions model review.
- rollback requirement: remove UI design candidate and revert to docs-only.

## 7) Docs-level -> runtime implementation candidate

- allowed precondition: prior contract/schema/API/DB gates approved and risk controls accepted.
- forbidden shortcut: direct runtime build from docs-level plan.
- required approval: explicit runtime implementation authorization per module.
- required boundary check: full forbidden-path and shared-foundation boundary checks.
- required validation: test strategy, rollback plan, and release gating approved.
- rollback requirement: revert implementation candidate flags and return to gate planning.
