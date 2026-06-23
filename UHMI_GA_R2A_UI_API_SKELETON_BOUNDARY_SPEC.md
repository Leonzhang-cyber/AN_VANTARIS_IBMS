# UHMI-GA-R2A UI/API Skeleton Boundary Spec

PASS marker: `UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

UHMI = Unified Human-Machine Interface. UHMI is under UConsole / UHMI Workspace. It is read-only, not an independent HMI server, and not a SCADA replacement.

## API Skeleton

The UHMI API skeleton exposes GET-only routes:

- `GET /api/v1/one/uhmi/health`
- `GET /api/v1/one/uhmi/menu`
- `GET /api/v1/one/uhmi/sections`
- `GET /api/v1/one/uhmi/sections/<section_key>`

No POST, PUT, PATCH, DELETE, command, approval, mutation, database write, migration, runtime activation, or device-control endpoint is created.

## Data Flow

`Device/System -> EDGE -> LINK -> CODE -> UConsole/UHMI`

## Forbidden Direct Paths

- UHMI -> Device
- UHMI -> DB write
- UHMI -> EDGE command
- UHMI -> LINK command
- UHMI -> NEXUS AI execution
- UHMI -> bypass CODE

## Future Controlled Action Path

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

The future controlled action path is NOT EXECUTED in R2A.

## Guardrails

- No direct device control
- No direct DB write
- No bypass CODE
- No runtime activation
- No production activation
- No install or rollback
- No DB migration

`UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`

