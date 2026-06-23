# UHMI-GA-R2A Full UConsole Menu IA + UHMI Workspace UI/API Skeleton

PASS marker: `UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

## Scope

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. UHMI is not an independent HMI server and not a SCADA replacement.

VANTARIS ONE is cross-industry and not airport-only. UHMI-GA-R2A implements a read-only UConsole menu IA plus UI/API skeleton for the UHMI Workspace.

R2A does not activate runtime behavior. It does not install packages, roll back packages, run database migration, write databases, execute device control, execute EDGE commands, execute LINK commands, execute NEXUS AI, or bypass CODE.

## Created UI/API Skeleton

- Backend provider: `AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py`
- Backend GET-only routes: `AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py`
- Frontend API service: `AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts`
- Frontend workspace page: `AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue`
- Frontend routes: `/one/uhmi/overview`, `/one/uhmi/system`, `/one/uhmi/device`, `/one/uhmi/alarms-events`, `/one/uhmi/edge-link-diagnostics`, `/one/uhmi/evidence-reports`

## Menu IA

Sidebar contains L1/L2 only:

- L1: UConsole
- L2: UHMI Workspace

L3 is inside the UHMI Workspace page:

- HMI Overview
- System HMI
- Device HMI
- Alarm & Event HMI
- EDGE / LINK Diagnostics
- Evidence & Reports

Production UI must not use Mock/Demo/Pilot/Coming soon labels.

## Boundary

Data flow:

`Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI`

Forbidden direct paths:

- UHMI -> Device
- UHMI -> DB write
- UHMI -> EDGE command
- UHMI -> LINK command
- UHMI -> NEXUS AI execution
- UHMI -> bypass CODE

Future controlled action path:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

Future controlled action path is NOT EXECUTED in R2A.

## PASS

`UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

