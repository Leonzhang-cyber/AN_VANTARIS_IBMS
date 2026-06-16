# VANTARIS IBMS System DB Error JSON 1

## 1. Task Scope

- normalize permissions DB failure response
- no DB setup
- no schema/seed/migration
- no write API testing
- no frontend source changed
- no contracts changed

Base commit: `3ef073c` — docs(ibms): prepare DB local smoke

---

## 2. Root Cause

- **DEV-JWT-SMOKE-EXEC** confirmed JWT gate passes; valid dev token reaches permissions handler.
- **DB connection failure** (`OperationalError 2003`, MySQL not on `127.0.0.1:3306`) bubbled uncaught from `list_permissions`.
- Flask default error handler returned **HTML 500** for permissions while menus/versions used try/except → JSON 500.
- **Root cause:** `list_permissions` in `system_api.py` had no try/except around `SystemService.list_permissions()`.

---

## 3. Files Changed

| File | Change |
| ---- | ------ |
| `AN_VANTARIS_IBMS-backend/src/api/system/system_api.py` | Wrap GET `list_permissions` in try/except; return `Result.error(code=500, message="Failed to load permissions")`; log `type(e).__name__` only |

---

## 4. Verification

| Check | Result | Notes |
| ----- | ------ | ----- |
| backend local-smoke start | **PASS** | `127.0.0.1:5001` |
| GET `/api/system/permissions` without token | **401** | `{"code":401,"message":"Unauthorized"}` |
| GET `/api/system/permissions` valid token + DB down | **JSON 500** | `Content-Type: application/json`; `{"code":500,"message":"Failed to load permissions"}` — **not HTML** |
| GET `/api/system/menus` valid token + DB down | **JSON 500** | `DB_UNAVAILABLE` envelope via local-smoke helper (when enabled) |
| GET `/api/system/versions` valid token + DB down | **JSON 500** | Same as menus |
| npm run build | **FAIL** | `vue-tsc`: `MODULE_NOT_FOUND` in `@vue/compiler-core` (node_modules); bundling not verified this run |

No stack trace, DB password, or token in permissions response body.

---

## 5. Not Changed

- no DB local-smoke implementation
- no DB credentials
- no schema changes
- no seed/migration
- no permission enforcement
- no frontend source changes
- no contracts changes
- menus/versions error messages unchanged (future standardization optional)

---

## 6. Next Tasks

- DB local-smoke execution
- approved dev JWT + DB 200 smoke
- optional: sanitize menus/versions JSON 500 messages (match permissions generic text)
- permission enforcement
- DID module prep
