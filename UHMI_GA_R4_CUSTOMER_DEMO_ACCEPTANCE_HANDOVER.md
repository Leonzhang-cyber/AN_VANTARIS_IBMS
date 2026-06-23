# UHMI-GA-R4 Customer Demo Acceptance Handover

PASS marker: `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`

## What The Customer Sees

- Customer Preview Export Package.
- Offline Demo Hand-off material.
- Demo-ready read-only UHMI Workspace path.
- R3 customer preview package.
- R2F evidence pack.
- `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.
- Disabled actions and future-only control path.

## Customer Confirmation Items

- UHMI remains UConsole-owned.
- UHMI is not HMI Server.
- UHMI is not SCADA replacement.
- Export package is `MANIFEST_EVIDENCE_RUNBOOK_ONLY`.
- No runnable production package generated.
- No dist/build committed.
- No .env/secrets committed.

## Non-production Statement

This handover does not represent production enablement. It does not represent device control enablement. It does not represent DB migration execution. It does not represent EDGE/LINK command execution.

Production activation: `NOT EXECUTED`. Device control: `NOT EXECUTED`. Runtime activation: `NOT EXECUTED`. DB migration/write: `NOT EXECUTED`. EDGE/LINK command execution: `NOT EXECUTED`. Auth/Login/JWT/RBAC mutation: `NOT EXECUTED`.

No Direct Device Control. No Runtime Activation. No DB Write. No EDGE Command Execution. No LINK Command Execution. No auth / login / JWT / RBAC mutation.

## Acceptance Sign-off Checks

- Customer understands the package is evidence and runbook only.
- Customer understands no install/rollback was executed.
- Customer understands no production activation was executed.
- Customer understands no control path was activated.
- Customer understands future control requires policy gate, approval, audit/UCDE, LINK, EDGE, and device execution guards.

## Required Before Production

- production activation plan
- deployment environment verification
- DB migration plan
- runtime control policy gate
- approval workflow
- EDGE/LINK execution guard
- security acceptance
- customer UAT

Future control path:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`
