# UHMI-GA-R4 Customer Preview Export Package Index

PASS marker: `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`

## Purpose

UHMI-GA-R4 creates a Customer Preview Export Package index and Offline Demo Hand-off material for the UHMI read-only workspace preview chain. This export package is `MANIFEST_EVIDENCE_RUNBOOK_ONLY`: it is a checklist, evidence, and hand-off index, not a production install package, not a deployment bundle, and not a runnable package.

UHMI = Unified Human-Machine Interface. VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system. UHMI remains UConsole-owned. UHMI is not HMI Server. UHMI is not SCADA replacement.

## Customer Preview Export Package Scope

Included:

- UHMI docs index.
- UHMI registry references.
- UHMI validator references.
- Offline Demo Hand-off Guide.
- Engineer Demo Runbook.
- Customer Demo Acceptance Handover.
- Export Scope / Exclusion Matrix.
- R1-R3 release chain linkage.
- R2F evidence pack linkage.
- R3 customer preview linkage.

Excluded:

- Runnable production package.
- Production install package.
- Production deployment package.
- `dist` or `build` artifacts.
- `.env` or secrets.
- Runtime data.
- Device credentials.
- DB migrations.
- EDGE/LINK commands.
- Install/rollback scripts.
- Production activation.

## Offline Demo Hand-off Scope

The hand-off material is designed for Customer, Engineer, Admin, and Operator review of the read-only demo flow. It provides the files to review, the commands an engineer may run locally, and the guardrails customers should understand before production planning.

## Release Linkage

- R1-R3 release chain linkage: PASS.
- R2F evidence pack linkage: PASS.
- R3 customer preview linkage: PASS.
- Visual style: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.

## Boundary Summary

- Production activation: `NOT EXECUTED`.
- Device control: `NOT EXECUTED`.
- DB migration/write: `NOT EXECUTED`.
- Runtime activation: `NOT EXECUTED`.
- EDGE/LINK command execution: `NOT EXECUTED`.
- Auth/RBAC mutation: `NOT EXECUTED`.
- Install/rollback: `NOT EXECUTED`.
- No Direct Device Control.
- No Runtime Activation.
- No DB Write.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.
- No runnable production package generated.
- No dist/build committed.
- No .env/secrets committed.

Future control path, not executed in R4:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`
