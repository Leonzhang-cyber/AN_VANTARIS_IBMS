# VANTARIS IBMS Frontend Browser UI Smoke 1 Risk Review

## 1. Security Boundary

- no backend started
- no production API used
- no real `.env` created
- no token/password/secret committed
- no raw source copied

Smoke used a non-real localStorage token (`smoke-test-token-not-real`) only in ephemeral browser automation — not committed.

API base URL remains env-driven; default fallback is relative `/api` (dev proxy / same-origin), not a production host.

---

## 2. Route Guard Observations

- Frontend `requiresAuth` guard redirects unauthenticated users to `/login` — **UX only**.
- Placeholder `hasPermission()` returns `true` for all routes — **not a security control**.
- Backend JWT and permission enforcement remain source of truth.
- `/403` route available for permission-denied UX; `/forbidden` alias redirects to `/403`.

Protected route behavior observed: redirect-to-login when no token; layout + page content when mock token present.

---

## 3. Placeholder Page Risk

| Page | Risk control |
|---|---|
| Audit Logs | Local placeholder rows only; not audit evidence |
| Notification Settings | No real webhook URLs or channel secrets |
| Integration Settings | Explicit note: no API keys/secrets shown; placeholder rows only |
| System Settings | Read-only env preview; no credential fields |
| Permission Management | Live API wiring present but fails gracefully offline |

---

## 4. Follow-up Controls

- **Backend integration smoke** — separate task; verify menu/permissions against local API
- **Permission enforcement** — wire `hasPermission()` to session/backend claims
- **Real API wiring** — audit/notification/integration only after contracts + backend exist
- **Manual browser smoke** — recommended incognito pass on developer machine for HMR/visual regression
