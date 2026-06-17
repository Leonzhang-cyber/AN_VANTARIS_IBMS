# VANTARIS IBMS Backend Local Runtime Dependency Map

## 1. Startup Entry Points

| Entry | Path | Notes |
|---|---|---|
| **Canonical Flask app** | `AN_VANTARIS_IBMS-backend/src/main.py` | `create_app()` → `app` / `application` (uWSGI) |
| **Direct run** | `python src/main.py` (from backend root with `PYTHONPATH=.` ) | `host='0.0.0.0'`, **port 5000** |
| **Flask CLI (alternative)** | `flask --app src.main:application run --host 127.0.0.1 --port 5001` | Not documented in README; valid if imports succeed |
| **API blueprint** | `src/api/__init__.py` | `api_bp` prefix **`/api`** |
| **Minimal seed Flask** | `scripts/seed_permissions.py` | DB-only mini app — **not** main API server; dry-run by default |

### `create_app()` startup sequence (`src/main.py`)

1. `Flask(__name__)` + `CORS(app)`
2. `app.config.from_object(Config)` — `src/common/config/default.py`
3. `init_database(app)` — `src/common/core/database.py` (MySQL URI)
4. `app.register_blueprint(api_bp)`
5. `init_system_on_startup()` — blockchain + DID system entity (**can raise**)
6. `init_iot_device_manager(app)` — IoT singleton (**errors logged**)

---

## 2. API Modules

| Module | File | Depends On | Smoke Safe (GET, no token) |
|---|---|---|---|
| System / permissions | `src/api/system/system_api.py` | MySQL, JWT | **401** expected — `@jwt_required` |
| System / menu & versions | `src/api/system/menu_api.py` | MySQL, JWT | **401** expected; includes `GET /api/system/test` |
| DID | `src/api/did/did_api.py` | MySQL, blockchain, JWT | **No** — chain + writes |
| IoT | `src/api/iot/iot_api.py` | MySQL, device manager, MQTT drivers | **No** |
| IoT SSE | `src/api/iot/sse_api.py` | Socket/stream state | **No** |
| Data modeling | `src/api/data_modeling/modeling_api.py` | CSV/ML stack, MySQL | **No** |

Blueprint imports (side effect): `did_api`, `iot_api`, `system_api`, `menu_api`, `modeling_api`, `sse_api` — all loaded at app registration.

---

## 3. External Services

| Service | Evidence | Required at Startup | Can Disable for Smoke |
|---|---|---|---|
| **MySQL** | `default.py` `SQLALCHEMY_DATABASE_URI`; `database.py` `mysql+pymysql://…`; PyMySQL in requirements | **Yes** — `init_database()` always runs; routes query `db.session` | **Partial** — URI still needed; skip heavy init only; SQLite adapter **not present today** |
| **Blockchain / Web3** | `main.py` `init_system_on_startup()`; `blockchain/config.py` RPC URLs `127.0.0.1:8545–8547`; `web3`, `eth-*` in requirements | **Yes today** — raises if no chain accounts | **Yes** — guard skip in `local-smoke` (EXEC) |
| **Anchor contract** | `ANCHOR_CONTRACT_ADDRESS` env / empty dev default; ABI in `blockchain/config.py` | **Soft** — logs error and returns if unset; but account check raises first | **Yes** — with blockchain skip |
| **MQTT** | `default.py` `IBMS_MQTT_*`; `paho-mqtt`; `Iot/drivers/mqtt_driver.py` | **No at import** — on device connect | **Yes** — skip IoT manager start |
| **IoT Manager** | `main.py` `init_iot_device_manager()`; `Iot/device_manager.py` singleton | **Invoked at startup** — loads DB devices | **Yes** — skip in smoke profile |
| **Private chain mining control** | `init_system_on_startup()` miner_stop RPC calls | Only if blockchain init runs | **Yes** — with blockchain skip |

---

## 4. Environment Variables

Discovered in `src/common/config/default.py`, `src/blockchain/config.py`, `.env.example` — **placeholders only; no real values in this doc.**

| Variable | Purpose |
|---|---|
| `IBMS_ENV` | Environment name (`development`, `production`; propose `local-smoke`) |
| `IBMS_DEBUG` | Debug flag (`.env.example`) |
| `IBMS_SECRET_KEY` | Flask secret |
| `IBMS_JWT_SECRET` | JWT signing secret |
| `IBMS_DATABASE_URL` | Full MySQL URL |
| `IBMS_DB_HOST` / `PORT` / `NAME` / `USER` / `PASSWORD` | DB components |
| `IBMS_MQTT_HOST` / `PORT` / `USERNAME` / `PASSWORD` | MQTT broker |
| `IBMS_DID_PRIVATE_KEY` | DID signing key |
| `IBMS_BLOCKCHAIN_RPC_URL` | Comma-separated RPC URLs |
| `IBMS_BLOCKCHAIN_CHAIN_ID` | Chain ID |
| `IBMS_BLOCKCHAIN_CONTRACT_ADDRESS` | Anchor contract address |
| `IBMS_TEST_DID_PRIVATE_KEY` | Test scripts only |
| `IBMS_SIMULATOR_ENABLED` | Dev simulator flag |
| `IBMS_TESTMQTT_ENABLED` | testMQTT scripts flag |
| `IBMS_MODELING_API_ENABLED` | Modeling API flag (`.env.example`) |
| `IBMS_UPLOAD_DIR` / `IBMS_MAX_UPLOAD_MB` | Upload config |
| `IBMS_TRACE_ENABLED` / `IBMS_AUDIT_ENABLED` | Audit/trace flags |

Dev fallbacks in `default.py` use non-production placeholders (`dev-only-jwt-secret-do-not-use-in-production`, `replace-with-db-password`, etc.).

---

## 5. Local Smoke Candidates

| Endpoint | Method | Auth | Smoke role |
|---|---|---|---|
| `GET /api/system/test` | GET | JWT required | Closest built-in ping — expect **401** without token |
| `GET /api/system/menus` | GET | JWT required | Frontend menu API — **401** / **200** with test JWT |
| `GET /api/system/permissions` | GET | JWT required | Frontend permissions list — **401** / **200** with test JWT |
| `GET /api/system/versions` | GET | JWT required | Menu version list — **401** / **200** with test JWT |

**No public `/api/health` route found** on main blueprint.

Frontend paths (reference): `menu.ts` calls `/system/menus`; not `/system/menu`.

---

## 6. Requirements / Platform Notes (macOS)

| Package | Issue |
|---|---|
| `pywin32==311` | Windows-only |
| `click==8.3.2` | Requires Python ≥3.10 |
| `numpy`, `pandas`, `scipy`, `xgboost` | Heavy; Python ≥3.10; optional for system-only smoke |
| `ckzg` | Native build may need toolchain |
| `pywin32`, `eventlet`, `Flask-SocketIO` | IoT/SSE path — optional for menu/permissions smoke |

System Python on smoke host: **3.9.6** — insufficient for current lockfile.
