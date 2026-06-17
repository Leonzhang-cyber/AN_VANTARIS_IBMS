# VANTARIS IBMS Backend Smoke Unblock Execution

## 1. Task Scope

- implement `IBMS_ENV=local-smoke` startup profile
- skip blockchain init and IoT DeviceManager in local-smoke
- bind `127.0.0.1:5001` by default in local-smoke
- macOS-installable requirements path (pywin32 platform marker)
- no seed/migration; no real `.env`; no production DB

Base commit: `f2b8755` — docs(ibms): prepare backend smoke unblock

---

## 2. Changes Applied

| File | Change |
|---|---|
| `src/common/config/default.py` | `IS_LOCAL_SMOKE`, `BIND_HOST`, `BIND_PORT` defaults |
| `src/main.py` | Guard blockchain/IoT init; configurable bind on `__main__` |
| `requirements.txt` | `pywin32` → PEP 508 `sys_platform == "win32"` |
| `requirements-macos-smoke.txt` | macOS/Linux install entry (`-r requirements.txt`) |
| `requirements-windows.txt` | Optional Windows extras reference |
| `.env.example` | local-smoke run notes |

---

## 3. Local Smoke Profile

| Setting | Value |
|---|---|
| `IBMS_ENV` | `local-smoke` |
| `IBMS_BIND_HOST` | `127.0.0.1` (default when local-smoke) |
| `IBMS_BIND_PORT` | `5001` (default when local-smoke; aligns with frontend Vite proxy) |
| Blockchain init | **Skipped** |
| IoT DeviceManager | **Skipped** |
| DB | Still configured via dev fallbacks — MySQL must be reachable for menu/permissions GET |

### Start command

```bash
cd AN_VANTARIS_IBMS-backend
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements-macos-smoke.txt
IBMS_ENV=local-smoke PYTHONPATH=. python src/main.py
```

---

## 4. Verification

| Check | Result | Notes |
|---|---|---|
| Code: `IS_LOCAL_SMOKE` flag | **PASS** | `default.py` |
| Code: skip blockchain/IoT | **PASS** | `main.py` create_app guards |
| Code: bind 127.0.0.1:5001 | **PASS** | `Config.BIND_*` + `__main__` |
| pywin32 macOS install path | **PASS** | PEP 508 marker |
| Full `pip install` on host Python 3.9.6 | **BLOCKED** | Requires Python ≥3.10 — documented |
| Live server smoke | **PENDING** | Requires Python 3.11 venv + optional local MySQL |

---

## 5. Remaining Blockers

1. **Python ≥3.10** on developer machine (system 3.9.6 insufficient for lockfile)
2. **MySQL** still required for API routes that query DB (no SQLite adapter in this task)
3. **GET 401 smoke** — follow-up with running server + curl (no test JWT in this task)

---

## 6. Next Tasks

- Install Python 3.11; run local-smoke server; curl GET `/api/system/menus` → 401
- Frontend + backend smoke with Vite proxy
- Approved dev JWT for 200-path verification
