# UHMI-GA-R1 UConsole Workspace Menu And Information Architecture

## Product Scope

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is not an independent HMI server and not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only.

## Menu Structure

UConsole / UHMI Workspace includes:

- HMI Overview
- System HMI
- Device HMI
- Alarm & Event HMI
- EDGE / LINK Diagnostics
- Evidence & Reports

## Navigation Rule

- Sidebar only L1/L2.
- L3 inside page as tabs, panels, drawers, tables, or workflow sections.
- UHMI must remain inside UConsole navigation and must not bypass CODE layer.

## Production UI Label Rule

Production UI must not use Mock/Demo/Pilot/Coming soon labels. Readiness or disabled states must be represented as read-only, not activated, locked, entitled, installed, enabled, visible, or approval required.

## Role Information Architecture

- Operator: read-only HMI overview, system status, device summaries, alarms/events, and evidence links.
- Engineer: read-only diagnostics, EDGE / LINK status, mapping context, and commissioning evidence.
- Customer: read-only delivery/status views and evidence/report exports.
- Supervisor/Admin: read-only governance, entitlement, visibility, and approval-state context.

PASS marker: `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`
