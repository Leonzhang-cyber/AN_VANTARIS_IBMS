# VANTARIS IBMS Contracts B1 Frontend API Subset

## 1. Task Scope

- frontend-facing OpenAPI subset only
- no backend runtime changed
- no frontend runtime changed in this commit
- no lint/test/install executed

Aligns with `AN_VANTARIS_IBMS-frontend/src/services/api/*` (FRONTEND-A4).

---

## 2. Files Changed

| File | Action |
|---|---|
| `contracts/openapi/ibms-frontend-api-v1.openapi.yaml` | **Created** |
| `contracts/openapi/README.md` | Updated index |
| `docs/architecture/IBMS_CONTRACTS_B1_FRONTEND_API_SUBSET.md` | **Created** |

---

## 3. Frontend-Facing API Groups

| Tag | Contract paths | Frontend module |
|---|---|---|
| **System** | `/system/permissions`, `/system/permissions/{id}` | `system.ts` |
| **Menu** | `/system/versions`, `/system/menus`, `/system/menu`, `/system/menu/{id}`, `/system/version/{version_id}/menus` | `menu.ts` |
| **DID** | `/did/login`, `/did/me`, `/did/entity`, `/did/vp/generate`, `/did/vc/reissue`, `/did/vc/revoke` | `did.ts` |
| **IoT** | `/iot/device/register`, `/iot/device/{device_did}/command`, `/iot/ingest/http`, `/iot/standard-fields` | `iot.ts` |
| **Modeling** | `/modeling/csv/list`, `/modeling/{device_code}/train`, `/predict`, `/predict_future`, `/model_info` | `modeling.ts` |

---

## 4. 401 / 403 Rule

| Response | When |
|---|---|
| **401** | Missing or invalid JWT on protected routes |
| **403** | Valid JWT but missing permission (`modeling:*`, `device:*`, `iot:*`, `did:*`) |
| **Menu routes** | JWT required (MENU-JWT); 403 marked **permission pending** until matrix applied |

Public exception: `POST /did/login` (no bearer required).

---

## 5. JWT / Menu Compatibility

- All menu contract operations require `bearerAuth` except none under menu group
- Frontend must obtain token via `/did/login` before menu/version calls
- Contract path `/system/version/{version_id}/menus` maps to backend `GET /system/version-menus/{version_code}`

---

## 6. Pending Validation

- [ ] Runtime response body schema validation vs Flask handlers
- [ ] Permission matrix `x-ibms-required-permission` per operation
- [ ] Contract test suite (CONTRACTS-B2)
- [ ] Align menu contract paths with optional backend alias routes

---

## 7. Next Tasks

- **CONTRACTS-B2** — contract validation / diff vs runtime routes
- **FRONTEND-A5** — login UI + token persistence
- **FRONTEND-A6** — typed responses from OpenAPI schemas
- **FRONTEND-A7** — module view migration plan
