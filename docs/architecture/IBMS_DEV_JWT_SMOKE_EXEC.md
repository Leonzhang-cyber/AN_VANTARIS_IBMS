# VANTARIS IBMS Dev JWT Smoke Execution

## 1. Task Scope

- approved non-production dev JWT smoke
- local-smoke only
- short-lived token
- no real `.env`
- no production secret
- no seed/migration
- no write API testing

Base commit: `ca757e6` — docs(ibms): prepare approved dev JWT smoke

---

## 2. Environment

| Item | Value |
| ---- | ----- |
| Backend URL | `http://127.0.0.1:5001` |
| IBMS_ENV | `local-smoke` |
| JWT secret source | Dev fallback via `Config.JWT_SECRET_KEY` (no `.env`) |
| Token storage | `/tmp/ibms-local-smoke-token.txt` only during smoke |
| Token lifetime | 15 minutes |
| Token committed | **No** |
| Token length (observed) | 320 chars (not recorded in repo) |

---

## 3. Token Payload

Field names only — **no token value in this document**.

| Field | Purpose |
| ----- | ------- |
| `sub` | `did:ibms:smoke:dev:local` — local smoke subject |
| `iat` | Issued-at (UTC) |
| `exp` | 15-minute expiry |
| `perms` | `["system:read"]` |
| `permission_codes` | `["system:read"]` |
| `permissions` | `["system:read"]` |
| `scope` | `local-smoke` marker |

Signed with dev fallback `JWT_SECRET_KEY` (HS256), same secret backend reads at runtime.

---

## 4. Curl Results

| Endpoint | No Token | Invalid Token | Valid Dev Token | Notes |
| -------- | -------- | ------------- | --------------- | ----- |
| GET `/api/system/menus` | **401** | **401** | **500** | Valid: JWT passed; MySQL connection refused |
| GET `/api/system/permissions` | **401** | N/A | **500** | Valid: JWT passed; unhandled DB exception → HTML 500 |
| GET `/api/system/versions` | **401** | N/A | **500** | Valid: JWT passed; MySQL connection refused |

**No-token / invalid body:** `{"code":401,"data":null,"message":"Unauthorized"}`

**Valid-token menus/versions body (JSON):** `OperationalError (2003) Can't connect to MySQL server on '127.0.0.1' (Connection refused)`

**Valid-token permissions body:** Flask HTML 500 page (same root cause — DB unreachable; route lacks try/except wrapper)

---

## 5. Interpretation

| Question | Result |
| -------- | ------ |
| Valid token passed JWT gate? | **Yes** — no 401 on any valid-token GET |
| Valid token reached DB/business layer? | **Yes** — stack traces show handler execution after `@jwt_required` |
| DB is next blocker? | **Yes** — MySQL not listening on `127.0.0.1:3306` |
| Any 500 auth-related? | **No** — 401 path fixed; 500s are post-auth DB errors |
| Permission 403? | **No** — routes have `@jwt_required` only |

Backend startup: **PASS** — `127.0.0.1:5001`, blockchain/DID and IoT DeviceManager skipped (local-smoke).

---

## 6. Frontend Observation

Executed via existing dev server on `127.0.0.1:5174` (unauthenticated; no token in browser/localStorage).

| Route | Result | Notes |
| ----- | ------ | ----- |
| `/login` | **PASS** — HTTP 200 | `<title>VANTARIS IBMS</title>`; no token/secret in HTML |
| `/system/permissions` | **PASS** — HTTP 200 | SPA shell loads; route guard handles unauthenticated state client-side |

No browser token injection performed per task rules.

---

## 7. Build Verification

| Check | Result |
| ----- | ------ |
| `npm run build` | **PASS** — `vue-tsc --noEmit && vite build` ~12s |

---

## 8. Temporary Token Cleanup

| Check | Result |
| ----- | ------ |
| `/tmp/ibms-local-smoke-token.txt` removed | **Yes** — deleted after curl smoke |
| Token in git/docs | **No** |

---

## 9. Next Tasks

- **DB local-smoke profile** — local MySQL or mock so valid-token GET returns 200
- **Permission enforcement** — verify 403 on guarded routes with/without `perms`
- **Handler error consistency** — `list_permissions` unhandled DB exception returns HTML 500 (separate fix)
- **DID module prep**
- **Contract tests** against running backend with approved dev JWT + DB
