# UHMI-GA-R2A UConsole Menu Information Architecture

PASS marker: `UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is not an independent HMI server and not a SCADA replacement.

## Sidebar Contract

The sidebar exposes L1/L2 only:

- L1: UConsole
- L2: UHMI Workspace

The sidebar must not expose UHMI L3 items directly. L3 views render inside the UHMI Workspace page through tabs and matching direct routes.

## UHMI Workspace L3 Views

- HMI Overview
- System HMI
- Device HMI
- Alarm & Event HMI
- EDGE / LINK Diagnostics
- Evidence & Reports

## Route Contract

- `/one/uhmi/overview`
- `/one/uhmi/system`
- `/one/uhmi/device`
- `/one/uhmi/alarms-events`
- `/one/uhmi/edge-link-diagnostics`
- `/one/uhmi/evidence-reports`

All routes use `platform:read` permission metadata and the common authenticated UConsole layout.

Production UI must not use Mock/Demo/Pilot/Coming soon labels.

`UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

