# VANTARIS IBMS Backend Smoke Run 2 Risk Review

## 1. Security Boundary

| Control | Status |
|---|---|
| Real `.env` created | **No** |
| Production DB used | **No** — dev fallback URI only; no successful DB query observed |
| Production blockchain key used | **No** — blockchain init skipped in local-smoke |
| Production MQTT credentials used | **No** — not exercised |
| Seed apply | **Not run** |
| Migration | **Not run** |
| Write API testing | **Not performed** |

No secrets, tokens, or production URLs written during this run.

---

## 2. Local Runtime Risk

- **local-smoke** skips blockchain/DID init and IoT DeviceManager start — **verified at runtime**
- **Import-time drivers** still register (ISUP listener on 7660); not fully isolated from IoT stack
- **MySQL** dev fallbacks (`127.0.0.1:3306`, placeholder password) configured but not required for server bind; menu/permission GET currently fail on JWT serialization before DB access
- Bind host remained **127.0.0.1:5001** — localhost only
- Frontend Vite proxy targets **127.0.0.1:5001** — dev-only, not production

---

## 3. API Auth Observation

- Protected GET routes reached JWT decorator without token
- **500 returned instead of 401** due to `jsonify(Result.error(...))` serialization bug — auth intent present but response broken
- No real token generated or used
- Frontend route guard is UX-only; backend JWT/permission remains source of truth once 401 path is fixed

---

## 4. Follow-up Controls

- DB local-smoke or mock mode as separate task (before expecting 200 on menu/permission APIs)
- Fix JWT error response serialization before contract/auth tests
- Approved test JWT only after explicit approval
- Contract tests only after backend returns clean 401/200 on GET smoke endpoints
- Do not commit `.venv/`, `node_modules/`, or `dist/`
- Normalize requirements file encoding in a dedicated task (install workaround used UTF-8 temp file only)
