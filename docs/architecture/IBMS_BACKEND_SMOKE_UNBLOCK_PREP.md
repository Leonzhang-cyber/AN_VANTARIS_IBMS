# VANTARIS IBMS Backend Smoke Unblock Prep

## 1. Task Scope

- backend smoke unblock preparation only
- no backend runtime changed
- no dependency changed
- no real `.env` created
- no DB connected
- no seed/migration executed

Target: `AN_VANTARIS_IBMS-backend/` (read-only analysis)  
Base commit: `cf77495` — test(ibms): record frontend backend smoke  
Evidence source: FRONTEND-BACKEND-SMOKE-1 (`pip install` failure, backend not started)

---

## 2. Current Blockers

| Blocker | Evidence | Impact | Proposed Handling |
|---|---|---|---|
| Python 3.9.6 incompatible packages | FRONTEND-BACKEND-SMOKE-1: `pip install -r requirements.txt` failed — `click==8.3.2` has no wheel for 3.9; pins like `numpy==2.4.4`, `pandas==3.0.2`, `scipy==1.17.1`, `pydantic==2.13.0` target modern Python | Backend venv install fails on macOS system Python 3.9.6 | Use **Python ≥3.10** (recommend **3.11**) for EXEC venv |
| Windows-only dependency `pywin32==311` | `requirements.txt` line 58 | macOS/Linux `pip install` fails or skips unpredictably | Move to **`requirements-windows.txt`**; filter on install |
| MySQL runtime required | `default.py` builds `mysql+pymysql://…`; `init_database()` in `create_app()`; menu/permissions routes query DB via SQLAlchemy | App import registers DB; GET menu/permissions need reachable MySQL schema | Local dev MySQL with placeholder creds from `.env.example`, **or** `local-smoke` lazy-init / optional SQLite adapter (EXEC design) |
| Blockchain runtime required at startup | `main.py` `init_system_on_startup()` → `Blockchain()` → **`RuntimeError` if no accounts** (line 45–46); expects RPC `127.0.0.1:8545+` and anchor contract | **`create_app()` fails** even if pip install succeeds | **`IBMS_ENV=local-smoke`** + skip/guard blockchain init in EXEC |
| IoT device manager at startup | `main.py` `init_iot_device_manager()` starts singleton `DeviceManager` (loads devices from DB, may connect MQTT drivers) | Startup errors logged; may block or degrade smoke | Disable in `local-smoke` profile (`IBMS_IOT_MANAGER_ENABLED=false` or equivalent flag in EXEC) |
| Port mismatch frontend vs backend | `main.py` runs port **5000**; frontend `.env.example` / Vite proxy target **5001** | Proxy 502 even when backend up | EXEC: bind **`127.0.0.1:5001`** via env or documented run command |
| Module-level eager `create_app()` | `main.py` lines 157–158: `app = create_app()` at import | uWSGI entry requires it, but prevents “import without side effects” for smoke tooling | EXEC: optional factory-only import path **or** smoke guards inside existing startup hooks |

---

## 3. Proposed Local Smoke Profile

**Not implemented in this task** — target for `BACKEND-SMOKE-UNBLOCK-EXEC`:

| Setting | Purpose |
|---|---|
| `IBMS_ENV=local-smoke` | Distinct from `development` / `production`; enables smoke guards |
| `IBMS_SMOKE_MODE=true` (proposed) | Master switch to skip blockchain + IoT manager init |
| DB | Use local MySQL with **non-production** placeholder credentials from `.env.example` **or** documented read-only test instance — **no migration/seed in smoke** |
| Blockchain | **Disabled** — skip `init_system_on_startup()` |
| MQTT / IoT manager | **Disabled** — skip `init_iot_device_manager()` |
| JWT | Dev placeholder secrets only (`IBMS_JWT_SECRET`, `IBMS_SECRET_KEY` from `.env.example` placeholders — **never production**) |
| Bind | **`127.0.0.1:5001`** only |
| APIs tested | **GET only** — no POST/PUT/DELETE |
| Write APIs | **Excluded** |

Approved test JWT (signed with dev JWT secret) may be added in a **separate approved task** after EXEC proves GET 401 → 200 path.

---

## 4. Proposed Dependency Split

**Recommendation only — do not modify `requirements.txt` in this task.**

| File | Contents |
|---|---|
| `requirements-core.txt` | Flask, flask-cors, Flask-SQLAlchemy, SQLAlchemy, PyMySQL, PyJWT, Werkzeug, Jinja2, pydantic, requests, python-dateutil |
| `requirements-dev.txt` | types-requests, pytest (if added), linters |
| `requirements-windows.txt` | `pywin32` (Windows only) |
| `requirements-integrations.txt` | Flask-SocketIO, python-socketio, eventlet, paho-mqtt, simple-websocket |
| `requirements-blockchain.txt` | web3, eth-*, rlp, hexbytes, ckzg, py-solc-x, aiohttp (web3 stack) |
| `requirements-ml.txt` | numpy, pandas, scipy, scikit-learn, xgboost, joblib (data modeling module) |

Install recipe for macOS smoke (EXEC):

```bash
pip install -r requirements-core.txt -r requirements-integrations.txt
# Optional for full stack: -r requirements-blockchain.txt -r requirements-ml.txt
# Windows only: -r requirements-windows.txt
```

Keep root `requirements.txt` as full lockfile reference until split is implemented and CI updated.

---

## 5. Proposed Execution Plan

**Next task: `BACKEND-SMOKE-UNBLOCK-EXEC`**

1. Install **Python 3.11** (pyenv/Homebrew) — do not use system 3.9.6
2. Create venv; install deps with **Windows packages filtered**
3. Add documented **`local-smoke`** config (env flags + startup guards — minimal code change in EXEC)
4. Start backend: `127.0.0.1:5001` (align with frontend Vite proxy)
5. **GET-only** curl smoke:
   - `/api/system/menus` → expect **401** without token
   - `/api/system/permissions` → **401**
   - `/api/system/versions` → **401**
   - `/api/system/test` → **401** (nearest “health” route; JWT required)
6. Optional: approved dev JWT → expect **200** on menu/permissions (read-only)
7. **No DB writes**, no seed `--apply`, no migration
8. Frontend proxy smoke (already configured in `vite.config.ts`)

---

## 6. Stop Conditions

Abort EXEC and report (do not commit broken runtime) if:

- Requires **real production DB credentials**
- Requires **blockchain private key** or live contract deployment
- Requires **production MQTT credentials**
- Requires **migration or seed apply** to pass smoke
- Requires **broad backend rewrite** (e.g. full DI refactor) instead of guarded startup skips
- `pip install` still fails after Python upgrade and platform split

---

## 7. Recommendation

**Proceed to `BACKEND-SMOKE-UNBLOCK-EXEC`** with narrow scope:

1. Python 3.11 venv + platform-filtered install
2. `local-smoke` startup guards (blockchain/IoT skip)
3. Local MySQL or approved mock — document which path taken
4. GET 401 verification first; JWT 200 as optional phase 2

No raw source, contracts, or frontend changes in EXEC unless proxy port doc update only.
