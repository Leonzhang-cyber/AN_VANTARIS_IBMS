# UHMI-GA-R2B Workspace Panels And System Context

PASS marker: `UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS`

## Scope

R2B is based on UHMI-GA-R2A. UHMI = Unified Human-Machine Interface. UHMI belongs to UConsole capability and remains part of UConsole Workspace even when UHMI Workspace appears as a high-frequency L1 entry.

VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system. UHMI is not independent HMI server infrastructure, not SCADA, and not a control runtime.

R2B adds Workspace Panels and System Context Panels on top of the R2A full UConsole menu IA, routes, GET-only API, and UHMI Workspace skeleton.

## Visual Style

visualStyle: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`

R2B continues the VANTARIS light enterprise operations console style:

- light app shell
- white / off-white rounded cards
- soft shadows
- light gray / pale mint background
- teal / green-teal primary action color
- pill tabs
- light sidebar
- selected menu item with white background and teal accent
- top bar with time chip and user chip
- metric cards with pastel icon blocks
- soft status cards
- clean table-heavy operations layout
- compact enterprise operations density

## Panels

R2B freezes these read-only UHMI Workspace L3 panels:

- Overview
- System Panels
- Device Panels
- Mimic Panels
- Status View
- Event Context
- Evidence Context
- Guardrails
- Future Control Path

## Safety

R2B remains read-only. It does not perform device control, DB write, runtime activation, EDGE command execution, LINK command execution, install, rollback, external API call, real device scan, or CODE runtime action.

Future control must go through:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

That path is documented only and not executable in R2B.

`UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS`

