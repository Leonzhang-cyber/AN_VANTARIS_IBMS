# UHMI-GA-R2D Workspace Visual Polish Light Console Style

PASS marker: `UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS`

## Scope

R2D is based on UHMI-GA-R2C. R2D is Workspace Visual Polish + Light Console Style Freeze for the UHMI Workspace.

UHMI = Unified Human-Machine Interface. UHMI belongs to UConsole capability and remains part of UConsole Workspace. VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system.

The active visual style is frozen as `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.

## Active Light Console Style

The style source is the current UFMS / VANTARIS light enterprise operations console, not a deep-blue visual theme. R2D freezes:

- light app shell
- white rounded cards
- soft shadow
- pale mint background
- teal primary accent
- green-teal action color
- pill tabs
- light sidebar alignment
- pastel icon blocks
- soft status badges
- clean table layout
- compact enterprise operations density

## Boundary

R2D does not create a dark operations dashboard, independent HMI server infrastructure, device control, DB write, runtime activation, EDGE command execution, LINK command execution, authentication change, login change, JWT change, production RBAC change, real permission write, or package state mutation.

All visible actions remain read-only, disabled, or future-only.

Future control must go through:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

`UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS`

