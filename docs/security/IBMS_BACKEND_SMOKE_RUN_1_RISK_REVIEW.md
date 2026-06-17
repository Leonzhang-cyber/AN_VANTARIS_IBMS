# VANTARIS IBMS Backend Smoke Run 1 Risk Review

## 1. Security Boundary

| Control | Status |
|---|---|
| Real `.env` created | **No** |
| Production DB used | **No** — not connected |
| Production blockchain key used | **No** |
| Production MQTT credentials used | **No** |
| Seed apply | **Not run** |
| Migration | **Not run** |
| Write API testing | **Not performed** |

Smoke run blocked before server start; no credentials written.

---

## 2. Local Runtime Risk

- **local-smoke** profile (from UNBLOCK-EXEC) skips blockchain and IoT at startup — not exercised in this run
- **MySQL** may still be required once server starts — follow-up task
- Bind target remains **127.0.0.1:5001** per config smoke
- Frontend Vite proxy unchanged; dev-only localhost

---

## 3. API Auth Observation

- GET 401/403 on protected routes expected when backend runs without token — **not tested** (server blocked)
- No real token generated or used
- Frontend route guard remains UX-only; backend JWT authoritative

---

## 4. Follow-up Controls

- Install **Python 3.11** before next smoke run (do not use production secrets)
- DB local-smoke or mock mode — separate task
- Approved test JWT only after explicit approval
- Contract tests after backend starts cleanly
- Do not commit `.venv/`, `node_modules/`, or `dist/`
