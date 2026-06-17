# VANTARIS IBMS Backend Inventory B2

**Task ID:** IBMS-BACKEND-INVENTORY-B2  
**Date:** 2026-06-16  
**Baseline Commit:** `f4becbb chore(ibms): establish modular workspace baseline`  
**Inspection Method:** Read-only `find` / `grep` / file read — no code execution

---

## 1. Task Scope

| Item | Status |
|---|---|
| Task ID | IBMS-BACKEND-INVENTORY-B2 |
| Scope | Read-only backend inventory |
| Business code changed | ❌ No |
| Dependency installed | ❌ No |
| Service started | ❌ No |
| Migration executed | ❌ No |
| Git commit | ❌ Not in this task |

---

## 2. Backend Technology Summary

### 2.1 Core Stack

| Component | Technology |
|---|---|
| Language | Python 3 (cpython-313/314 `.pyc` artifacts observed) |
| Web framework | **Flask 3.1.3** |
| CORS | flask-cors 6.0.2 |
| Real-time | Flask-SocketIO 5.6.1, python-socketio, eventlet |
| ORM | **Flask-SQLAlchemy 3.1.1** / SQLAlchemy 2.0.49 |
| Database driver | **PyMySQL 1.1.2** → MySQL |
| Auth | **PyJWT 2.12.1** (`src/common/utils/jwt_util.py`) |
| HTTP client | requests 2.33.1 |

### 2.2 Integration & Domain Dependencies

| Domain | Key Packages | Present |
|---|---|---|
| MQTT / IoT | paho-mqtt 2.1.0 | ✅ |
| DID / Blockchain | web3 7.15.0, eth-account, py-solc-x | ✅ |
| AI / Data modeling | scikit-learn 1.8.0, xgboost 3.2.0, pandas 3.0.2, numpy 2.4.4, joblib 1.5.3 | ✅ |
| Crypto | cryptography, pycryptodome | ✅ |
| Validation | pydantic 2.13.0 | ✅ |

### 2.3 Module Presence Summary

| Module Area | Discovered | Location |
|---|---|---|
| Flask API routes / Blueprint | ✅ | `src/api/` → `api_bp` prefix `/api` |
| MQTT | ✅ | `src/Iot/drivers/mqtt_driver.py`, `src/testMQTT/` |
| DID | ✅ | `src/DID/`, `src/api/did/` |
| Blockchain | ✅ | `src/blockchain/`, startup in `src/main.py` |
| Data modeling / AI | ✅ | `src/data_modeling/`, `src/api/data_modeling/` |
| Edge simulators (testMQTT) | ✅ | `src/testMQTT/` (standalone simulators + mock ISAPI Flask app) |
| System / RBAC primitives | ✅ Partial | `src/system/`, `src/api/system/` |
| Menu / version config | ✅ | `src/api/system/menu_api.py` |

### 2.4 Scale

| Metric | Count |
|---|---|
| Python source files (`.py`) | 90 |
| Directories (maxdepth 4) | 49 |
| Files (maxdepth 4) | 158 |
| Registered API route decorators (`@api_bp.route`) | ~80+ |
| Standalone simulator routes (`mock_isapi_camera.py`) | ~12 |

---

## 3. Directory Inventory

```
AN_VANTARIS_IBMS-backend/
├── README.md / README.en.md
├── requirements.txt
├── data/
│   ├── csv/                    # HVAC_SIM_001.csv (~7.2 MB, gitignored)
│   └── models/                 # hvac.pkl (~8.3 MB, gitignored)
└── src/
    ├── main.py                 # Flask app factory, blockchain + IoT startup
    ├── api/                    # HTTP Blueprint (prefix /api)
    │   ├── __init__.py         # api_bp registration
    │   ├── did/did_api.py
    │   ├── iot/iot_api.py, sse_api.py
    │   ├── system/system_api.py, menu_api.py
    │   └── data_modeling/modeling_api.py
    ├── common/
    │   ├── config/default.py   # Hardcoded DB/JWT/MQTT config ⚠️
    │   ├── core/database.py    # SQLAlchemy init
    │   ├── models/response.py  # Result + error codes
    │   └── utils/jwt_util.py   # JWT create/decode/@jwt_required
    ├── system/                 # Entity types, permissions, menu services
    ├── DID/                    # DID/VC/VP service + DAO + models
    ├── Iot/
    │   ├── device_manager.py   # Background device driver orchestration
    │   ├── drivers/            # mqtt, http, modbus, isapi, isup, rtsp
    │   ├── services/           # device, data, field, method services
    │   ├── dao.py, models.py
    │   └── command_converters/
    ├── blockchain/             # web3 client, contract, transaction, mining
    │   └── contracts/IMBSAnchor.sol
    ├── data_modeling/
    │   ├── service.py, csv_storage.py, config.py
    │   └── predictors/hvac_sim_001.py
    ├── testMQTT/               # Edge simulators (MQTT/HTTP/RTSP/ISUP/ISAPI)
    ├── scripts/                # migrate_csv_data.py, deploy_anchor.py
    └── tests/                  # Test fixtures + credential JSON samples
```

---

## 4. API / Route Inventory

All production routes register on `api_bp` with prefix **`/api`** unless noted.

### 4.1 DID API — `src/api/did/did_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| did_api.py | `/api/did/system/init` | POST | Core + Security/Auth | System root entity init; no `@jwt_required` |
| did_api.py | `/api/did/entity` | POST | Core + Security/Auth | Create sub-entity + issue VC; requires parent private key in body |
| did_api.py | `/api/did/vp/generate` | POST | Security/Auth | VP generation |
| did_api.py | `/api/did/vp/verify` | POST | Security/Auth | VP verification |
| did_api.py | `/api/did/vc/reissue` | POST | Security/Auth | VC reissue |
| did_api.py | `/api/did/vc/revoke` | POST | Security/Auth | VC revoke |
| did_api.py | `/api/did/vc/status` | POST | Security/Auth | VC status check |
| did_api.py | `/api/did/challenge` | GET | Security/Auth | Auth challenge |
| did_api.py | `/api/did/subordinates/direct` | GET | Core | Subordinate list |
| did_api.py | `/api/did/subordinates/tree` | GET | Core | Subordinate tree |
| did_api.py | `/api/did/subordinates/flat` | GET | Core | Flat subordinate list |
| did_api.py | `/api/did/entity/<did>` | GET | Core | Entity detail |
| did_api.py | `/api/did/login` | POST | Security/Auth | DID signature login → JWT |
| did_api.py | `/api/did/me` | GET | Security/Auth | **`@jwt_required`** — current user |
| did_api.py | `/api/did/chain/entity-hash/<did>` | GET | Core + Link-like | Blockchain anchor query |
| did_api.py | `/api/did/chain/vc-hash/<vc_id>` | GET | Core + Link-like | VC hash on chain |
| did_api.py | `/api/did/chain/events` | GET | Core + Link-like | Chain event log |
| did_api.py | `/api/did/verify/entity/<did>` | GET | Security/Auth | Entity verification |

### 4.2 System API — `src/api/system/system_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| system_api.py | `/api/system/entity-types` | GET/POST | Core | **`@jwt_required`** on all routes |
| system_api.py | `/api/system/entity-types/<id>` | GET/PUT/DELETE | Core | Entity type CRUD |
| system_api.py | `/api/system/entity-types/tree` | GET | Core | Entity type tree |
| system_api.py | `/api/system/permissions` | GET/POST | Core + Security/Auth | Permission CRUD |
| system_api.py | `/api/system/permissions/<id>` | GET/PUT/DELETE | Core + Security/Auth | Permission CRUD |
| system_api.py | `/api/system/*-standard-fields*` | Various | Core | Standard field CRUD (6 routes) |
| system_api.py | `/api/system/*-standard-methods*` | Various | Core | Standard method CRUD (6 routes) |

### 4.3 Menu API — `src/api/system/menu_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| menu_api.py | `/api/system/test` | GET | Core | Health/test |
| menu_api.py | `/api/system/versions` | GET/POST | Core | Version management |
| menu_api.py | `/api/system/versions/default` | GET | Core | Default version |
| menu_api.py | `/api/system/versions/<code>` | PUT/DELETE | Core | Version update/delete |
| menu_api.py | `/api/system/versions/switch/<code>` | PUT | Core | Switch active version |
| menu_api.py | `/api/system/menu/config/<code>` | GET | Core | Menu config by version |
| menu_api.py | `/api/system/menu/active` | GET | Core | Active menu |
| menu_api.py | `/api/system/menus` | GET | Core | Menu tree |
| menu_api.py | `/api/system/menus-add` | POST | Core | Add menu item |
| menu_api.py | `/api/system/menus-update/<id>` | PUT | Core | Update menu |
| menu_api.py | `/api/system/menus-delete/<id>` | DELETE | Core | Delete menu |
| menu_api.py | `/api/system/menus/batch-sort` | POST | Core | Batch sort |
| menu_api.py | `/api/system/version-menus/<code>` | GET | Core | Version menus |
| menu_api.py | `/api/system/version-menus/<code>/batch` | POST | Core | Batch assign menus |
| menu_api.py | `/api/system/version-menus/<code>/incremental` | POST | Core | Incremental sync |
| menu_api.py | `/api/system/version-menus/<code>/diff` | POST | Core | Diff menus |
| menu_api.py | `/api/system/menu/init-data` | GET | Core | Page init payload |

> **Auth note:** `menu_api.py` routes have **no `@jwt_required`** decorator observed.

### 4.4 IoT API — `src/api/iot/iot_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| iot_api.py | `/api/iot/device/register` | POST | Link-like Module | Device registration |
| iot_api.py | `/api/iot/device/parent/<parent_did>` | GET | Link-like Module | List by parent |
| iot_api.py | `/api/iot/device/did/<device_did>` | GET/PUT/PATCH/DELETE | Link-like Module | Device CRUD by DID |
| iot_api.py | `/api/iot/device/code/<device_code>` | GET | Link-like Module | Lookup by code |
| iot_api.py | `/api/iot/device/did/<did>/status` | PUT | Link-like Module | Status update |
| iot_api.py | `/api/iot/device/did/<did>/field-mappings` | PUT | Link-like Module | Field mapping |
| iot_api.py | `/api/iot/device/did/<did>/method-mappings` | PUT | Link-like Module | Method mapping |
| iot_api.py | `/api/iot/device/<code>/sse-url` | GET | Link-like Module | SSE URL helper |
| iot_api.py | `/api/iot/standard-methods` | GET/POST | Core + Link-like | Standard method defs |
| iot_api.py | `/api/iot/standard-methods/<code>` | GET/PUT/DELETE | Core + Link-like | Method CRUD |
| iot_api.py | `/api/iot/standard-fields` | GET/POST | Core + Link-like | Standard field defs |
| iot_api.py | `/api/iot/standard-fields/<code>` | GET/PUT/DELETE | Core + Link-like | Field CRUD |
| iot_api.py | `/api/iot/device/<did>/command` | POST | Link-like Module | Send device command |
| iot_api.py | `/api/iot/device/code/<code>/command` | POST | Link-like Module | Command by code |
| iot_api.py | `/api/iot/<did>/field-mappings-info` | GET | Link-like Module | Mapping info |
| iot_api.py | `/api/iot/<did>/method-mappings-info` | GET | Link-like Module | Mapping info |
| iot_api.py | `/api/iot/ingest/http` | POST | Link-like Module + Edge Interface | **HTTP telemetry ingress** |
| iot_api.py | `/api/iot/device/<code>/reconnect` | POST | Link-like Module | Driver reconnect |

> **Auth note:** `iot_api.py` routes have **no `@jwt_required`** decorator observed.

### 4.5 SSE API — `src/api/iot/sse_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| sse_api.py | `/api/iot/device/<code>/stream` | GET | Link-like Module | SSE real-time stream |
| sse_api.py | `/api/iot/device/<code>/stream` | OPTIONS | Link-like Module | CORS preflight |
| sse_api.py | `/api/iot/device/<code>/latest` | GET | Link-like Module | Latest telemetry snapshot |
| sse_api.py | `/api/iot/device/<code>/test-sse-push` | POST | Link-like Module | Test push |

### 4.6 Data Modeling API — `src/api/data_modeling/modeling_api.py`

| File | Route / Blueprint | Method | Logical Module | Notes |
|---|---|---|---|---|
| modeling_api.py | `/api/modeling/csv/list` | GET | NexusAI Interface + Storage | List CSV datasets |
| modeling_api.py | `/api/modeling/csv/<device_code>` | GET | NexusAI Interface + Storage | CSV stats |
| modeling_api.py | `/api/modeling/<device_code>/train` | POST | NexusAI Interface | Train ML model |
| modeling_api.py | `/api/modeling/<device_code>/predict` | POST | NexusAI Interface | Single-point predict |
| modeling_api.py | `/api/modeling/<device_code>/predict_future` | POST | NexusAI Interface | Multi-day forecast |
| modeling_api.py | `/api/modeling/<device_code>/model_info` | GET | NexusAI Interface | Model metadata |
| modeling_api.py | `/api/modeling/<device_code>/<method>` | GET/POST | NexusAI Interface | Generic predictor call |

> **Auth note:** `modeling_api.py` routes have **no `@jwt_required`** decorator observed.

### 4.7 Standalone Simulator (Not on api_bp)

| File | Route | Method | Logical Module | Notes |
|---|---|---|---|---|
| testMQTT/mock_isapi_camera.py | `/ISAPI/*`, `/health`, `/snapshot` | Various | Edge Interface | Standalone Flask mock camera (~12 routes) |

### 4.8 Route Registration

| File | Mechanism | Notes |
|---|---|---|
| `src/main.py` | `app.register_blueprint(api_bp)` | Single blueprint mount |
| `src/api/__init__.py` | `Blueprint('api', url_prefix='/api')` | Imports did, iot, system, menu, modeling, sse |

---

## 5. Module Ownership Mapping

| Path | Current Role | Logical Module | Risk Level | Future Split Candidate |
|---|---|---|---|---|
| `src/main.py` | App bootstrap, blockchain init, IoT manager start | Core | **Critical** | No — entry point |
| `src/api/__init__.py` | Blueprint aggregation | Core | High | Partial — route grouping |
| `src/api/did/did_api.py` | DID/VC/VP/login API | Core + Security/Auth | **Critical** | No — Core identity |
| `src/api/system/system_api.py` | Entity types, permissions, standard fields/methods | Core + Security/Auth | **Critical** | No — Core |
| `src/api/system/menu_api.py` | Menu/version CRUD (raw SQL) | Core | **High** | No — Core admin |
| `src/api/iot/iot_api.py` | Device CRUD, ingest, commands | Link-like Module | **High** | **Yes — Link** |
| `src/api/iot/sse_api.py` | SSE streaming | Link-like Module | High | **Yes — Link** |
| `src/api/data_modeling/modeling_api.py` | ML train/predict API | NexusAI Interface | **High** | **Yes — NexusAI** |
| `src/common/config/default.py` | Hardcoded secrets/config | Core / Data | **Critical** | No — move to env |
| `src/common/core/database.py` | SQLAlchemy MySQL init | Data | **Critical** | No — Data |
| `src/common/utils/jwt_util.py` | JWT + `@jwt_required` | Security/Auth | **Critical** | No — Core auth |
| `src/system/` | SystemService, menu DAO/models | Core + Data | High | Partial |
| `src/DID/` | DID service, DAO, models | Core + Security/Auth | **Critical** | No — Core identity |
| `src/Iot/device_manager.py` | Background driver manager | Link-like + Edge Interface | **High** | **Yes — Link + Edge** |
| `src/Iot/drivers/` | Protocol adapters | Edge Interface + Link-like | **High** | **Yes — Edge adapter** |
| `src/Iot/dao.py`, `models.py` | IoT persistence | Data | High | Partial — Data DAO |
| `src/Iot/services/` | Device/data/field/method services | Link-like Module | High | **Yes — Link** |
| `src/blockchain/` | web3 private chain integration | Core (anchor) | **Critical** | **Yes — external integration** |
| `src/data_modeling/` | ML service, CSV storage, predictors | NexusAI Interface + Storage | **High** | **Yes — NexusAI + Storage** |
| `src/data_modeling/csv_storage.py` | Thread-safe CSV writer | Storage | High | **Yes — Storage** |
| `src/testMQTT/` | Device simulators | Edge Interface | Medium | **Yes — Edge simulator** |
| `src/scripts/migrate_csv_data.py` | CSV data migration | Data | High | **Yes — Data migration** |
| `src/scripts/deploy_anchor.py` | Contract deploy script | Core + blockchain | High | Review |
| `src/tests/` | Test fixtures, credential JSON | Unknown / Needs Review | **High** | No — test only |
| `data/csv/`, `data/models/` | Local data/model artifacts | Storage | Medium | **Yes — Storage** |

---

## 6. Data Access Findings

### 6.1 Primary Database

| Item | Finding |
|---|---|
| Engine | **MySQL** via `mysql+pymysql://` |
| ORM | Flask-SQLAlchemy / SQLAlchemy 2.x |
| Init | `src/common/core/database.py` → `init_database(app)` |
| Config | `src/common/config/default.py` — hardcoded host `140.245.109.223:13306`, db `ibms` |
| Session usage | `db.session` across APIs, DAOs, services |

### 6.2 ORM Models Identified

| Module | Models / Tables |
|---|---|
| `src/Iot/models.py` | `IMSDevice`, `IMSStandardField`, `IMSFieldMapping`, `IMSMethodMapping`, `IMSStandardMethod` |
| `src/DID/models.py` | `EntityType`, `Permission`, `EntityRelationship`, `User`, `VCAnchor`, `VCRevocation` |
| `src/system/models.py` | System entity type extensions |
| `src/system/menu_models.py` | `sys_version`, `sys_menu`, version-menu relations |

### 6.3 Raw SQL Usage

| Location | Pattern |
|---|---|
| `src/api/system/menu_api.py` | Extensive `db.session.execute(text(...))` for menu/version tables |
| `src/system/menu_service.py` | Raw SQL via SQLAlchemy `text()` |

### 6.4 File-Based Data Storage

| Path | Type | Access |
|---|---|---|
| `data/csv/{device_code}.csv` | Telemetry time-series CSV | `csv_storage.py` — append/read via pandas |
| `data/models/{device_code}.pkl` | ML model artifacts | `hvac_sim_001.py` via joblib |
| `src/testMQTT/*.csv` | Simulator sample data | Read by simulators / migration script |

### 6.5 Blockchain as Secondary Store

| Item | Finding |
|---|---|
| Client | web3.py → private Geth cluster (3 nodes) |
| Contract | `IMBSAnchor.sol` — entity/VC hash anchoring |
| Config | `src/blockchain/config.py` — node URLs, chain ID 9527 |

### 6.6 Assessment

> **MySQL + SQLAlchemy is configured and used**, but **Data module boundary is not separated** from Core/Link/API layers. DAO, raw SQL, and business services coexist without Repository abstraction.
>
> For architecture doc purposes: **Production-grade DB boundary (isolated Data service, migration governance, backup policy) is NOT confirmed yet.**

---

## 7. Security / Auth Findings

### 7.1 JWT Infrastructure

| Component | Location | Details |
|---|---|---|
| Token create/decode | `src/common/utils/jwt_util.py` | HS256, `JWT_SECRET_KEY` from config |
| Decorator | `@jwt_required` | Reads `Authorization: Bearer <token>` |
| Login endpoint | `POST /api/did/login` | DID signature → JWT with `sub` + `perms` |
| Protected example | `GET /api/did/me` | Requires JWT |
| Permission helper | `verify_api_permission()` | Defined but **not widely applied to routes** |

### 7.2 RBAC Primitives

| Feature | Status |
|---|---|
| Permission CRUD API | ✅ `system_api.py` — `/api/system/permissions` |
| User `permission_codes` | ✅ In DID `User` model / `did_service.py` |
| JWT carries `perms` | ✅ On login |
| Route-level permission enforcement | ⚠️ **Incomplete** — most IoT/DID/menu/modeling routes unprotected |
| Role entity | ⚠️ Not found as dedicated role table — permissions appear DID-centric |

> **RBAC boundary not confirmed.** JWT exists and `system_api` is protected, but Link/Edge/NexusAI ingress routes largely lack `@jwt_required`. Full RBAC enforcement across all modules is not established.

### 7.3 Hardcoded Secrets (Critical)

Found in `src/common/config/default.py`:

| Secret Type | Hardcoded |
|---|---|
| DB password | `hexin.com` |
| DB host (public IP) | `140.245.109.223:13306` |
| JWT secret | `your-secret-key-change-in-production` |
| System DID private key | Present in source |
| MQTT broker | `1.14.152.252:1883` |

Simulator files also contain `MQTT_PASSWORD = "hexinic"`.

### 7.4 Test Credential Artifacts

| File | Risk |
|---|---|
| `src/tests/credential_*.json` | Sample credentials in repo |
| `src/tests/vc_*.json`, `vp_test.json` | VC/VP test fixtures |

---

## 8. IoT / MQTT / Edge Findings

### 8.1 IoT Core

| Component | File | Role |
|---|---|---|
| Device manager | `src/Iot/device_manager.py` | Starts on app boot; manages driver connections |
| Device service | `src/Iot/services/device_service.py` | Registration, CRUD orchestration |
| Data service | `src/Iot/services/data_service.py` | Telemetry handling |
| HTTP ingress | `POST /api/iot/ingest/http` | External device data intake |
| SSE push | `src/api/iot/sse_api.py` | Real-time stream to Console clients |

### 8.2 Protocol Drivers (`src/Iot/drivers/`)

| Driver | Protocol | Logical Module |
|---|---|---|
| `mqtt_driver.py` | MQTT (paho-mqtt) | Edge Interface + Link-like |
| `http_driver.py` | HTTP polling | Edge Interface |
| `modbus_driver.py` | Modbus (stub) | Edge Interface |
| `isapi_driver.py` | Hikvision ISAPI | Edge Interface |
| `isup_driver.py` | Hikvision ISUP | Edge Interface |
| `rtsp_driver.py` | RTSP stream | Edge Interface |

### 8.3 Edge Simulators (`src/testMQTT/`)

| File | Simulates |
|---|---|
| `hvac_mqtt_simulator.py` | HVAC MQTT telemetry |
| `air_quality_simulator.py` | Air quality MQTT |
| `http_device_simulator.py` | HTTP device |
| `isup_simulator.py` | ISUP protocol |
| `rtsp_simulator.py` | RTSP camera |
| `mock_isapi_camera.py` | Standalone ISAPI mock server |
| `mqtt_subscriber.py` | SocketIO test client |
| `test_air_quality_receiver.py` | MQTT receiver test |

### 8.4 MQTT Config

- Broker host in `default.py`: `1.14.152.252:1883`
- Simulators use hardcoded username/password (`hexinic`)

---

## 9. DID / Blockchain Findings

### 9.1 DID Module (`src/DID/`)

| Component | Role |
|---|---|
| `did_service.py` | Entity hierarchy, VC/VP lifecycle, permission inheritance |
| `dao.py` | User, entity type, permission, relationship, VC anchor/revocation DAO |
| `models.py` | SQLAlchemy models for DID tables |
| `did_utils.py`, `exceptions.py` | Utilities |

### 9.2 DID API Highlights

- Entity creation requires parent private key in request body
- Login via DID signature challenge → JWT
- Subordinate tree queries for organizational hierarchy
- Chain anchor queries for entity/VC hashes

### 9.3 Blockchain Module (`src/blockchain/`)

| File | Role |
|---|---|
| `client.py` | Multi-node RPC failover |
| `account.py` | Account management |
| `contract.py` | Deploy/call anchor contract |
| `transaction.py` | TX building/signing |
| `mining_controller.py` | Mining start/stop |
| `config.py` | Node URLs, chain ID, contract ABI |
| `contracts/IMBSAnchor.sol` | On-chain anchor contract source |

### 9.4 Startup Integration

`src/main.py` on boot:
1. Connects to private chain
2. Stops mining if active
3. Validates anchor contract
4. Calls `DIDService.init_system_entity()` (may print private key on first run)

---

## 10. AI / Data Modeling Findings

### 10.1 Service Layer

| File | Role |
|---|---|
| `src/data_modeling/service.py` | Orchestrates train/predict/list via predictor map |
| `src/data_modeling/config.py` | `DEVICE_PREDICTOR_MAP`, CSV/model paths |
| `src/data_modeling/csv_storage.py` | Thread-safe CSV append/read (pandas) |
| `src/data_modeling/predictors/hvac_sim_001.py` | HVAC XGBoost + sklearn pipeline |
| `src/data_modeling/predictors/template_predictor.py` | Predictor template |

### 10.2 ML Stack in Code

- **sklearn**: LinearRegression, SelectKBest, metrics
- **xgboost**: XGBRegressor
- **pandas/numpy**: Data manipulation
- **joblib**: Model serialize/deserialize → `data/models/hvac.pkl`

### 10.3 Configured Device

| Device Code | Predictor Module | Model File |
|---|---|---|
| `HVAC_SIM_001` | `predictors/hvac_sim_001.py` | `data/models/hvac.pkl` |

### 10.4 API Exposure

All `/api/modeling/*` endpoints are **unauthenticated** in current code — high risk for unauthorized train/predict.

---

## 11. Storage / File / Report Findings

### 11.1 Storage Mechanisms

| Mechanism | Location | Type |
|---|---|---|
| CSV telemetry store | `data/csv/{device_code}.csv` | File-based time series |
| ML model store | `data/models/{device_code}.pkl` | joblib pickle |
| CSV migration | `src/scripts/migrate_csv_data.py` | Copies testMQTT CSV → data/csv |
| HTTP file responses | Not found as dedicated upload/download API | — |
| Report export (PDF/XLSX) | **Not found** | Future Core orchestration |

### 11.2 Large / Sample Artifacts (on disk, mostly gitignored)

| File | Size | Git Status |
|---|---|---|
| `data/models/hvac.pkl` | ~8.3 MB | Ignored (`*.pkl`) |
| `data/csv/HVAC_SIM_001.csv` | ~7.2 MB | Ignored (`*.csv`) |
| `src/testMQTT/hvac_2025_prediction_data.csv` | ~4.6 MB | Ignored (`*.csv`) |
| `src/testMQTT/video.mp4` | ~13 MB | Ignored (`*.mp4`) |
| `src/testMQTT/air_quality_data.csv` | ~18 KB | Ignored (`*.csv`) |

### 11.3 Upload/Download

- No dedicated MinIO/S3 integration found
- No Flask `send_file` upload endpoints found in API layer
- IoT ingest writes to DB + CSV via services, not multipart upload API

---

## 12. High Risk Areas

| Area | Location | Risk |
|---|---|---|
| App bootstrap + chain init | `src/main.py` | Prints private keys; starts IoT manager |
| Route registration | `src/api/__init__.py` | Single blueprint — no module-level auth middleware |
| Auth / token / secret | `jwt_util.py`, `default.py` | Weak default JWT secret; secrets in source |
| Hardcoded config | `default.py`, `blockchain/config.py`, simulators | DB/MQTT/chain IPs and passwords |
| Data/model files | `data/csv/`, `data/models/` | Large artifacts; no retention policy |
| CSV / pkl / mp4 artifacts | `data/`, `testMQTT/` | Sample data in repo tree (gitignored) |
| MQTT / simulated device data | `testMQTT/`, `mqtt_driver.py` | Hardcoded broker credentials |
| DID / blockchain logic | `DID/`, `blockchain/`, `did_api.py` | Identity + on-chain anchor; many routes unauthenticated |
| Data modeling / prediction | `data_modeling/`, `modeling_api.py` | Unauthenticated train/predict |
| Menu raw SQL | `menu_api.py` | Direct SQL without auth decorator |
| IoT ingress | `POST /api/iot/ingest/http` | Unauthenticated external data intake |
| Test credentials | `src/tests/credential_*.json` | Committed in baseline (small JSON) |

---

## 13. Do Not Modify List

Current phase — do not modify without explicit approval:

1. `AN_VANTARIS_IBMS-backend/src/**` — all business source
2. `requirements.txt`
3. `data/**` — CSV and model artifacts
4. `src/testMQTT/**` — simulator scripts and sample media
5. `src/DID/**`, `src/blockchain/**` — identity and chain logic
6. `src/common/utils/jwt_util.py` — auth/token logic
7. `src/common/config/default.py` — runtime config / secrets
8. `src/common/core/database.py` — DB connection
9. Any `.env` / environment files (when introduced)

---

## 14. Recommended Next Tasks

| Priority | Task | Rationale |
|---|---|---|
| 1 | **IBMS-CONTRACTS-A0** | Version policy before documenting 80+ routes |
| 2 | **IBMS-CONTRACTS-A1** | OpenAPI drafts for `/api/did`, `/api/iot`, `/api/system`, `/api/modeling` |
| 3 | **IBMS-DATA-A0** | Separate Data Repository boundary from raw SQL/DAO mix |
| 4 | **IBMS-CORE-A0** | Unified auth middleware; close unprotected route gaps |
| 5 | **IBMS-LINK-B0** | Link-like module boundary for ingest/SSE/drivers |
| 6 | **IBMS-EDGE-INTERFACE-B0** | Edge simulator vs production adapter contract |

**Deferred:** IBMS-CONSOLE-A0 (awaiting final frontend package)

---

## 15. Related Documents

- [IBMS_WORKSPACE_B1_BASELINE.md](./IBMS_WORKSPACE_B1_BASELINE.md)
- [IBMS_CODE_INVENTORY_A1.md](./IBMS_CODE_INVENTORY_A1.md)
- [IBMS_LOGICAL_MODULE_BOUNDARY_A2.md](./IBMS_LOGICAL_MODULE_BOUNDARY_A2.md)
- [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](./IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md)
