# UHMI-GA-R1 UConsole UHMI Workspace Read-only Foundation Freeze

## Definition

UHMI = Unified Human-Machine Interface. UHMI is placed under UConsole / UHMI Workspace. UHMI is not an independent HMI server. UHMI is not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only. Airport, data center, smart building / IBMS, utility, and facility are projections over the same platform foundation.

## R1 Decision

UHMI R1 is read-only. It provides a UConsole workspace for observing HMI-oriented operational context, system status, device summaries, alarm/event context, EDGE / LINK diagnostics, and evidence/report links. It does not execute control.

- UHMI foundation freeze: PASS.
- UHMI runtime activation: NOT EXECUTED.
- UHMI controlled action capability: NOT EXECUTED.
- UHMI production activation: NOT EXECUTED.

## Placement

UHMI belongs under UConsole / UHMI Workspace. It is a workspace surface inside the operator/engineer/admin/customer console, not a separate runtime tier.

## Read-only Boundaries

- No direct device control.
- No direct DB write.
- No bypass CODE.
- No EDGE command.
- No LINK command.
- No NEXUS AI execution.
- No runtime activation.

## Allowed R1 Capability

- Read-only HMI overview.
- Read-only system HMI status.
- Read-only device HMI cards.
- Read-only alarm and event HMI context.
- Read-only EDGE / LINK diagnostic visibility.
- Read-only evidence and reports links.

## Safety Statement

No install executed. No rollback executed. No DB migration executed. No runtime activation executed. No device control executed. No production activation executed. No push executed. No tag executed.

PASS marker: `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`
