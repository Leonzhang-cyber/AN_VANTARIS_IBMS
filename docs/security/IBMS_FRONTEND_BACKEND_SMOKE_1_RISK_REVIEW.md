# VANTARIS IBMS Frontend Backend Smoke 1 Risk Review

## 1. Security Boundary

- no real `.env` created
- no production API URL used
- no real token/password/secret committed
- no DB write
- no seed apply
- no migration
- raw source unchanged
- contracts unchanged

Backend `.venv/` created locally for install attempt — gitignored, not committed.

---

## 2. API Auth Observations

- Protected system routes (`/api/system/menus`, `/api/system/permissions`, `/api/system/versions`) use `@jwt_required`.
- Missing/invalid `Authorization: Bearer` → **401** (documented in `jwt_util.py`).
- Permission checks on backend remain authoritative; frontend route guard is UX only.
- This smoke did not use any test token — only connection/proxy behavior observed.

---

## 3. Localhost Proxy Risk

| Control | Status |
|---|---|
| Proxy target | `http://127.0.0.1:5001` — dev-only, localhost |
| Vite `host` | `127.0.0.1` — not `0.0.0.0` |
| Production URL in config | **None** |
| Backend beyond localhost | **Not configured** |

502 from proxy when backend down confirms proxy is active without exposing a running API.

---

## 4. Follow-up Controls

- **Backend integration smoke with test token** — only after approved local backend + non-production JWT fixture task
- **Permission enforcement** — wire frontend `hasPermission()` to backend claims
- **Contract tests** — validate OpenAPI paths against running backend (`/api/system/menus` not `/api/system/menu`)
- **Backend startup docs** — Python ≥3.10, MySQL, dependency platform matrix (separate ops task)
