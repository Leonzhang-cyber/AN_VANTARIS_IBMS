# VANTARIS IBMS Dev JWT Smoke Execution Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Non-production dev token only | **Yes** — subject `did:ibms:smoke:dev:local` |
| local-smoke only | **Yes** — `IBMS_ENV=local-smoke`, bind `127.0.0.1:5001` |
| Production secret used | **No** — dev fallback JWT secret |
| Real `.env` created | **No** |
| Token stored in `/tmp` only | **Yes** — during smoke only |
| Token removed after smoke | **Yes** |
| Token committed | **No** |
| POST/PUT/DELETE tested | **No** |
| Seed/migration | **Not run** |
| Production DB | **Not connected** |

---

## 2. Token Handling Controls

- Token **not printed in full** in docs or commit (length 320 noted only).
- Token **not committed** to git.
- Token **short-lived** (15 minutes).
- Token subject clearly marked as local smoke (`did:ibms:smoke:dev:local`, `scope: local-smoke`).
- Browser **localStorage not used**; no frontend authenticated UI test.

---

## 3. API Auth Interpretation

| Scenario | Observed | Acceptable |
| -------- | -------- | ---------- |
| Missing token | **401** JSON | Yes |
| Invalid token | **401** JSON | Yes |
| Valid dev token | **500** (DB) | Yes — JWT gate passed; not auth failure |
| Valid dev token returns 401 | Not observed | Would indicate regression |

500 after valid token indicates **DB/business issue**, not JWT gate failure.

---

## 4. Remaining Risks

- **DB-backed 200 path still fails** — MySQL connection refused on dev fallback host/port.
- **Permission enforcement** not exercised on system GET routes (no `@require_permission`).
- **Dev fallback secret** must never be used in production.
- **local-smoke** must remain bound to `127.0.0.1` only.
- **`list_permissions`** leaks stack trace to server log on DB failure; HTML 500 to client (handler inconsistency — out of scope for this task).

---

## 5. Follow-up Controls

- **DB local-smoke** as separate task before expecting 200 responses.
- **Permission matrix enforcement** as separate task.
- **Contract tests** with running backend + approved ephemeral JWT + DB.
- **Never reuse** dev smoke token across sessions or environments.
