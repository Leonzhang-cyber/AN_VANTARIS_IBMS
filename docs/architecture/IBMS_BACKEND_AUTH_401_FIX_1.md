# VANTARIS IBMS Backend Auth 401 Fix 1

## 1. Task Scope

- fix missing/invalid JWT response from 500 to 401
- backend auth helper only
- no real token generated
- no DB write
- no seed/migration
- no frontend source changed
- no contracts changed

Base commit: `9b20fcc` — test(ibms): rerun backend local smoke

---

## 2. Root Cause

BACKEND-SMOKE-RUN-2 showed protected GET endpoints returned **500** when no Bearer token was supplied.

**Root cause:** `jwt_util.py` `@jwt_required` wrapper called `jsonify(Result.error(...)), 401`. `Result.error()` already returns `(jsonify(dict), code)` via `to_response()`. Wrapping that tuple's Response object in `jsonify()` again caused:

```
TypeError: Object of type Response is not JSON serializable
```

**Fix:** Return `Result.error(code=401, message="Unauthorized")` directly (no double `jsonify`).

**File/function changed:** `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` — `jwt_required()` wrapper (missing token, expired token, invalid token paths).

---

## 3. Files Changed

| File | Change |
| ---- | ------ |
| `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` | Return `Result.error(code=401, ...)` directly; remove double `jsonify`; unified `"Unauthorized"` message; drop unused `jsonify` import |

---

## 4. Verification

| Check | Result | Notes |
| ----- | ------ | ----- |
| backend local-smoke start | **PASS** | `127.0.0.1:5001`, Python 3.11 venv |
| GET `/api/system/menus` without token | **401** | `{"code":401,"data":null,"message":"Unauthorized"}` |
| GET `/api/system/permissions` without token | **401** | Same body |
| GET `/api/system/versions` without token | **401** | Same body |
| invalid bearer token | **401** | `Authorization: Bearer invalid.local.smoke.token` → same JSON, no stack trace |
| npm run build | **PASS** | `vue-tsc --noEmit && vite build` completed (~12s) |

No 500 on JWT paths. Response body JSON-serializable; no token/secret/stack trace in body.

---

## 5. Not Changed

- no permission enforcement changes
- no DB schema changes
- no seed/migration
- no test JWT generation
- no frontend source changes
- no contracts changes
- no `response.py` changes (`Result.error().to_response()` already correct)

---

## 6. Next Tasks

- approved dev JWT smoke
- permission enforcement
- DB local-smoke profile
- DID module prep
