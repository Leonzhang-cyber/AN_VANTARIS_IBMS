# IBMS FRONTEND-A9-EXEC-1 — Permission Management Page

**Task:** FRONTEND-A9-EXEC-1  
**Status:** Complete (sanitized migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the first System batch page from raw `PermissionManagement.vue` into the hardened target frontend as a **sanitized** `PermissionListView` using Element Plus and the domain `system.ts` API module.

In scope:

- List permissions on mount
- Create / update / delete UI with dialogs and confirmation
- Route `/system/permissions` with auth meta
- Static menu fallback entry
- Architecture and security notes

Out of scope:

- Raw page/CSS/asset copy
- Backend changes
- npm install/build/dev
- Full parity with legacy admin UX

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/PermissionManagement.vue` |
| Backend routes | `AN_VANTARIS_IBMS-backend/src/api/system/system_api.py` — `/system/permissions` CRUD |
| Contract | `contracts/openapi/ibms-frontend-api-v1.openapi.yaml` — `/system/permissions` |

Backend fields at runtime: `perm_code`, `description`, optional `extra` (display name stored in `extra.name` when provided).

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw Vue + legacy styles | Element Plus `el-card`, `el-table`, `el-dialog`, `el-form` |
| Direct axios / hardcoded URLs | `services/api/system.ts` via shared `request` client |
| Full admin shell | Minimal list + CRUD dialogs |
| Copied images/CSS | Scoped minimal layout CSS only |

Display **Name** column maps to `extra.name` when present, otherwise falls back to `perm_code`.

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/PermissionListView.vue` | New sanitized page |
| `AN_VANTARIS_IBMS-frontend/src/services/api/system.ts` | Typed CRUD + response normalization |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Route registration |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | Fallback menu item |

---

## Route added

| Path | Component | Meta |
|---|---|---|
| `/system/permissions` | `PermissionListView` | `requiresAuth: true`, `permissions: ['system:read']`, `layout: true` |

Frontend route permission is advisory; backend JWT and future `system:write` enforcement are authoritative.

---

## API mapping

| UI action | Domain method | HTTP |
|---|---|---|
| Load list | `getSystemPermissions()` | `GET /system/permissions` |
| Create | `createSystemPermission(payload)` | `POST /system/permissions` |
| Update | `updateSystemPermission(id, payload)` | `PUT /system/permissions/{id}` |
| Delete | `deleteSystemPermission(id)` | `DELETE /system/permissions/{id}` |

Payload types: `PermissionRecord`, `PermissionPayload`, `PermissionUpdatePayload`.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**` (raw source)
- `AN_VANTARIS_IBMS-backend/**`
- Other System placeholder routes
- npm scripts / lockfiles
- Real `.env` or secrets

---

## Next page candidates (A9 batch)

1. SystemSettings → sanitized settings view  
2. System (admin overview)  
3. Settings (user settings)  
4. AuditLogs  
5. NotificationSettings  
6. IntegrationSettings  

Defer: MenuManagement, EditionManagement, RoleManagement (large / high complexity).
