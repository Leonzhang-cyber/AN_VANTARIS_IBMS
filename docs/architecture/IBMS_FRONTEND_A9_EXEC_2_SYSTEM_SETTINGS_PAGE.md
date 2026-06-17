# IBMS FRONTEND-A9-EXEC-2 — System Settings Page

**Task:** FRONTEND-A9-EXEC-2  
**Status:** Complete (sanitized migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the second System batch page from raw `SystemSettings.vue` into a **sanitized** `SystemSettingsView` — a read-only configuration preview using Element Plus and existing frontend env/menu modules.

In scope:

- Read-only display of application name, API base URL, debug flag, menu mode, permission enforcement note
- Route `/system/settings` with auth meta
- Static menu fallback entry
- Architecture and security notes

Out of scope:

- Raw page/CSS/asset copy
- Backend configuration write API
- npm install/build/dev
- Persistent settings persistence

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/SystemSettings.vue` |
| Env template | `AN_VANTARIS_IBMS-frontend/.env.example` |
| Menu probe | `services/api/menu.ts` → `GET /system/menus` |

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw Vue + legacy styles | Element Plus `el-card`, `el-form`, `el-switch`, `el-select`, `el-alert` |
| Full settings CRUD | Read-only preview + disabled save button |
| Direct axios | `menuApi.getMenus()` for menu mode probe only; base URL via `resolveBaseUrl()` |
| Copied assets | Scoped minimal CSS only |

Save action shows **“Pending backend configuration API”** and remains disabled — no fictional write endpoints.

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/SystemSettingsView.vue` | New sanitized page |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Route registration |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | Fallback menu item |

`system.ts` unchanged — no suitable read-only system config endpoint exists yet.

---

## Route added

| Path | Component | Meta |
|---|---|---|
| `/system/settings` | `SystemSettingsView` | `requiresAuth: true`, `permissions: ['system:read']`, `layout: true` |

---

## API behavior

| Field | Source | Writable |
|---|---|---|
| Application Name | `import.meta.env.VITE_IBMS_APP_NAME` | No |
| API Base URL | `resolveBaseUrl()` / env | No |
| Debug Enabled | `VITE_IBMS_ENABLE_DEBUG` | No |
| Menu Mode | `menuApi.getMenus()` probe → dynamic or fallback | No |
| Permission Enforcement | Static label `backend-controlled` | No |

No write API calls. Menu probe uses existing domain module (not direct axios).

---

## Pending backend config API

Future work should add a backend-sourced settings resource (e.g. `GET/PUT /system/settings`) with:

- Server-authoritative values
- `system:admin` write enforcement
- Audit logging for changes

Until then, this page is a **configuration center placeholder** for operators and developers.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**`
- `AN_VANTARIS_IBMS-backend/**`
- `system.ts` (no new methods)
- Other System module pages

---

## Next page candidates (A9 batch)

1. System (admin overview)  
2. Settings (user settings)  
3. AuditLogs  
4. NotificationSettings  
5. IntegrationSettings  

Completed: Permission Management (EXEC-1), System Settings (EXEC-2).
