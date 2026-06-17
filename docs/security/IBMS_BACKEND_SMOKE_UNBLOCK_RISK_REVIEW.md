# VANTARIS IBMS Backend Smoke Unblock Risk Review

## 1. Security Boundary

| Control | Status |
|---|---|
| Real `.env` created | **No** — prep is docs-only |
| Production DB used | **No** — not connected in this task |
| Production blockchain key used | **No** |
| Production MQTT credentials used | **No** |
| Seed apply | **Not run** |
| Migration | **Not run** |
| Write API testing | **Not performed** |
| Raw source changed | **No** |
| Backend / frontend runtime changed | **No** |

This task records analysis only. EXEC must maintain the same boundaries.

---

## 2. Dependency Risk

| Risk | Detail | Mitigation (EXEC) |
|---|---|---|
| Windows-only dependency | `pywin32` breaks cross-platform install | Platform-specific requirements file |
| Python version drift | Lockfile assumes ≥3.10; CI/dev may use 3.9 | Pin Python 3.11 in smoke docs/venv |
| Supply-chain | 80 pinned packages including web3/ML stack | Split installs; minimal smoke subset |
| Dev vs runtime mix | ML/blockchain deps not needed for menu smoke | Optional requirement groups |

Do not run `pip install` blindly on production hosts using full `requirements.txt` without platform filtering.

---

## 3. Local Smoke Risk

| Risk | Detail |
|---|---|
| Local JWT placeholder | Must use **dev-only** secrets from `.env.example` pattern — never production JWT secret |
| Bind address | Backend must use **`127.0.0.1`** in smoke — avoid `0.0.0.0` default from `main.py` |
| External services | Do not contact production RPC, MQTT, or DB endpoints unless explicitly approved |
| Write APIs | Exclude POST/PUT/DELETE from smoke — permission/menu mutations affect DB |
| Blockchain skip | Reduces DID integrity guarantees in smoke mode — acceptable for API wiring test only |
| Frontend proxy | Dev-only `/api` → localhost; already scoped in frontend Vite config |

401 responses on protected GET routes are **correct** and prove auth boundary — not a smoke failure.

---

## 4. Recommended Controls

1. **`IBMS_ENV=local-smoke`** — separate profile with explicit skip flags (EXEC)
2. **Platform-specific requirements** — no `pywin32` on macOS/Linux
3. **Explicit mock/disable flags** — blockchain init, IoT manager (EXEC code + env)
4. **Audit log for smoke decisions** — document in `IBMS_BACKEND_SMOKE_UNBLOCK_EXEC.md` (next task)
5. **Test token only after approval** — signed dev JWT for 200-path verification; never commit token to git
6. **No seed/migration in smoke** — read-only GET verification first
7. **Contract alignment** — smoke uses `/api/system/menus` (not `/api/system/menu`)

---

## 5. Follow-up

| Task | Purpose |
|---|---|
| `BACKEND-SMOKE-UNBLOCK-EXEC` | Python 3.11 venv, deps split/filter, local-smoke guards, GET 401 smoke |
| Approved JWT smoke | Optional 200 responses for menu/permissions |
| `FRONTEND-BACKEND-SMOKE-2` | End-to-end with running backend + frontend proxy |
| Contract tests | OpenAPI vs live backend route map |
