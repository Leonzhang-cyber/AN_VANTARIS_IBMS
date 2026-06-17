# IBMS CONTRACTS-B6 — System OpenAPI Completion

**Task:** CONTRACTS-B6  
**Status:** Complete (static contract update only)  
**Prior work:** CONTRACTS-B5 (DID/IoT gaps closed)

---

## Task scope

Close the remaining **17 method-level** OpenAPI gaps for System administration routes: entity-types, system standard-fields/methods (Flask runtime paths), and `/system/test` diagnostic endpoint.

Out of scope:

- Backend / frontend runtime changes
- Audit log API (not present in Flask)
- Live API verification

---

## Inputs from B4/B5 method validation

**Before B6** (commit `3fcecf4`):

| Metric | Value |
|---|---|
| Flask route-method pairs | 97 |
| OpenAPI operations (union) | 96 |
| Missing in OpenAPI | **17** (system admin only) |
| OpenAPI-only (contract aliases) | 9 |

**After B6** (this commit):

| Metric | Value |
|---|---|
| Flask route-method pairs | 97 |
| OpenAPI operations (union) | **113** |
| Missing in OpenAPI | **0** |
| OpenAPI-only | 9 (menu contract aliases — expected) |

All Flask-scanned route-methods now appear in OpenAPI union.

---

## Files changed

| File | Change |
|---|---|
| `contracts/openapi/ibms-frontend-api-v1.openapi.yaml` | System admin frontend subset |
| `contracts/openapi/ibms-protected-api-v1.openapi.yaml` | Full entity-types, standard-fields/methods, test |
| `contracts/openapi/README.md` | B6 reference |

---

## Entity-types routes completed

| Flask path | Methods | Auth |
|---|---|---|
| `/system/entity-types` | GET, POST | JWT; write + 403 pending |
| `/system/entity-types/{type_id}` | GET, PUT, DELETE | JWT; write/delete + 403 pending |
| `/system/entity-types/tree` | GET | JWT — 401 |

Documented in both protected-api (full) and frontend-api (subset).

---

## Standard-fields routes completed

Flask uses non-REST path names — documented as runtime paths:

| Flask path | Methods |
|---|---|
| `/system/list-standard-fields` | GET |
| `/system/getById-standard-fields/{field_id}` | GET |
| `/system/create-standard-fields` | POST |
| `/system/update-standard-fields/{field_id}` | PUT |
| `/system/delete-standard-fields/{field_id}` | DELETE |

Contract alias `/system/standard-fields` noted in description as pending adoption (not a separate OpenAPI path — avoids B4 false extras vs Flask).

---

## Standard-methods routes completed

| Flask path | Methods |
|---|---|
| `/system/list-standard-methods` | GET |
| `/system/getById-standard-methods/{method_id}` | GET |
| `/system/create-standard-methods` | POST |
| `/system/update-standard-methods/{method_id}` | PUT |
| `/system/delete-standard-methods/{method_id}` | DELETE |

---

## /system/test route decision

| Item | Detail |
|---|---|
| Flask | `GET /system/test` in `menu_api.py` |
| Runtime auth | `@jwt_required` — **401 only** in contract (no `@require_permission`) |
| Purpose | Diagnostic ping `{ status: ok }` |
| Production | Description warns **production exposure must be reviewed** |
| 403 | Not documented at runtime — reserved for future hardening |

Not included in frontend-api subset (non-user-facing diagnostic).

---

## Runtime alias notes

- Standard field/method paths use Flask naming (`list-standard-fields`, `getById-standard-fields/{field_id}`) rather than REST `/system/standard-fields/{id}`.
- Menu contract aliases (`/system/menu`, `/system/version/{version_id}/menus`) remain OpenAPI-only by design — still appear in B4 extras list.

---

## 401 / 403 rule

| Route class | Responses |
|---|---|
| JWT read (entity-types GET, list-*) | 401, 500 |
| JWT write/delete (POST/PUT/DELETE admin) | 401, 403 (enforcement pending), 500 |
| `/system/test` | 401, 500 — JWT required, no runtime 403 |

---

## Remaining gaps

**Flask missing in OpenAPI:** none (0).

**OpenAPI-only (9):** menu/version contract aliases — intentional.

**Not in scope:** audit log query API — no Flask route exists.

---

## Not changed

- `AN_VANTARIS_IBMS-backend/src/**`
- `AN_VANTARIS_IBMS-frontend/src/**`
