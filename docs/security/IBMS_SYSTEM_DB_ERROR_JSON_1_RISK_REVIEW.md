# VANTARIS IBMS System DB Error JSON 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| Real `.env` created | **No** |
| DB credential committed | **No** |
| Production DB used | **No** |
| Token committed | **No** — ephemeral `/tmp` token used for verification, deleted |
| Seed/migration | **Not run** |
| Write API testing | **No** |

---

## 2. Error Response Rule

| Rule | Permissions GET (after fix) |
| ---- | --------------------------- |
| DB failure returns JSON | **Yes** — `application/json` |
| No stack trace in body | **Yes** — generic message only |
| No DB URI/password in body | **Yes** |
| No token/secret in body | **Yes** |
| Server log | Warning with exception **class name** only (`OperationalError`) |

---

## 3. Remaining Risks

- **DB-backed 200 path** still not verified — MySQL required.
- **menus/versions** still embed driver exception text in JSON 500 (information disclosure risk lower than HTML but not fully sanitized).
- **Permission enforcement** unchanged — JWT only on system GET routes.
- **local-smoke** dev DB fallbacks must not be used in production.

---

## 4. Follow-up Controls

- **DB local-smoke** as separate task for 200 responses.
- **Contract tests** after DB starts.
- **Permission matrix enforcement** as separate task.
- Optional follow-up: generic JSON error messages for menus/versions handlers.
