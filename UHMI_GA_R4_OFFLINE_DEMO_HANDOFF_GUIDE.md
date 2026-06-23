# UHMI-GA-R4 Offline Demo Hand-off Guide

PASS marker: `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`

## Audience

Offline Demo Hand-off recipients:

- Customer
- Engineer
- Admin
- Operator

## Preparation

- Confirm the hand-off is a Customer Preview Export Package.
- Confirm the package type is `MANIFEST_EVIDENCE_RUNBOOK_ONLY`.
- Confirm no runnable production package generated.
- Confirm no dist/build committed.
- Confirm no .env/secrets committed.
- Confirm visual style: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.
- Confirm UHMI remains UConsole-owned.
- Confirm UHMI is not HMI Server.
- Confirm UHMI is not SCADA replacement.

## Demo Path

Use the R3 demo flow as the primary path:

- Open UConsole.
- Open UHMI Workspace.
- Show overview cards, system panels, device table, mimic preview, event context, evidence context, role-based views, disabled actions, guardrails, future control path, and R2F evidence pack.

Every step is read-only, view-only, and demo-only.

## Read-only Boundary

No Direct Device Control. No Runtime Activation. No DB Write. No EDGE Command Execution. No LINK Command Execution. No auth / login / JWT / RBAC mutation.

Production activation: `NOT EXECUTED`. Install/rollback: `NOT EXECUTED`.

## Hand-off File List

- `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_INDEX.md`
- `UHMI_GA_R4_OFFLINE_DEMO_HANDOFF_GUIDE.md`
- `UHMI_GA_R4_ENGINEER_DEMO_RUNBOOK.md`
- `UHMI_GA_R4_CUSTOMER_DEMO_ACCEPTANCE_HANDOVER.md`
- `UHMI_GA_R4_EXPORT_SCOPE_AND_EXCLUSION_MATRIX.md`
- `UHMI_GA_R4_REPORT.md`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-export-manifest.txt`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-release-chain.txt`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-handoff-files.txt`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-validator-results.txt`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r4/uhmi-r4-exclusion-evidence.txt`

## Forbidden Items

- Do not install.
- Do not deploy.
- Do not run DB migration.
- Do not activate runtime.
- Do not call devices.
- Do not call EDGE/LINK commands.
- Do not mutate auth/login/JWT/RBAC.
- Do not generate a runnable package.
- Do not commit `dist`, `build`, `.env`, or secrets.

## Customer Observation Points

- Customer can observe read-only workspace flow.
- Customer can observe role views.
- Customer can observe evidence links.
- Customer can observe disabled actions and future-only control path.
- Customer must not interpret the preview as production activation.

## Engineer Review Commands

Suggested local read-only verification commands are listed in `UHMI_GA_R4_ENGINEER_DEMO_RUNBOOK.md`.

R2F evidence pack reference:

- `UHMI_GA_R2F_EVIDENCE_PACK.md`

R3 demo flow reference:

- `UHMI_GA_R3_DEMO_READY_WORKSPACE_FLOW.md`

`UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`
