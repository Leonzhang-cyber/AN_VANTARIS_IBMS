# VANTARIS IBMS Frontend A9 System First Batch Plan

## 1. Task Scope

- first batch plan only
- no page migration
- no raw source copied

---

## 2. Prerequisites

| Prerequisite | Status |
|---|---|
| Request/auth baseline (A1) | ✅ |
| Router auth guard (A2) | ✅ |
| Domain API modules (A4) | ✅ |
| Frontend OpenAPI contract (B1) | ✅ |
| Dynamic menu baseline (A8) | ✅ |
| npm install + dev smoke | ⏳ future |

---

## 3. Target Module

```
AN_VANTARIS_IBMS-frontend/src/modules/system/
```

Register routes under `/system/*` with `meta.requiresAuth: true`.

---

## 4. First Batch Pages

| Order | Target Page | Raw Source | Route | Required API | Permission |
|---|---|---|---|---|---|
| 1 | `PermissionListView.vue` | `Administration/PermissionManagement.vue` | `/system/permissions` | `getSystemPermissions`, CRUD | JWT + system perms TBD |
| 2 | `SystemHubView.vue` | `Administration/System.vue` | `/system` | — | JWT |
| 3 | `SystemSettingsView.vue` | `Administration/SystemSettings.vue` | `/system/settings` | — (phase 1) | JWT |
| 4 | `SettingsIndexView.vue` | `Settings/Settings.vue` | `/system/settings/index` | — | JWT |
| 5 | `AuditLogsView.vue` | `Administration/AuditLogs.vue` | `/system/audit-logs` | Future audit API | JWT |
| 6 | `NotificationSettingsView.vue` | `Administration/NotificationSettings.vue` | `/system/notifications` | — | JWT |
| 7 | `IntegrationSettingsView.vue` | `Administration/IntegrationSettings.vue` | `/system/integrations` | — | JWT |

**One page per commit** recommended during FRONTEND-A9-EXEC batch.

---

## 5. Migration Rules

- migrate **one page at a time**
- replace raw axios/`system_api.js` with `@/services/api/system` and `menu`
- remove hardcoded URLs (especially IntegrationSettings)
- preserve `meta.requiresAuth: true`
- no raw images/assets unless reviewed
- no secrets/tokens in migrated code
- strip mock loading theatrics unless needed for UX parity

---

## 6. Stop Conditions

- missing backend contract for page API calls
- hardcoded secret or production URL in raw diff
- unknown npm dependency required by page
- single page >500 lines after refactor — split first
- compile blocker requiring unapproved package (echarts, etc.)

---

## 7. Next Tasks

- **FRONTEND-A9-EXEC-1** — Migrate PermissionListView
- **FRONTEND-A9-EXEC-2** — Migrate SystemHubView
- **CONTRACTS-B2** — route validation (same batch)
- **FRONTEND-A10** — EditionManagement / menu version UI (batch 2)
