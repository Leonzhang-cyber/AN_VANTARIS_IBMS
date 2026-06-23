# UHMI Read-only Workspace Release Index

PASS marker: `UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX_PASS`

## Scope

UHMI-GA-R2F is the final read-only workspace release index and evidence pack for the UHMI chain from UHMI-GA-R1 through UHMI-GA-R2E.

UHMI = Unified Human-Machine Interface. VANTARIS ONE is a cross-industry unified operations platform, not an airport-only system. UHMI belongs to UConsole and may appear as an L1 high-frequency entry, while remaining owned by the UConsole Workspace. UHMI is not HMI Server. UHMI is not SCADA replacement.

Current HEAD baseline before R2F:

`6bd6bbaa0e23eee6676e170d2493d093084216a5`

R2F does not add business functionality, UI functionality, runtime ability, control ability, production activation, package mutation, install, rollback, DB migration, device control, EDGE command execution, LINK command execution, auth mutation, login mutation, JWT mutation, or RBAC mutation.

## Release Chain

| Stage | Commit | Tag | Scope | Status | PASS Marker |
| --- | --- | --- | --- | --- | --- |
| UHMI-GA-R1 | `003f4f710cfd76130ff79275c8190ec6bbe7edc9` | `uhmi-ga-r1-uconsole-readonly-workspace-freeze-20260622` | Read-only UConsole Workspace Foundation | PASS | `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS` |
| UHMI-GA-R2A | `6d682fdd351e3ad51b27ce91f2dbf92c74da3323` | `uhmi-ga-r2a-full-uconsole-menu-ui-api-skeleton-freeze-20260622` | Full UConsole Menu IA + UI/API Skeleton | PASS | `UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS` |
| UHMI-GA-R2B | `3678150d55f2459def6fc7b423496acb62143ac4` | `uhmi-ga-r2b-workspace-panels-system-context-freeze-20260622` | Workspace Panels + System Context Panels | PASS | `UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS` |
| UHMI-GA-R2C | `0262d90efffbb4993215d44c35f7c4d26f6d762f` | `uhmi-ga-r2c-role-based-workspace-views-freeze-20260622` | Role-based Workspace Views | PASS | `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS` |
| UHMI-GA-R2D | `e6c94cefcc7aee336d4702bc377a554a549454eb` | `uhmi-ga-r2d-light-console-style-freeze-20260622` | Workspace Visual Polish + Light Console Style Freeze | PASS | `UHMI_GA_R2D_WORKSPACE_VISUAL_POLISH_LIGHT_CONSOLE_STYLE_PASS` |
| UHMI-GA-R2E | `6bd6bbaa0e23eee6676e170d2493d093084216a5` | `uhmi-ga-r2e-api-frontend-integration-audit-freeze-20260622` | Workspace API Consolidation + Frontend Integration Audit | PASS | `UHMI_GA_R2E_WORKSPACE_API_CONSOLIDATION_FRONTEND_INTEGRATION_AUDIT_PASS` |

## Delivery Summary

| Stage | Core Deliverables |
| --- | --- |
| UHMI-GA-R1 | Read-only foundation freeze, data flow and boundary spec, workflows, future guardrails, registry, validator. |
| UHMI-GA-R2A | UConsole menu IA, route/menu references, UI/API skeleton, read-only section endpoints, registry, validator. |
| UHMI-GA-R2B | Workspace panels, system/device/event/evidence context payloads, backend provider expansion, frontend workspace panels, registry, validator. |
| UHMI-GA-R2C | Role-based workspace views, visibility matrix, disabled action matrix, no real RBAC mutation, registry, validator. |
| UHMI-GA-R2D | `VANTARIS_LIGHT_OPERATIONS_CONSOLE` visual style freeze, light console tokens, visual guardrails, registry, validator. |
| UHMI-GA-R2E | Read-only API consolidation endpoint, frontend service typing, integration audit registry, validator. |

## Boundary Summary

- `visualStyle`: `VANTARIS_LIGHT_OPERATIONS_CONSOLE`
- `mode`: `read_only`
- Full customer production activation: `NOT EXECUTED`
- Runtime/device/control/DB/auth mutation: `NOT EXECUTED`
- No Direct Device Control
- No Runtime Activation
- No DB Write
- No EDGE Command Execution
- No LINK Command Execution
- No auth / login / JWT / RBAC mutation

All future control must follow:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

## API / UI / Menu / Role / Style / Evidence Chain

- API chain: read-only UHMI endpoints remain GET-only and are indexed by the R2E integration audit endpoint.
- UI chain: UHMI Workspace remains a UConsole-owned read-only workspace.
- Menu chain: HMI Overview, System HMI, Device HMI, Alarm & Event HMI, EDGE / LINK Diagnostics, Evidence & Reports.
- Role chain: Customer, Engineer, Admin, and Operator views remain context-only with disabled actions and no real permission mutation.
- Style chain: R2D freezes `VANTARIS_LIGHT_OPERATIONS_CONSOLE`; R2F records it without adding UI capability.
- Evidence chain: R2F adds release index, evidence pack, readiness matrix, validator evidence, registry evidence, and tag/commit evidence.

`UHMI_GA_R2F_FINAL_READONLY_WORKSPACE_RELEASE_INDEX_PASS`
