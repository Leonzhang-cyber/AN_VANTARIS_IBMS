# IBMS FRONTEND-A9-EXEC-3 — System Overview Page

**Task:** FRONTEND-A9-EXEC-3  
**Status:** Complete (sanitized migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the third System batch page — admin overview hub — from raw `Administration/System.vue` into a **sanitized** `SystemOverviewView` that links to migrated and pending System submodules.

In scope:

- Module entry cards with status and permission hints
- Route `/system` as System module landing page
- Nested static menu under System
- Architecture and security notes

Out of scope:

- Raw page/CSS/asset copy
- API calls (navigation only)
- Pending submodule implementations

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/System.vue` |
| Prior migrations | `PermissionListView`, `SystemSettingsView` |

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw dashboard tiles | Element Plus `el-row` / `el-col` / `el-card` grid |
| Deep-linked admin sections | Router navigation to `/system/*` paths |
| Live config/API calls | No API — static module metadata only |
| Copied assets | Scoped minimal CSS |

Available modules navigate via `router.push`. Pending modules show disabled buttons.

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/SystemOverviewView.vue` | New overview hub |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | `/system` → `SystemOverviewView` |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | System submenu with children |

---

## Route added/updated

| Path | Component | Change |
|---|---|---|
| `/system` | `SystemOverviewView` | **Updated** from placeholder; meta `permissions: ['system:read']` |
| `/system/permissions` | `PermissionListView` | Unchanged |
| `/system/settings` | `SystemSettingsView` | Unchanged |

---

## Menu behavior

Static fallback menu nests System children:

- System Overview → `/system`
- Permission Management → `/system/permissions`
- System Settings → `/system/settings`

`AppLayout` renders `el-sub-menu` when `children` is present.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**`
- `AN_VANTARIS_IBMS-backend/**`
- `system.ts` and other API modules
- npm scripts / lockfiles

---

## Next page candidates (A9 batch)

1. AuditLogs → `/system/audit-logs`  
2. NotificationSettings → `/system/notification-settings`  
3. IntegrationSettings → `/system/integration-settings`  
4. Settings (user-level) — separate from System Settings  

Completed: Permission Management (EXEC-1), System Settings (EXEC-2), System Overview (EXEC-3).
