# VANTARIS IBMS Approved Dev JWT Smoke Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| JWT generated in this prep task | **No** |
| Real `.env` created | **No** |
| Production secret used | **No** |
| Production DB used | **No** |
| Token/password/secret committed | **No** |
| Seed/migration | **Not run** |
| Write API testing | **Not performed** |
| Backend/frontend source changed | **No** — docs only |

---

## 2. Dev Token Rule

For the planned **DEV-JWT-SMOKE-EXEC** task:

- Dev token must be **short-lived** (use default 8h max or explicit short `expires_in_hours` in generator script).
- Dev token must be **local-smoke only** — never used against production hosts.
- Dev token must **never be committed** to git, docs, or chat logs in full.
- Dev token must **not use production secret** — only dev fallback or ephemeral `<LOCAL_SMOKE_JWT_SECRET>`.
- Dev token must **not be logged in full** — log only “token issued” or last 4 chars if needed for correlation.

Token generation should occur in **memory or `/tmp` one-off script**, deleted after EXEC.

---

## 3. API Auth Expectations

| Scenario | Expected HTTP | Notes |
| -------- | ------------- | ----- |
| Missing `Authorization` | **401** | Fixed in AUTH-401-FIX-1 |
| Invalid / expired Bearer | **401** | Same JSON envelope |
| Valid dev token, auth-only route (`/api/system/test`) | **200** | No DB |
| Valid dev token, DB-backed system GET | **200** or **500** | 200 with data/`[]` if MySQL OK; 500 = DB issue, not auth failure |
| Valid dev token, permission-guarded route without `perms` | **403** | Not in scope for initial system GET smoke |

**500 is not acceptable for auth failure** — only for downstream DB/application errors after JWT passes.

Response body must remain JSON-serializable; no stack traces, secrets, or full tokens in responses.

---

## 4. Remaining Risks

- **DB-backed 200 path** may require local MySQL with `sys_menu`, `sys_version`, and permissions tables — dev fallbacks point to `127.0.0.1:3306` with placeholder credentials.
- **Permission enforcement** is implemented (`require_permission`) but **not applied** to the three system GET smoke endpoints; broader 403 testing is a separate task.
- **local-smoke config** (dev JWT fallback, skipped blockchain/IoT) must not be deployed or reused in production.
- **Contract tests** against authenticated backend remain pending.
- **requirements.txt UTF-16** encoding may require install-time `iconv` workaround (documented in RUN-2); does not affect JWT logic.

---

## 5. Follow-up Controls

- **DEV-JWT-SMOKE-EXEC** only after explicit approval and with ephemeral token handling.
- **Permission enforcement** verification as separate task (routes with `@require_permission`).
- **DB local-smoke profile** as separate task if 200 with real menu/permission data is required.
- Do **not** test POST/PUT/DELETE in JWT smoke EXEC.
- Do **not** use `/api/did/login` POST in smoke EXEC unless DID/VP infrastructure is explicitly in scope — prefer in-memory `create_jwt` with minimal payload.
