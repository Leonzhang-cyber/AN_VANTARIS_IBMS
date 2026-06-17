# VANTARIS IBMS Backend Smoke Unblock Execution Risk Review

## 1. Security Boundary

| Control | Status |
|---|---|
| Real `.env` created | **No** |
| Production DB credentials | **Not added** — dev fallbacks unchanged |
| Production blockchain key | **Not used** — init skipped in local-smoke |
| Production MQTT | **Not used** — IoT manager skipped |
| Seed / migration | **Not run** |
| Write API testing | **Not performed** |

---

## 2. Local Smoke Behavior

- `local-smoke` is **non-production**; must not be used in deployment configs
- Bind defaults to **127.0.0.1:5001** — reduces exposure vs `0.0.0.0:5000`
- JWT/Flask secrets remain dev placeholders unless env overrides
- Skipping blockchain/IoT reduces attack surface during API wiring smoke only

---

## 3. Dependency Risk

- `pywin32` isolated to Windows via PEP 508 marker
- Full stack still includes web3/ML pins — macOS install requires Python ≥3.10
- `requirements-macos-smoke.txt` documents path; does not reduce package count

---

## 4. Follow-up Controls

- Do not commit `.env` with real credentials
- GET-only smoke; no POST/PUT/DELETE until approved
- Test JWT only in separate approved task
- Production must use `IBMS_ENV=production`, not `local-smoke`
