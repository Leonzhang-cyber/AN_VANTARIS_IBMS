# VANTARIS IBMS Backend Smoke Run 2

## 1. Task Scope

- run backend local-smoke with Python 3.11
- no real `.env`
- no production DB
- no seed/migration
- GET-only smoke
- no write API testing

Base commit: `1a5f208` — test(ibms): run backend local smoke

---

## 2. Environment

| Item | Value |
|---|---|
| macOS Python default | **3.9.6** (`/usr/bin/python3`) |
| python3.11 available | **Yes** — Python 3.11.15 at `/usr/local/bin/python3.11` |
| Python 3.11 install method | **brew** — `brew install python@3.11` (Homebrew 6.0.1) |
| Backend venv | **Created** — `AN_VANTARIS_IBMS-backend/.venv` (Python 3.11.15) |
| Backend URL | `http://127.0.0.1:5001` |
| IBMS_ENV | `local-smoke` |

---

## 3. Dependency Install Result

| Check | Result | Notes |
|---|---|---|
| python3.11 venv | **PASS** | `python3.11 -m venv .venv` succeeded |
| pip install `requirements-macos-smoke.txt` | **PASS** (workaround) | Direct `pip install -r requirements-macos-smoke.txt` **FAILS**: `requirements.txt` is UTF-16LE-encoded; pip reports invalid requirement. Install succeeded via install-time conversion: `iconv -f UTF-16LE -t UTF-8 requirements.txt > /tmp/ibms-requirements-utf8.txt` then `pip install -r` temp file. **Repo file not modified.** |
| pywin32 skipped on macOS | **PASS** | Log: `Ignoring pywin32: markers 'sys_platform == "win32"' don't match your environment` |

No package build failures after UTF-8 conversion. All pinned deps installed (Flask, web3, xgboost, ckzg built from source, etc.).

---

## 4. Config Smoke Result

Executed in Python 3.11 venv:

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
| Overall | **PASS** — server listening |
| Server on 127.0.0.1:5001 | **PASS** — `Running on http://127.0.0.1:5001` |
| Skip blockchain init | **PASS** — `[local-smoke] Skipping blockchain/DID system initialization` |
| Skip IoT DeviceManager | **PASS** — `[local-smoke] Skipping IoT DeviceManager start` |
| MySQL at startup | **Not blocking** — `init_database()` binds URI with dev fallbacks; no connection test at startup |
| Real env/DB required to start | **No** — no `.env` created; dev fallback DB credentials used |
| Real credentials required | **No** |

### Startup log (key lines)

```
[SECURITY-A8] IBMS_ENV=local-smoke; production=False; local_smoke=True
[local-smoke] Blockchain init and IoT DeviceManager start are disabled.
[local-smoke] Skipping blockchain/DID system initialization
[local-smoke] Skipping IoT DeviceManager start
[IBMS] Starting on 127.0.0.1:5001 (IBMS_ENV=local-smoke)
 * Running on http://127.0.0.1:5001
```

### Import-time side effects (not blocked by local-smoke)

- Driver registry loads at import (`src.api`); ISUP driver starts listener on port **7660** despite IoT DeviceManager skip
- `isapi_driver` skipped: `No module named 'cv2'` (optional dep)

### GET handler error (not MySQL)

Protected routes hit JWT decorator but return **500** instead of **401**:

```
TypeError: Object of type Response is not JSON serializable
  at jwt_util.py wrapper → jsonify(Result.error(...)), 401
```

MySQL was **not** reached on these GET requests. Follow-up fix belongs in `jwt_util.py` (out of scope for this run).

---

## 6. GET-only API Smoke

Backend running; no Authorization header; no real token.

| Endpoint | Result | Notes |
|---|---|---|
| GET `/api/system/menus` | **500** | JWT guard triggered; 401 response serialization bug → 500 |
| GET `/api/system/permissions` | **500** | Same as menus |
| GET `/api/system/versions` | **500** | Same as menus |

Expected **401** once JWT error response is fixed. No write APIs tested.

---

## 7. Frontend Proxy Smoke

Backend on 5001; Vite dev on **127.0.0.1:5178** (proxy `/api` → backend). Verified via HTTP (SPA returns `index.html`).

| Route | Result | Notes |
|---|---|---|
| `/login` | **PASS** | HTTP 200; `<title>VANTARIS IBMS</title>`; page shell loads |
| `/system/permissions` | **PASS** | HTTP 200; SPA shell loads; backend API errors handled without crash |

Multiple stale Vite instances on ports 5173–5177 were present from prior sessions; port 5178 confirmed proxy to live backend (API proxy returned 500 matching backend).

---

## 8. Build Verification

| Check | Result | Notes |
|---|---|---|
| `npm run build` | **FAIL** (hung) | `vue-tsc --noEmit` ran >18 minutes without output or completion on smoke host (likely resource contention with concurrent Vite dev processes). |
| Prior `dist/` | Exists | `dist/index.html` from earlier successful build (2026-06-17 03:57 local); not regenerated this run |

---

## 9. Fixes Applied

**None** to application source.

Documentation-only and README supplement:

- `docs/architecture/IBMS_BACKEND_SMOKE_RUN_2.md` — this report
- `docs/security/IBMS_BACKEND_SMOKE_RUN_2_RISK_REVIEW.md` — risk review
- `AN_VANTARIS_IBMS-backend/README.md` — Python 3.11 brew install + pip UTF-16 workaround note

`.gitignore` unchanged — `.venv/` already ignored.

---

## 10. Next Tasks

- Fix JWT 401 response serialization in `jwt_util.py` (500 → 401 on protected GET)
- Normalize `requirements.txt` encoding to UTF-8 (separate change; enables direct pip install)
- DB local-smoke or MySQL local profile / mock mode
- Approved test JWT smoke (401 → 200)
- Permission enforcement verification
- DID module prep
- Re-run `npm run build` on clean host (no stale Vite processes)
