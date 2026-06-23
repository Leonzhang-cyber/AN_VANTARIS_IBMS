# UHMI-GA-R5 Customer Preview Sign-off Pack

PASS marker: `UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS`

## Customer Preview Package Summary

The UHMI customer preview package is ready for read-only customer preview and offline demo hand-off. The release decision is GO for `READ_ONLY_CUSTOMER_PREVIEW_OFFLINE_DEMO_HANDOFF`.

Production GA: NOT YET. Production Activation: NOT EXECUTED.

## Demo Route

- Open UConsole.
- Open UHMI Workspace.
- Show `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.
- Show overview metrics, system panels, device table, mimic preview, event context, evidence context, role views, disabled actions, guardrails, future path, R2F evidence pack, R3 preview package, and R4 hand-off.

## What Customer Can Validate

- UConsole-owned UHMI workspace.
- Read-only customer preview flow.
- Role context for Customer, Engineer, Admin, and Operator.
- Evidence chain from R1 through R4.
- Guardrails and exclusions.

## What Customer Cannot Treat As Production Activation

- Customer preview GO is not production GA.
- It is not production activation.
- It is not runtime control activation.
- It is not device control.
- It is not DB migration/write.
- It is not EDGE/LINK command execution.
- It is not auth/login/JWT/RBAC mutation.
- It is not a runnable production package.

## Acceptance Sign-off Checklist

- Customer preview readiness: PASS.
- Engineer demo readiness: PASS.
- Evidence readiness: PASS.
- Read-only safety: PASS.
- No Direct Device Control.
- No Runtime Activation.
- No DB Write.
- No EDGE Command Execution.
- No LINK Command Execution.
- No auth / login / JWT / RBAC mutation.
- No runnable production package.
- No dist/build committed.

## Required Sign-off Statements

- Decision: GO for customer preview only.
- Decision Scope: `READ_ONLY_CUSTOMER_PREVIEW_OFFLINE_DEMO_HANDOFF`.
- Production GA Decision: `NOT_YET`.
- Production Activation: `NOT_EXECUTED`.

## Next Step After Customer Preview

If customer preview is accepted, proceed to production planning only after the future production prerequisites are approved.

## Production Prerequisites

- production activation plan
- deployment environment verification
- DB migration plan
- runtime control policy gate
- approval workflow
- EDGE/LINK execution guard
- security acceptance
- customer UAT

UHMI remains UConsole-owned. UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R5_FINAL_CUSTOMER_PREVIEW_READINESS_DECISION_PASS`
