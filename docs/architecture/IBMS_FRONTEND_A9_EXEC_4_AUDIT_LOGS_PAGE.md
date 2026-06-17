# IBMS FRONTEND-A9-EXEC-4 — Audit Logs Page

**Task:** FRONTEND-A9-EXEC-4  
**Status:** Complete (sanitized placeholder migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the fourth System batch page from raw `AuditLogs.vue` into a **sanitized** `AuditLogsView` — a read-only audit visualization placeholder without calling a non-existent backend API.

In scope:

- Filter UI preview (keyword, severity, date range)
- Placeholder table rows clearly labeled
- Route `/system/audit-logs` with `audit:read` meta
- System overview card updated to Available + API pending tag
- Static menu entry

Out of scope:

- Raw page/CSS/asset copy
- Fictional API integration
- npm install/build/dev

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/AuditLogs.vue` |

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw Vue + live audit feed | Element Plus card, alert, filters, table |
| Backend audit API calls | **None** — contract/backend audit route not confirmed |
| Copied assets | Scoped minimal CSS only |

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/AuditLogsView.vue` | New placeholder page |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Route registration |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | Menu child entry |
| `AN_VANTARIS_IBMS-frontend/src/modules/system/SystemOverviewView.vue` | Audit Logs → Available + API pending |

---

## Route added

| Path | Component | Meta |
|---|---|---|
| `/system/audit-logs` | `AuditLogsView` | `requiresAuth: true`, `permissions: ['audit:read']`, `layout: true` |

---

## API behavior

**API pending** — static scan of `AN_VANTARIS_IBMS-backend/src/api` and `contracts/openapi` found no dedicated audit log query route (only trace/audit utilities in other modules).

The page:

- Does **not** call HTTP APIs
- Does **not** use direct axios
- Shows disabled filters and a disabled Search button

When a contract route such as `GET /system/audit-logs` is added in a future batch, this view can be wired to a domain API module.

---

## Local placeholder rule

All table rows use `source: "Local placeholder / API pending"`. Timestamps and actors are static placeholder strings — not real operational data. `el-empty` reinforces that no backend feed is connected.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**`
- `AN_VANTARIS_IBMS-backend/**`
- Domain API modules (no audit API exists)

---

## Next page candidates (A9 batch)

1. NotificationSettings → `/system/notification-settings`  
2. IntegrationSettings → `/system/integration-settings`  
3. User Settings (non-system)  

Completed: Permission Management, System Settings, System Overview, Audit Logs (placeholder).

Future: wire audit view when CONTRACTS + backend define audit query API.
