# UHMI-GA-R2C Customer Engineer Admin Operator Context Spec

PASS marker: `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`

## Foundation

R2C is based on UHMI-GA-R2B. UHMI = Unified Human-Machine Interface. UHMI is a UConsole Workspace capability.

R2C is static role context. It does not modify authentication / login / JWT / production RBAC. It does not introduce real permission interceptors or production authorization behavior changes.

## Role Contexts

Customer Context:

- Delivery Status
- Acceptance Checklist
- Evidence Records
- Reports Snapshot

Engineer Context:

- Package Diagnostics
- API Health
- EDGE / LINK Health
- DB Readiness
- Offline Verification

Admin Context:

- Menu Visibility
- Package Visibility
- Role Matrix
- Locked Modules
- Entitlement Snapshot

Operator Context:

- Live Operations
- Active Events
- Device Status
- Shift Handover
- Event Context

## Disabled Actions

- Device Control: Disabled
- Runtime Activation: Disabled
- DB Write: Disabled
- EDGE Command: Disabled
- LINK Command: Disabled
- RBAC Mutation: Disabled
- Package Enable/Disable: Disabled
- Install/Rollback: Disabled

## Guardrails

- Read-only Mode
- No Direct Device Control
- No Runtime Activation
- No DB Write
- No EDGE Command Execution
- No LINK Command Execution
- No RBAC Mutation
- No Package State Mutation
- Future Control Path: `UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`

