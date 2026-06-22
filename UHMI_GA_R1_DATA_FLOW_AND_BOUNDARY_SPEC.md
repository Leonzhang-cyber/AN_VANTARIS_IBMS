# UHMI-GA-R1 Data Flow And Boundary Spec

## Product Scope

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is not an independent HMI server and not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only.

## R1 Read-only Data Flow

```text
Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI
```

UHMI consumes approved read-only state from CODE-facing APIs and UConsole workspace surfaces. UHMI does not talk directly to device systems, EDGE command paths, LINK command paths, DB write paths, or NEXUS AI execution.

## Forbidden Direct Paths

- UHMI -> Device
- UHMI -> DB write
- UHMI -> EDGE command
- UHMI -> LINK command
- UHMI -> NEXUS AI execution
- UHMI -> bypass CODE

## Future Controlled Action Path

```text
UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device
```

Future controlled action path is NOT EXECUTED in R1. It requires explicit future task approval, RBAC, policy safety, CODE boundary enforcement, UCDE evidence record, audit log, rollback plan, and two-person approval.

## Boundary Decision

- Read-only: PASS.
- Direct device control: NOT EXECUTED.
- Direct DB write: NOT EXECUTED.
- Bypass CODE: NOT EXECUTED.
- Runtime activation: NOT EXECUTED.

PASS marker: `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`
