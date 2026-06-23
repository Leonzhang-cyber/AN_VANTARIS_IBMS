# UHMI-GA-R2C Role Based Workspace Views

PASS marker: `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`

## Scope

R2C is based on UHMI-GA-R2B. UHMI = Unified Human-Machine Interface. UHMI belongs to UConsole capability and remains part of UConsole Workspace.

VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system. UHMI is not independent HMI server infrastructure, not SCADA, and not a control runtime.

R2C adds Customer / Engineer / Admin / Operator role-based workspace views as static role context only. It is not a real RBAC change.

## Role Views

- Customer: delivery status, acceptance checklist, system health summary, read-only UHMI panels, evidence records, reports snapshot.
- Engineer: package diagnostics, API health, EDGE / LINK health, DB readiness, offline verification, system context panels, device context table, guardrails.
- Admin: menu visibility matrix, package visibility, role matrix, workspace availability, locked modules, entitlement snapshot, guardrail policy summary.
- Operator: live operations summary, active events, device status, system panels, event context, shift handover snapshot, guardrails.

## Boundary

R2C is read-only. It does not perform device control, DB write, runtime activation, EDGE command execution, LINK command execution, install, rollback, authentication change, login change, JWT change, production RBAC change, real permission write, or package state mutation.

visualStyle: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`

Future control must go through:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`

