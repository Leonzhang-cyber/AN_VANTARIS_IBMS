# VANTARIS IBMS Backend Smoke Run 1

## 1. Task Scope

- run backend local-smoke with Python 3.11
- no real `.env`
- no production DB
- no seed/migration
- GET-only smoke
- no write API testing

Base commit: `cf79626` — feat(ibms): add backend local-smoke startup profile

---

## 2. Environment

| Item | Value |
|---|---|
| macOS Python default | **3.9.6** (`/usr/bin/python3`) |
| python3.11 available | **No** — `command not found: python3.11`; not found in Homebrew/pyenv paths |
| Backend venv (Python 3.11) | **Skipped** — blocked on missing Python 3.11 |
| Backend URL (target) | `http://127.0.0.1:5001` |
| IBMS_ENV | `local-smoke` |

---

## 3. Dependency Install Result

| Check | Result | Notes |
|---|---|---|
| python3.11 venv | **BLOCKED** | Python 3.11 not installed on host; task rule: do not install system Python |
| pip install `requirements-macos-smoke.txt` | **BLOCKED** | Not attempted — requires Python ≥3.10 venv |
| pywin32 skipped on macOS | **N/A** | Install not run; PEP 508 marker from UNBLOCK-EXEC unverified in live install |

Existing `.venv/` (Python 3.9.6 from prior smoke) has incomplete deps (no Flask) — not used.

---

## 4. Config Smoke Result

Executed with system `python3` (config module only; no Flask import):

```
IS_LOCAL_SMOKE= True
BIND_HOST= 127.0.0.1
BIND_PORT= 5001
```

| Check | Result |
|---|---|
| `IS_LOCAL_SMOKE` | **PASS** — `True` |
| `BIND_HOST` | **PASS** — `127.0.0.1` |
| `BIND_PORT` | **PASS** — `5001` |

---

## 5. Backend Startup Result

| Item | Result |
|---|---|
| Overall | **BLOCKED** |
| Server listening on 127.0.0.1:5001 | **Not attempted** |
| Skip blockchain init | **Not verified at runtime** — code present from UNBLOCK-EXEC |
| Skip IoT manager | **Not verified at runtime** — code present from UNBLOCK-EXEC |
| MySQL / env block | **Unknown** — startup not reached |
| Real credentials required | **No** — no `.env` created |

### Blocked reason

**Python 3.11 unavailable** on smoke host. Canonical backend lockfile requires Python ≥3.10 (`click==8.3.2`, etc.). System Python 3.9.6 cannot complete `pip install -r requirements-macos-smoke.txt`.

### Prerequisite to unblock run

Install Python 3.11 (e.g. `brew install python@3.11` or pyenv) **outside this task**, then re-run:

```bash
cd AN_VANTARIS_IBMS-backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-macos-smoke.txt
IBMS_ENV=local-smoke PYTHONPATH=. python src/main.py
```

---

## 6. GET-only API Smoke

| Endpoint | Result | Notes |
|---|---|---|
| GET `/api/system/menus` | **SKIPPED** | Backend not started |
| GET `/api/system/permissions` | **SKIPPED** | Backend not started |
| GET `/api/system/versions` | **SKIPPED** | Backend not started |

---

## 7. Frontend Proxy Smoke

| Route | Result | Notes |
|---|---|---|
| `/login` | **SKIPPED** | Backend not started |
| `/system/permissions` | **SKIPPED** | Backend not started |

---

## 8. Build Verification

```bash
cd AN_VANTARIS_IBMS-frontend && npm run build
```

| Check | Result |
|---|---|
| `vue-tsc --noEmit` | **PASS** |
| `vite build` | **PASS** (~1.5s) |

Frontend regression OK; no frontend changes in this task.

---

## 9. Fixes Applied

| File | Change | Reason |
|---|---|---|
| `AN_VANTARIS_IBMS-backend/.gitignore` | Add `.venv/` | Explicit ignore if root pattern insufficient for backend-only workflows |
| `AN_VANTARIS_IBMS-backend/README.md` | Local-smoke run section | Document Python 3.11 prerequisite and start command |

No `src/**` changes.

---

## 10. Next Tasks

- Install Python 3.11 on developer machine; re-run BACKEND-SMOKE-RUN-2
- Backend MySQL local-smoke profile (optional SQLite/mock)
- Approved test JWT smoke (401 → 200 path)
- Permission enforcement
- DID module prep
