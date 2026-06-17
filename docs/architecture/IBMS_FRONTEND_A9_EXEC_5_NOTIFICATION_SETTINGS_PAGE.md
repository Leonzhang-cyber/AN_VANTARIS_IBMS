# IBMS FRONTEND-A9-EXEC-5 — Notification Settings Page

**Task:** FRONTEND-A9-EXEC-5  
**Status:** Complete (sanitized placeholder migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the fifth System batch page from raw `NotificationSettings.vue` into a **sanitized** `NotificationSettingsView` — a notification channel configuration placeholder without calling a non-existent backend API.

In scope:

- Channel table preview (Email, SMS, Teams, Slack, Webhook)
- Disabled switches and Save/Test actions
- Route `/system/notification-settings`
- System overview card → Available + API pending
- Static menu entry

Out of scope:

- Raw page/CSS/asset copy
- Webhook secrets or real channel credentials
- npm install/build/dev

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/NotificationSettings.vue` |

Static scan of `AN_VANTARIS_IBMS-backend/src/api` and `contracts/openapi` found **no** dedicated notification settings route.

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw Vue + live channel config | Element Plus card, alert, table, form |
| Backend notification API | **None** — API/contract pending |
| Webhook URLs/secrets in UI | **None** — no secrets displayed |
| Copied assets | Scoped minimal CSS only |

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/NotificationSettingsView.vue` | New placeholder page |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Route registration |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | Menu child entry |
| `AN_VANTARIS_IBMS-frontend/src/modules/system/SystemOverviewView.vue` | Notification → Available + API pending |

---

## Route added

| Path | Component | Meta |
|---|---|---|
| `/system/notification-settings` | `NotificationSettingsView` | `requiresAuth: true`, `permissions: ['system:read']`, `layout: true` |

---

## API behavior

**API pending** — no notification configuration endpoint in current contracts or Flask `@route` scan.

The page:

- Does **not** call HTTP APIs
- Does **not** use direct axios
- Shows disabled channel switches and disabled Save/Test buttons labeled **Pending backend API**

Future: wire to `GET/PUT /system/notification-settings` (or equivalent) when CONTRACTS + backend define the route.

---

## Local placeholder rule

Every channel row includes `source: "Local placeholder / API pending"`. Status is `Not configured`. No webhook URLs, tokens, or SMTP credentials are shown.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**`
- `AN_VANTARIS_IBMS-backend/**`
- Domain API modules

---

## Next page candidates (A9 batch)

1. IntegrationSettings → `/system/integration-settings` (EXEC-6)  
2. User Settings (non-system module)  
3. Wire notification API when backend contract exists  

Completed: Permission Management, System Settings, System Overview, Audit Logs, Notification Settings (placeholder).
