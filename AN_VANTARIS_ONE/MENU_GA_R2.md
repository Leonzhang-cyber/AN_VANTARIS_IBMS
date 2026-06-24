# MENU-GA-R2 Route Coverage and Sidebar/L3 Behavior Audit

PASS marker: ONE_MENU_GA_R2_ROUTE_COVERAGE_SIDEBAR_L3_BEHAVIOR_AUDIT_PASS

## Purpose

MENU-GA-R2 audits route coverage, Sidebar behavior, and L3 content-area behavior after the MENU-GA-R1 international GA menu baseline. This task is audit-only and does not mutate frontend implementation, backend implementation, routes, menu source, AppLayout, types, MENU-GA-R1 files, or SERVER-PRECHECK-R4 files.

## Relationship to MENU-GA-R1

MENU-GA-R1 freezes the architecture model: L1/L2 in the left Sidebar and L3 as content-area metadata. MENU-GA-R2 verifies that the current source still follows that baseline and that mapped/planned L2 routes are covered by existing route definitions.

## Audit-only Boundary

- frontendMutationAllowed: false.
- backendMutationAllowed: false.
- routeMutationAllowed: false.
- menuMutationAllowed: false.
- l3SidebarAllowed: false.
- sshResidueAllowed: false.
- No SSH, deployment, install, DB, auth/JWT/RBAC, secrets, EDGE/LINK runtime, POST/PUT/PATCH/DELETE API, or UI component creation.

## Route Coverage Checks

The validator extracts L1/L2 menu paths from `static-menu.ts` and route paths from `routes.ts`. Every L1/L2 menu path must match a route path unless explicitly listed as an exception. Current MENU-GA-R1 uses shared existing routes for mapped/planned pages, so duplicate path reuse is accepted only when listed in `routePathReuseExceptions`.

## Sidebar/L3 Behavior Checks

The validator checks that `static-menu.ts` contains `fallbackMenuItems` and `l3Items` metadata, that `types.ts` exposes `AppMenuL3Item`, and that `AppLayout.vue` contains the Sidebar collapse state plus content-area L3 row. L3 items must not be rendered as Sidebar child menu items.

## Duplicate ID / Path / Name Checks

- Duplicate menu IDs are not allowed.
- Duplicate L3 IDs within the same L2 are not allowed.
- Duplicate route paths are not allowed.
- Duplicate route names are not allowed.
- Duplicate menu path reuse is allowed only when the path is documented as a mapped/planned metadata route reuse exception.

## Forbidden Residue Checks

The validator rejects removed R4 / SSH route residue in `routes.ts`, including `ServerSshApprovalPacket`, `server-ssh-approval-packet`, `ssh-approval`, `SSH Approval Packet`, `R4 SSH`, and `SERVER_PRECHECK_R4`.

The validator rejects forbidden frontend labels: `Home` as an L1 label, `Mock`, unsupported standalone `Demo`, `MVP`, and `Coming soon`. Existing `Customer Demo` scenario/report labels are treated as frozen MENU-GA-R1 scenario coverage, not unsupported demo residue.

## Route Path Reuse Exceptions

These paths are intentionally reused by multiple L2 menu items as read-only mapped/planned metadata entries:

- `/dashboard`
- `/console/operations`
- `/assets/topology`
- `/one/airport/alarms-events`
- `/one/airport/fault-cases`
- `/one/umms/workspace`
- `/uesg/sustainability`
- `/reports`
- `/ucde/evidence`
- `/one/nexus-ai/branch-audit`
- `/one/assets/context`
- `/one/airport/assets-topology`
- `/one/airport/overview`
- `/uedge/setup`
- `/uedge/diagnostics`
- `/console/foundation-diagnostics/workspace`
- `/system`
- `/system/audit-logs`

## Acceptance Criteria

- Required MENU-GA-R2 document, registry, evidence, validation JSON, and validator exist.
- Registry flags are correct.
- Sidebar L1/L2 and L3 content-area metadata behavior is present.
- Route coverage has no missing paths outside documented exceptions.
- Duplicate IDs and duplicate route definitions are absent.
- Forbidden R4 / SSH route residue is absent.
- No frontend/backend/routes/static-menu/types/AppLayout mutation is included in this task.

## Final PASS Marker

ONE_MENU_GA_R2_ROUTE_COVERAGE_SIDEBAR_L3_BEHAVIOR_AUDIT_PASS
