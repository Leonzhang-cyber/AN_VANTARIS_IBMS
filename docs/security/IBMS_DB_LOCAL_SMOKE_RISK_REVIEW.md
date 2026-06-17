# VANTARIS IBMS DB Local Smoke Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Production DB | **Not used** in prep |
| Real `.env` created | **No** |
| Password/secret committed | **No** |
| Seed/migration in prep | **Not executed** |
| Write APIs tested | **No** |
| local-smoke only | **Yes** — target bind `127.0.0.1:5001` |
| Backend/frontend src changed | **No** — docs only |

---

## 2. DB Safety Rules

- Use **disposable local DB** only (dedicated `ibms_db` smoke instance).
- **No production dump** or customer data import.
- **No destructive migration** without backup — repo has no migration framework; manual DDL only with review.
- **No root DB credential** committed to git or docs.
- Credentials supplied via **session env** or local-only config outside repo.
- Seed scripts (`seed_permissions.py --apply`) require **explicit approval** in EXEC task — default dry-run.

---

## 3. Token/Auth Boundary

- Dev JWT **already proved** auth gate (DEV-JWT-SMOKE-EXEC).
- DB smoke should use **short-lived local token** only if needed — same pattern as prior EXEC (`/tmp`, deleted after).
- Token **must not be committed**.
- **No browser localStorage** token unless explicitly approved in a future UI smoke task.
- DB 500 after valid token is **not** an auth regression.

---

## 4. Error Handling Risk

| Risk | Mitigation |
| ---- | ---------- |
| DB connection failure returns HTML 500 on permissions | Fix in **SYSTEM-DB-ERROR-JSON-1** (separate task) |
| JSON 500 bodies include raw exception strings | Sanitize messages in future handler hardening |
| Stack traces in server logs | Acceptable for local smoke; do not expose in API response |
| HTML 500 breaks API clients | Documented; permissions route highest priority for JSON consistency |

**Rule:** DB connection failure should return **JSON error**, not HTML, for all system GET smoke endpoints.

---

## 5. Follow-up Controls

| Task | Purpose |
| ---- | ------- |
| **DB-LOCAL-SMOKE-EXEC-A** (or Docker variant) | Start MySQL, minimal schema, re-run JWT + GET 200 smoke |
| **SYSTEM-DB-ERROR-JSON-1** | Align permissions route error format with menus/versions |
| **Approved dev JWT + DB 200 smoke** | Combined verification after DB EXEC |
| **Permission enforcement** | Separate from DB read smoke |
| **DID module prep** | Out of scope for DB local-smoke |

Never reuse dev smoke tokens or local DB credentials across environments.
