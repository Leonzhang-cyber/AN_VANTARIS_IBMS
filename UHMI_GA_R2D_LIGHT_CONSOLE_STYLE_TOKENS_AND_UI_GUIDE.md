# UHMI-GA-R2D Light Console Style Tokens And UI Guide

PASS marker: `UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS`

## Foundation

R2D is based on UHMI-GA-R2C and freezes visual polish only. It does not change business logic, real authentication, real RBAC, database state, runtime state, device state, EDGE command state, LINK command state, NEXUS AI runtime, or CODE runtime action.

visualStyle: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`

## Style Tokens

- light app shell
- white rounded cards
- soft shadow
- pale mint background
- teal primary accent
- green-teal action color
- subtle mint / cyan accents
- pill tabs
- light sidebar alignment
- selected menu item with white background and teal accent
- top bar style compatible with existing UFMS layout
- pastel icon blocks
- soft status badges
- clean table layout
- compact enterprise operations density

## Styled Components

- UHMI Workspace Header
- Overview Metric Cards
- L3 Pill Tabs
- System Context Cards
- Device Context Table
- Mimic Panel Preview Cards
- Event Context Cards
- Evidence Context Cards
- Role Selector
- Role Visibility Matrix
- Disabled Actions Panel
- Guardrails Panel
- Future Control Path Panel

## Status Semantics

- Healthy / Success = green or mint
- Warning = amber / orange
- Critical = red
- Info = blue / cyan
- Disabled / Locked = gray
- Read-only = teal / slate / light blue-gray

Forbidden visual patterns are tracked in the registry as disallowed patterns for QA, not as active design requirements.

`UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS`

