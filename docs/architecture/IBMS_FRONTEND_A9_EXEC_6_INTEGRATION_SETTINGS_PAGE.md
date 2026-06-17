# IBMS FRONTEND-A9-EXEC-6 — Integration Settings Page

**Task:** FRONTEND-A9-EXEC-6  
**Status:** Complete (sanitized placeholder migration)  
**Parent plan:** `IBMS_FRONTEND_A9_SYSTEM_PREP.md`

---

## Task scope

Migrate the sixth System batch page from raw `IntegrationSettings.vue` into a **sanitized** `IntegrationSettingsView` — an external integration configuration placeholder without API keys, secrets, or live backend calls.

In scope:

- Integration table preview (EdgeLink, MQTT, Webhook, Email Gateway, External IBMS)
- Disabled switches and Save/Test actions
- Route `/system/integration-settings`
- System overview card → Available + API pending
- Static menu entry

Out of scope:

- Raw page/CSS/asset copy
- API keys, tokens, or connector secrets in UI
- npm install/build/dev

---

## Raw source reference

Read-only reference (not copied):

| Item | Location |
|---|---|
| Legacy page | `AN_VANTARIS_IBMS-ibms_front/src/.../Administration/IntegrationSettings.vue` |

Static scan of `AN_VANTARIS_IBMS-backend/src/api` and `contracts/openapi` found **no** dedicated integration settings route.

---

## Sanitized migration decision

| Legacy | Target |
|---|---|
| Raw Vue + live connector config | Element Plus card, alert, table, form |
| Backend integration API | **None** — API/contract pending |
| API keys/secrets in forms | **Explicitly excluded** |
| Copied assets | Scoped minimal CSS only |

---

## Files changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-frontend/src/modules/system/IntegrationSettingsView.vue` | New placeholder page |
| `AN_VANTARIS_IBMS-frontend/src/router/routes.ts` | Route registration |
| `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts` | Menu child entry |
| `AN_VANTARIS_IBMS-frontend/src/modules/system/SystemOverviewView.vue` | Integration → Available + API pending |

---

## Route added

| Path | Component | Meta |
|---|---|---|
| `/system/integration-settings` | `IntegrationSettingsView` | `requiresAuth: true`, `permissions: ['system:read']`, `layout: true` |

---

## API behavior

**API pending** — no integration configuration endpoint in current contracts or Flask scan.

The page:

- Does **not** call HTTP APIs
- Does **not** use direct axios
- Does **not** display API keys or secrets
- Shows disabled switches and Save/Test labeled **Pending backend API**

---

## Local placeholder rule

Each integration row tags `source: "Local placeholder / API pending"`. Status is `Not configured`. No credentials, broker URLs, or API keys are rendered.

---

## Not changed

- `AN_VANTARIS_IBMS-ibms_front/**`
- `AN_VANTARIS_IBMS-backend/**`
- Domain API modules

---

## Next page candidates

1. **A9 batch complete** for planned System admin pages (7/7 shell or placeholder)  
2. User Settings (separate module)  
3. **CONTRACTS-NOTIFY-1 / CONTRACTS-INTEG-1** — define backend OpenAPI for notification/integration settings  
4. Wire placeholder pages when APIs exist  
5. **npm-smoke-1** — first frontend dev smoke when allowed  

System batch pages migrated: Permission Management (live CRUD), System Settings, System Overview, Audit Logs, Notification Settings, Integration Settings (placeholders where no API).
