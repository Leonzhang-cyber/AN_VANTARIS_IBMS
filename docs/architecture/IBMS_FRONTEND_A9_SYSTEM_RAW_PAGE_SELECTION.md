# VANTARIS IBMS Frontend A9 System Raw Page Selection

## 1. Task Scope

- selection only
- no raw source copied
- no target source changed
- no npm install/build/dev executed

Source: `AN_VANTARIS_IBMS-ibms_front/src/views/` (Administration, Settings)

---

## 2. Candidate Raw Pages

| Raw Path | Candidate Target | API Dependencies | UI Dependencies | Risk | Selected |
|---|---|---|---|---|---|
| `Administration/PermissionManagement.vue` | `modules/system/PermissionListView` | `systemApi.getSystemPermissions` | Element Plus table | Low — mock UI shell | **Yes** |
| `Administration/SystemSettings.vue` | `modules/system/SystemSettingsView` | None wired (static) | Element Plus form | Low | **Yes** |
| `Administration/System.vue` | `modules/system/SystemHubView` | None | Element Plus cards | Low | **Yes** |
| `Settings/Settings.vue` | `modules/system/SettingsIndexView` | None | Element Plus | Low | **Yes** |
| `Administration/AuditLogs.vue` | `modules/system/AuditLogsView` | None (mock) | Element Plus table | Low | **Yes** |
| `Administration/NotificationSettings.vue` | `modules/system/NotificationSettingsView` | None | Element Plus | Low | **Yes** |
| `Administration/IntegrationSettings.vue` | `modules/system/IntegrationSettingsView` | None | Element Plus | Medium — may embed URLs | **Yes** |
| `Administration/RoleManagement.vue` | `modules/system/RoleListView` | Future permissions API | Element Plus, large mock | Medium — 1175 lines, mock only | No (batch 2) |
| `Administration/UserManagement.vue` | `modules/system/UserListView` | No backend contract | Mock data | Medium | No (batch 2) |
| `Administration/EditionManagement.vue` | `modules/system/MenuVersionView` | `system_api` menus/versions | Element Plus, 1789 lines | **High** — size + API | No (batch 2) |
| `Administration/EditionManagement/MenuManagement.vue` | `modules/system/MenuEditorView` | `system_api` full menu CRUD | 2073 lines | **High** | **Excluded** |
| `Administration/TenantManagement.vue` | — | Unknown | Mock | Medium | No |
| `Administration/LicenseManagement.vue` | — | Unknown | Mock | Medium | No |

---

## 3. First Batch Selection

**7 pages selected** (within 5–10 limit):

1. `Administration/PermissionManagement.vue` — permissions list (wire `systemApi`)
2. `Administration/SystemSettings.vue` — simple system settings shell
3. `Administration/System.vue` — system module hub
4. `Settings/Settings.vue` — settings index
5. `Administration/AuditLogs.vue` — audit log table (mock → stub)
6. `Administration/NotificationSettings.vue` — notification prefs shell
7. `Administration/IntegrationSettings.vue` — integration settings (sanitize URLs on migrate)

**Deferred to batch 2:** RoleManagement, UserManagement, EditionManagement (menu/version UI).

---

## 4. Excluded Pages

| Reason | Examples |
|---|---|
| **Heavily charted / large** | RoleManagement (1175 lines), EditionManagement (1789), MenuManagement (2073) |
| **Unknown backend contract** | TenantManagement, LicenseManagement, OEMBranding |
| **Hardcoded API URLs** | DeveloperCenter sandbox pages (not in System batch) |
| **Menu/version complexity** | EditionManagement family — after A8 dynamic menu proven in runtime |

---

## 5. API Wiring Notes (raw)

Only **EditionManagement.vue** and **MenuManagement.vue** import `@/api/system_api` in Administration folder. Selected batch 1 pages are **UI shells** — migration rewrites to use `systemApi` / `menuApi` without copying raw API module.
