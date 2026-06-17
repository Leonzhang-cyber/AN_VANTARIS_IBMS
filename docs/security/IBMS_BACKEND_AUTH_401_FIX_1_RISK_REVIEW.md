# VANTARIS IBMS Backend Auth 401 Fix 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Real JWT generated | **No** |
| Production secret used | **No** — dev fallback JWT secret from config only |
| Real `.env` created | **No** |
| DB write | **No** |
| Seed/migration | **Not run** |
| POST/PUT/DELETE tested | **No** |

---

## 2. Auth Response Rule

- missing token returns **401** with JSON body `{"code":401,"data":null,"message":"Unauthorized"}`
- invalid/expired token returns **401** with same schema (no distinction leaked in message)
- response body is JSON-serializable
- response body does not include token, secret, or stack trace

---

## 3. Remaining Risks

- permission enforcement still pending (JWT presence only; no per-route permission matrix)
- approved test JWT smoke still pending (401 → 200 path not verified)
- DB-backed 200 path not verified (authenticated GET with valid token + DB)
- local-smoke still depends on DB for real menu/permission data once token is supplied

---

## 4. Follow-up Controls

- dev JWT smoke only after explicit approval
- permission matrix enforcement as separate task
- contract tests against running backend after approved JWT available
