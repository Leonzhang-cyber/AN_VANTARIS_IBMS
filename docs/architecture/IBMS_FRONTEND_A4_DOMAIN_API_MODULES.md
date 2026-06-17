# VANTARIS IBMS Frontend A4 Domain API Modules

## 1. Task Scope

- domain API module baseline only
- no raw `system_api.js` / `did_api.js` copied
- no backend connection tested
- no npm install/build/dev executed

---

## 2. Files Created

| File | Domain |
|---|---|
| `src/services/api/system.ts` | System permissions |
| `src/services/api/menu.ts` | Menu / versions |
| `src/services/api/did.ts` | DID auth + credentials |
| `src/services/api/iot.ts` | IoT device + ingest |
| `src/services/api/modeling.ts` | Modeling pipeline |
| `src/services/api/index.ts` | Barrel exports |

---

## 3. Domain API Modules

All modules use unified `request` client — no direct axios imports.

| Module | Functions |
|---|---|
| **system** | `getSystemPermissions`, `createSystemPermission`, `updateSystemPermission`, `deleteSystemPermission` |
| **menu** | `getMenuVersions`, `getMenus`, `getVersionMenus`, `createMenu`, `updateMenu`, `deleteMenu` |
| **did** | `login`, `getMe`, `createEntity`, `generateVp`, `reissueVc`, `revokeVc` |
| **iot** | `registerDevice`, `sendDeviceCommand`, `ingestHttp`, `getStandardFields`, `createStandardField` |
| **modeling** | `listCsv`, `trainModel`, `predict`, `predictFuture`, `getModelInfo` |

Types use `Record<string, unknown>` placeholders pending CONTRACTS-B1 schema binding.

---

## 4. Backend Route Mapping

| Frontend function | Backend route |
|---|---|
| `getSystemPermissions` | `GET /system/permissions` |
| `createSystemPermission` | `POST /system/permissions` |
| `updateSystemPermission` | `PUT /system/permissions/{id}` |
| `deleteSystemPermission` | `DELETE /system/permissions/{id}` |
| `getMenuVersions` | `GET /system/versions` |
| `getMenus` | `GET /system/menus` |
| `getVersionMenus` | `GET /system/version-menus/{version_code}` |
| `createMenu` | `POST /system/menus-add` |
| `updateMenu` | `PUT /system/menus-update/{id}` |
| `deleteMenu` | `DELETE /system/menus-delete/{id}` |
| `login` | `POST /did/login` |
| `getMe` | `GET /did/me` |
| `createEntity` | `POST /did/entity` |
| `generateVp` | `POST /did/vp/generate` |
| `reissueVc` | `POST /did/vc/reissue` |
| `revokeVc` | `POST /did/vc/revoke` |
| `registerDevice` | `POST /iot/device/register` |
| `sendDeviceCommand` | `POST /iot/device/{device_did}/command` |
| `ingestHttp` | `POST /iot/ingest/http` |
| `getStandardFields` | `GET /iot/standard-fields` |
| `createStandardField` | `POST /iot/standard-fields` |
| `listCsv` | `GET /modeling/csv/list` |
| `trainModel` | `POST /modeling/{device_code}/train` |
| `predict` | `POST /modeling/{device_code}/predict` |
| `predictFuture` | `POST /modeling/{device_code}/predict_future` |
| `getModelInfo` | `GET /modeling/{device_code}/model_info` |

---

## 5. Auth Behavior via Request Client

- Bearer token attached automatically when present (A1)
- 401 → `logoutLocal` + `/login` (A3)
- 403 → `/403` (A3)
- `login()` is public at backend — token should be stored by caller after success (A5)

---

## 6. Not Changed

- Raw frontend API modules
- Backend runtime
- Router / views (except service layer)

---

## 7. Next Tasks

- **CONTRACTS-B1** — frontend OpenAPI subset alignment
- **FRONTEND-A5** — login form wiring `didApi.login` + `setAccessToken`
- **FRONTEND-A6** — typed responses from OpenAPI schemas
- **FRONTEND-A7** — module view migration
