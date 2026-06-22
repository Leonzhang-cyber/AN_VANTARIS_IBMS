# UHMI-GA-R1 Control Capability Future Guardrails

## Product Scope

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is not an independent HMI server and not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only.

## R1 Control Decision

UHMI R1 is read-only. Future controlled actions are explicitly NOT EXECUTED in R1.

## Future Guardrails

Any future controlled UHMI action requires:

- RBAC.
- Approval workflow.
- Policy safety.
- CODE boundary.
- UCDE evidence record.
- Audit log.
- Rollback plan.
- Two-person approval.
- Explicit customer production activation approval.
- EDGE / LINK command eligibility validation.

## Future Controlled Action Path

```text
UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device
```

This path is documented only. It is NOT EXECUTED in R1.

## Forbidden R1 Actions

- Direct device control.
- Direct DB write.
- Bypass CODE.
- EDGE command.
- LINK command.
- NEXUS AI execution.
- Runtime activation.

PASS marker: `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`
