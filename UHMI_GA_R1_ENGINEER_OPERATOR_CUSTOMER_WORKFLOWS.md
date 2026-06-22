# UHMI-GA-R1 Engineer Operator Customer Workflows

## Product Scope

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is not an independent HMI server and not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only.

## Operator Workflow

Operators use UHMI read-only views to inspect HMI overview status, system HMI panels, device HMI cards, alarm/event HMI context, and evidence/report links. Operators do not control devices from UHMI in R1.

## Engineer Workflow

Engineers use UHMI read-only views to inspect EDGE / LINK diagnostics, source-system mapping context, HMI locator context, integration health, and evidence references. Engineers do not issue EDGE command or LINK command actions from UHMI in R1.

## Customer Workflow

Customers use UHMI read-only workspace views for delivery review, acceptance evidence, exported reports, and visible package state. Customer access does not include device control, DB writes, runtime activation, or policy bypass.

## Supervisor/Admin Workflow

Supervisors and admins use UHMI read-only governance context to inspect entitlement, visibility, approval state, audit posture, and future-control readiness. Approval workflows are represented as future guardrails only in R1.

## R1 Safety

No install executed. No rollback executed. No DB migration executed. No runtime activation executed. No device control executed. No production activation executed.

PASS marker: `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`
