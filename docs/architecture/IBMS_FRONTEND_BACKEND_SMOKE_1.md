# VANTARIS IBMS Frontend Backend Smoke 1

## 1. Task Scope

- local frontend/backend smoke
- menu and permissions API observation
- no DB write
- no seed apply
- no migration
- no production API
- no raw source changed

Target: `AN_VANTARIS_IBMS-frontend/` + read-only `AN_VANTARIS_IBMS-backend/`  
Base commit: `f14307a` — test(ibms): record frontend browser UI smoke

---

## 2. Environment

| Item | Value |
|---|---|
| Node | v20.20.2 |
| npm | 10.8.2 |
| Python | 3.9.6 (system) |
| Vite | 8.0.16 |
| Frontend dev URL | `http://127.0.0.1:5178/` |
| Backend URL (expected) | `http://127.0.0.1:5001/api` (`.env.example`; `main.py` defaults to port **5000**) |
| Backend start status | **BLOCKED** |

---

## 3. Commands Executed

```bash
# Repo checks
cd ~/Desktop/AN_VANTARIS_IBMS
git status --short
git log --oneline -20

# Backend read-only discovery
find AN_VANTARIS_IBMS-backend -maxdepth 3 -type f | sort
grep -RIn --include="*.py" -E "Flask\(|create_app|app.run" AN_VANTARIS_IBMS-backend

# Backend startup attempt
cd AN_VANTARIS_IBMS-backend
python3 --version
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # FAILED — see §4

# Frontend dev (after vite proxy added)
cd AN_VANTARIS_IBMS-frontend
npm run dev -- --host 127.0.0.1 --port 5178

# API curl (backend not running)
curl -i http://127.0.0.1:5001/api/system/menus
curl -i http://127.0.0.1:5001/api/system/permissions
curl -i http://127.0.0.1:5001/api/system/versions

# Via Vite proxy (backend down)
curl -i http://127.0.0.1:5178/api/system/menus
curl -i http://127.0.0.1:5178/api/system/permissions
curl -i http://127.0.0.1:5178/api/system/versions
curl -i http://127.0.0.1:5178/login

# Build
npm run build
```

No POST/PUT/DELETE. No real token. No `.env` created.

---

## 4. Backend Startup Result

| Check | Result |
|---|---|
| Backend started | **No — BLOCKED** |
| venv created | Yes (`.venv/` — gitignored, not committed) |
| `pip install -r requirements.txt` | **FAIL** |
| Real `.env` created | **No** |
| DB migration/seed | **Not run** |

### Blocked reasons

1. **Python version:** system Python **3.9.6** cannot satisfy pinned deps (e.g. `click==8.3.2` — no matching wheel for 3.9).
2. **Platform pins:** `requirements.txt` includes `pywin32==311` (Windows-only).
3. **Runtime deps (if install succeeded):** `create_app()` in `src/main.py` calls `init_database()` (MySQL via dev fallbacks), `init_system_on_startup()` (private blockchain + anchor contract), and IoT device manager — requires local MySQL + chain infrastructure without creating real `.env`/DB credentials in this task.
4. **Entry point:** `python src/main.py` from repo root or `flask --app src.main:application run --host 127.0.0.1 --port 5001` (not executed — blocked at install).

---

## 5. API Smoke Result

Backend not listening → direct curls return connection failure. Vite proxy returns **502 Bad Gateway** (proxy target unreachable — expected).

| Endpoint | Result | Notes |
|---|---|---|
| GET `/api/system/menu` | **BLOCKED** | No such route; canonical backend path is **`/api/system/menus`** |
| GET `/api/system/menus` | **BLOCKED** | Direct: connection refused; via proxy: **502** |
| GET `/api/system/permissions` | **BLOCKED** | Direct: connection refused; via proxy: **502**; `@jwt_required` → **401** expected when backend up, no token |
| GET `/api/system/versions` | **BLOCKED** | Direct: connection refused; via proxy: **502**; `@jwt_required` → **401** expected when backend up |

When backend is available, protected GET endpoints require `Authorization: Bearer <JWT>` per `jwt_util.jwt_required`; missing token returns **401** (acceptable).

---

## 6. Browser Smoke Result

Dev server verified at `http://127.0.0.1:5178/` (proxy config active).

| Route | Result | Notes |
|---|---|---|
| `/login` | **PASS** | HTTP 200; SPA shell loads |
| `/system` | **PASS** | Unauthenticated → redirect `/login?redirect=/system` (route guard); with token → overview (per prior UI smoke) |
| `/system/permissions` | **PASS** | Menu API 502 → fallback menu + error alert on permissions load; no white-screen crash |

Console/network: axios errors to `/api/system/menus` and `/api/system/permissions` when backend down; handled by fallback menu and `el-alert` error UI.

---

## 7. Fixes Applied

| File | Change | Reason |
|---|---|---|
| `AN_VANTARIS_IBMS-frontend/vite.config.ts` | Add dev `proxy` `/api` → `http://127.0.0.1:5001`; bind `host: '127.0.0.1'` | Local smoke: relative `/api` base URL works in dev without cross-origin |
| `AN_VANTARIS_IBMS-frontend/.env.example` | Add smoke comments (no real `.env`) | Document proxy vs absolute base URL |

`request.ts` unchanged — default `/api` works with new proxy.

---

## 8. Build Verification

```bash
npm run build
```

| Check | Result |
|---|---|
| `vue-tsc --noEmit` | PASS |
| `vite build` | PASS (~1.8s) |

---

## 9. Next Tasks

- backend permission enforcement
- real audit API
- notification/integration APIs
- DID module prep
- **Backend smoke unblock:** Python ≥3.10 venv, macOS-compatible requirements, local MySQL + approved test JWT smoke (separate task)
