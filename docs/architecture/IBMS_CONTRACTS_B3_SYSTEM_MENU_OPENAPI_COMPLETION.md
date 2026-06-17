# IBMS CONTRACTS-B3 — System / Menu OpenAPI Completion

**Task:** CONTRACTS-B3  
**Status:** Complete (static contract update only)  
**Prior work:** CONTRACTS-B2 route validation tool

---

## Task scope

Close OpenAPI gaps for **system permissions** and **menu/version administration** routes identified by CONTRACTS-B2 static validation. Update both frontend-facing and protected OpenAPI drafts with consistent 401/403/500 semantics.

In scope:

- Permission CRUD paths
- Menu/version admin paths and Flask runtime aliases
- Contract alias paths (`/system/menu`, `/system/version/{version_id}/menus`, etc.)
- Documentation and README pointer

Out of scope:

- Backend or frontend runtime changes
- DID / IoT / modeling route completion
- Standard-fields / entity-types system routes (deferred)
- Live API verification

---

## Inputs from B2 validation

**Before B3** (commit `5309434`):

| Metric | Value |
|---|---|
| Flask routes (static) | 78 |
| OpenAPI paths (union) | 42 |
| Missing in OpenAPI | 39 |
| OpenAPI-only contract aliases | 3 (`/system/menu`, `/system/menu/{id}`, `/system/version/{version_id}/menus`) |

System/menu gaps included: permissions partial coverage, missing `versions/default`, `versions/switch`, `menu/init-data`, `menus/batch-sort`, version-menu batch/incremental/diff, and incomplete 403/500 on write routes.

**After B3** (this commit):

| Metric | Value |
|---|---|
| Flask routes (static) | 78 |
| OpenAPI paths (union) | 55 |
| Missing in OpenAPI | 32 |

System/menu Flask routes covered in OpenAPI except deferred admin surfaces (`entity-types`, `standard-fields`, `/system/test`). Contract alias paths remain OpenAPI-only by design (validator still lists them under “missing” when comparing literal Flask paths).

---

## Files changed

| File | Change |
|---|---|
| `contracts/openapi/ibms-frontend-api-v1.openapi.yaml` | Permissions GET-by-id, menu/version routes, ServerError component |
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | Full permission CRUD, runtime menu routes, contract aliases |
| `contracts/openapi/README.md` | B3 references and 403/500 notes |

---

## Routes completed

### System permissions

| Contract path | Methods | Runtime |
|---|---|---|
| `/system/permissions` | GET, POST | Exact Flask match |
| `/system/permissions/{id}` or `{perm_id}` | GET, PUT, DELETE | Exact Flask match (`perm_id`) |

### Menu / version (runtime paths)

| OpenAPI path | Methods | Flask source |
|---|---|---|
| `/system/versions` | GET, POST | `menu_api.py` |
| `/system/versions/default` | GET | `menu_api.py` |
| `/system/versions/{version_code}` | PUT, DELETE | `menu_api.py` |
| `/system/versions/switch/{version_code}` | PUT | `menu_api.py` |
| `/system/menus` | GET | `menu_api.py` |
| `/system/menus-add` | POST | `menu_api.py` |
| `/system/menus-update/{menu_id}` | PUT | `menu_api.py` |
| `/system/menus-delete/{menu_id}` | DELETE | `menu_api.py` |
| `/system/menus/batch-sort` | POST | `menu_api.py` |
| `/system/menu/active` | GET | `menu_api.py` |
| `/system/menu/config/{version_code}` | GET | `menu_api.py` |
| `/system/menu/init-data` | GET | `menu_api.py` |
| `/system/version-menus/{version_code}` | GET, POST | `menu_api.py` |
| `/system/version-menus/{version_code}/batch` | POST | `menu_api.py` |
| `/system/version-menus/{version_code}/incremental` | POST | `menu_api.py` |
| `/system/version-menus/{version_code}/diff` | POST | `menu_api.py` |

### Frontend contract aliases (path shape differs)

| Contract path | Runtime alias (`x-ibms-backend-route`) |
|---|---|
| `/system/menu` POST | `POST /system/menus-add` |
| `/system/menu/{id}` PUT/DELETE | `PUT/DELETE /system/menus-update|menus-delete/{id}` |
| `/system/versions/{version_id}` PUT/DELETE | `PUT/DELETE /system/versions/{version_code}` |
| `/system/version/{version_id}/menus` GET/POST | `GET/POST /system/version-menus/{version_code}` |
| `/system/version/{version_id}/menu/{menu_id}` PUT/DELETE | Pending exact runtime verification |
| `/system/menus/{id}` GET | Placeholder — no dedicated Flask GET-by-id |

---

## Runtime alias notes

Where Flask uses different path segments (`menus-add`, `menus-update`, `version_code` vs `version_id`), OpenAPI retains the **frontend contract path** and documents the Flask alias in `description` and `x-ibms-backend-route`.

Protected spec includes **both** runtime paths and contract aliases so SDK generators and validators can choose the appropriate surface.

---

## 401 / 403 rule

All system/menu protected operations:

- `bearerAuth` required
- `401 UnauthorizedError` on missing/invalid JWT
- `500 ServerError` on server failures

Write/delete (POST, PUT, DELETE):

- `403 ForbiddenError` with description:  
  *Authenticated user lacks required system permission. Runtime permission enforcement pending for menu routes if not yet applied.*

Frontend and protected OpenAPI specs use the same forbidden semantics for system/menu write routes.

---

## Pending exact runtime validation

- Contract-only paths (`/system/menus/{id}` GET, `/system/version/{version_id}/menu/{menu_id}`) need live route tests when backend service is available.
- Permission matrix (`system:admin`, `system:write`) not yet enforced on all menu mutations at runtime.
- Standard-fields and entity-types system routes remain out of this batch.
- Method-level diff (HTTP verb per path) — CONTRACTS-B4 candidate.

---

## Not changed

- `AN_VANTARIS_IBMS-backend/src/**`
- `AN_VANTARIS_IBMS-frontend/src/**`
- No services started, no npm, no DB
