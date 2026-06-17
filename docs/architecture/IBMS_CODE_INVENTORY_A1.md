# VANTARIS IBMS Code Inventory A1

**Task:** IBMS-INVENTORY-A1  
**Date:** 2026-06-16  
**Inspection Method:** Read-only `ls` / `find` / `unzip -l` / `unzip -p` on workspace; no extraction, no code modification.

---

## 1. Workspace Overview

| Item | Status |
|---|---|
| Root path | `/Users/leon/Desktop/AN_VANTARIS_IBMS` |
| Frontend on disk | `AN_VANTARIS_IBMS-main/` — **placeholder only** (`README.md`) |
| Backend on disk | `AN_VANTARIS_IBMS-backend/` — **NOT present** (archived in zip) |
| Backend archive | `AN_VANTARIS_IBMS-backend.zip` — full Python/Flask `src/` tree |
| Frontend archive | `AN_VANTARIS_IBMS-main.zip` — placeholder (`README.md` only) |
| Git repository | Not initialized at workspace root |

---

## 2. Frontend Inventory — `AN_VANTARIS_IBMS-main`

### 2.1 On-Disk Structure

```
AN_VANTARIS_IBMS-main/
└── README.md          # Placeholder: "# AN_VANTARIS_IBMS\nSource Code"
```

### 2.2 Expected Future Structure (Not Yet Present)

When Console is fully implemented, expected logical areas:

| Expected Path | Logical Module | Notes |
|---|---|---|
| `src/pages/` or `src/views/` | Console | Dashboard, Asset, Alarm, Event, Work Order |
| `src/components/` | Console | Shared UI components |
| `src/api/` or `src/services/` | Console | Backend/Core API client only |
| `src/store/` or `src/state/` | Console | Client-side state |
| `src/router/` | Console | Route definitions |
| `src/auth/` | Console | JWT session UI — **HIGH RISK: auth/login/RBAC** |
| `public/` | Console | Static assets |
| `package.json` | Console | Build config — **not present yet** |
| `vite.config.*` | Console | Build config — **not present yet** |

### 2.3 Frontend Inventory Status

> **Current state:** Frontend package is a scaffold placeholder. Full Console source code has not been deployed to the workspace. Inventory below for backend is based on zip archive inspection.

---

## 3. Backend Inventory — `AN_VANTARIS_IBMS-backend` (from zip)

### 3.1 Top-Level Structure

```
AN_VANTARIS_IBMS-backend/
├── README.md / README.en.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── csv/                    # HVAC simulation CSV (HVAC_SIM_001.csv)
│   └── models/                 # ML model files (hvac.pkl)
└── src/
    ├── main.py                 # Flask app entrypoint
    ├── api/                    # HTTP API blueprints
    ├── common/                 # Config, DB, utils, response models
    ├── system/                 # System/user/menu services
    ├── DID/                    # Decentralized Identity (DID/VC/VP)
    ├── Iot/                    # IoT device management & drivers
    ├── blockchain/             # Private chain integration
    ├── data_modeling/          # ML predictors / AI-like services
    ├── testMQTT/               # Device simulators (Edge-like)
    ├── scripts/                # Deploy / migration scripts
    └── tests/                  # Test utilities & fixtures
```

### 3.2 Backend Module Detail

| Directory | Key Files | Approx. Role |
|---|---|---|
| `src/main.py` | Flask init, blockchain startup, device manager | Core bootstrap |
| `src/api/` | `iot_api.py`, `system_api.py`, `menu_api.py`, `did_api.py`, `modeling_api.py`, `sse_api.py` | Core + Link-like HTTP ingress |
| `src/api/system/` | `system_api.py`, `menu_api.py` | Core — auth/system/menu **HIGH RISK** |
| `src/api/iot/` | `iot_api.py`, `sse_api.py` | Link-like — IoT ingress + SSE |
| `src/api/did/` | `did_api.py` | Core — identity API **HIGH RISK** |
| `src/api/data_modeling/` | `modeling_api.py` | NexusAI Interface ingress |
| `src/common/core/` | `database.py` | Data — DB connection **HIGH RISK** |
| `src/common/config/` | `default.py` | Environment config **HIGH RISK** |
| `src/common/utils/` | `jwt_util.py`, `vp_util.py` | Core — auth utilities **HIGH RISK** |
| `src/system/` | `service.py`, `dao.py`, `menu_*` | Core + Data — user/system RBAC **HIGH RISK** |
| `src/DID/` | `did_service.py`, `dao.py`, `models.py` | Core — identity **HIGH RISK** |
| `src/Iot/` | `device_manager.py`, `drivers/`, `services/` | Link-like + Edge drivers **HIGH RISK: external integration** |
| `src/Iot/drivers/` | `mqtt_driver.py`, `modbus_driver.py`, `http_driver.py`, `isapi_driver.py`, `isup_driver.py`, `rtsp_driver.py` | Edge/Link — protocol adapters **HIGH RISK** |
| `src/blockchain/` | `client.py`, `contract.py`, `transaction.py` | Core — blockchain anchor **HIGH RISK: external integration** |
| `src/data_modeling/` | `service.py`, `predictors/hvac_sim_001.py`, `csv_storage.py` | NexusAI Interface + Storage **HIGH RISK: AI call** |
| `src/testMQTT/` | `hvac_mqtt_simulator.py`, `isup_simulator.py`, `rtsp_simulator.py`, etc. | Edge Interface — simulators |
| `src/scripts/` | `migrate_csv_data.py`, `deploy_anchor.py` | Data migration scripts **HIGH RISK** |
| `src/tests/` | test fixtures, credential JSON | Test only — **HIGH RISK: contains credential samples** |
| `data/csv/` | `HVAC_SIM_001.csv` | Storage — local data files |
| `data/models/` | `hvac.pkl` | Storage — ML model artifacts |

### 3.3 Not Found in Current Backend Archive

The following paths referenced in future IBMS architecture are **not present** in the current zip:

- `prisma/` — not applicable (Python/SQLAlchemy stack)
- `migrations/` — not found as dedicated directory
- `seed/` — not found
- Dedicated MinIO / S3 storage module
- Dedicated notification dispatch module
- Dedicated report export worker

These are marked as **Future / Planned** in logical mapping.

---

## 4. Logical Ownership Mapping

| Current Path | Physical Package | Logical Module | Current Role | Split Candidate |
|---|---|---|---|---|
| `AN_VANTARIS_IBMS-main/` | Frontend (main) | Console | Frontend package root (placeholder) | No — stays as Console |
| `AN_VANTARIS_IBMS-main/README.md` | Frontend (main) | Console | Placeholder readme | No |
| `AN_VANTARIS_IBMS-backend/src/main.py` | Backend (zip) | Core | Flask app bootstrap & lifecycle | No — Core entry |
| `AN_VANTARIS_IBMS-backend/src/api/` | Backend (zip) | Core | REST API blueprint registration | Partial — ingress routes may split to Link |
| `AN_VANTARIS_IBMS-backend/src/api/system/` | Backend (zip) | Core | System/user/menu API **auth/RBAC** | No — Core |
| `AN_VANTARIS_IBMS-backend/src/api/iot/` | Backend (zip) | Link | IoT device HTTP ingress | **Yes — Link ingress** |
| `AN_VANTARIS_IBMS-backend/src/api/iot/sse_api.py` | Backend (zip) | Link | SSE real-time push | **Yes — Link delivery** |
| `AN_VANTARIS_IBMS-backend/src/api/did/` | Backend (zip) | Core | DID/VC identity API | No — Core (identity) |
| `AN_VANTARIS_IBMS-backend/src/api/data_modeling/` | Backend (zip) | NexusAI Interface | ML modeling API ingress | **Yes — NexusAI Interface** |
| `AN_VANTARIS_IBMS-backend/src/common/core/database.py` | Backend (zip) | Data | DB connection init | No — Data |
| `AN_VANTARIS_IBMS-backend/src/common/config/` | Backend (zip) | Core / Data | App configuration **env config** | No — shared config |
| `AN_VANTARIS_IBMS-backend/src/common/utils/jwt_util.py` | Backend (zip) | Core | JWT auth utility **auth** | No — Core |
| `AN_VANTARIS_IBMS-backend/src/system/` | Backend (zip) | Core + Data | User/system/menu service+DAO **RBAC** | Partial — DAO stays Data |
| `AN_VANTARIS_IBMS-backend/src/DID/` | Backend (zip) | Core | Decentralized identity service | No — Core |
| `AN_VANTARIS_IBMS-backend/src/Iot/` | Backend (zip) | Link + Edge Interface | Device management & protocol drivers | **Yes — Link + Edge** |
| `AN_VANTARIS_IBMS-backend/src/Iot/drivers/` | Backend (zip) | Edge Interface | Protocol adapters (MQTT/Modbus/RTSP/ISAPI) | **Yes — Edge adapter** |
| `AN_VANTARIS_IBMS-backend/src/blockchain/` | Backend (zip) | Core | Private chain anchor integration | **Yes — external integration** |
| `AN_VANTARIS_IBMS-backend/src/data_modeling/` | Backend (zip) | NexusAI Interface | ML predictors & modeling service **AI call** | **Yes — NexusAI Interface** |
| `AN_VANTARIS_IBMS-backend/src/data_modeling/csv_storage.py` | Backend (zip) | Storage | CSV file storage adapter | **Yes — Storage interface** |
| `AN_VANTARIS_IBMS-backend/data/csv/` | Backend (zip) | Storage | Simulation/training CSV data | **Yes — Storage** |
| `AN_VANTARIS_IBMS-backend/data/models/` | Backend (zip) | Storage | ML model artifacts (pkl) | **Yes — Storage** |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/` | Backend (zip) | Edge Interface | Device simulators (MQTT/HTTP/RTSP/ISUP) | **Yes — Edge simulator** |
| `AN_VANTARIS_IBMS-backend/src/scripts/migrate_csv_data.py` | Backend (zip) | Data | CSV data migration script **migration** | **Yes — Data migration** |
| `AN_VANTARIS_IBMS-backend/src/scripts/deploy_anchor.py` | Backend (zip) | Core | Blockchain deploy script | Review |
| `AN_VANTARIS_IBMS-backend/src/tests/` | Backend (zip) | Unknown / Needs Review | Test fixtures & credential samples | No — test only |
| `contracts/` | Root | Contracts | Future protocol center (placeholder) | N/A — documentation only |

---

## 5. High-Risk Areas

The following areas require strict change control and must not be moved or modified without explicit approval:

| Area | Current Location | Risk |
|---|---|---|
| **auth / login** | `src/common/utils/jwt_util.py`, `src/api/system/` | Authentication bypass |
| **RBAC / user / role / permission** | `src/system/`, `src/api/system/menu_api.py` | Authorization breach |
| **database schema / access** | `src/common/core/database.py`, `src/*/dao.py` | Data integrity |
| **migration** | `src/scripts/migrate_csv_data.py` | Data loss |
| **seed** | Not present — future Data module | Data integrity |
| **environment config** | `src/common/config/default.py`, `.env` (future) | Credential leak |
| **notification dispatch** | Not present — future Link module | Message spoofing |
| **file upload / storage** | `src/data_modeling/csv_storage.py`, `data/` | Data exfiltration |
| **external integration** | `src/Iot/drivers/`, `src/blockchain/` | OT/security boundary |
| **AI call** | `src/data_modeling/predictors/`, `data/models/` | Model poisoning / cost |
| **report export** | Not present — future Core orchestration | Data leak |

---

## 6. Do Not Move List

The following paths and concerns must **not** be relocated, renamed, or split during the current A0–A3 phase:

1. `AN_VANTARIS_IBMS-main/src` — (when created) Console source root
2. `AN_VANTARIS_IBMS-backend/src` — Backend source root
3. `prisma/` / `migrations/` — (future Data module; not present in current Python stack)
4. **auth / login / RBAC** — `src/system/`, `src/api/system/`, `src/common/utils/jwt_util.py`
5. **env config** — `src/common/config/`, `.env`, `.env.*`
6. **upload / storage implementation** — `src/data_modeling/csv_storage.py`, `data/`
7. **notification implementation** — (future; not present)
8. **database access code** — `src/common/core/database.py`, all `dao.py` files

---

## 7. Future Split Candidates

These modules are candidates for future physical separation when the system matures beyond the dual-package monolith:

| Candidate | Current Location | Future Logical Module |
|---|---|---|
| Link ingress / integration | `src/api/iot/`, `src/Iot/` | Link |
| Edge adapter / import / simulator | `src/Iot/drivers/`, `src/testMQTT/` | Edge Interface |
| NexusAI interface | `src/data_modeling/`, `src/api/data_modeling/` | NexusAI Interface |
| Storage interface | `src/data_modeling/csv_storage.py`, `data/` | Storage |
| Report worker | Not present | Core orchestration → future worker |
| Notification adapter | Not present | Link-like Module |
| Data migration / backup scripts | `src/scripts/` | Data |

---

## 8. Re-Inventory Trigger

Re-run IBMS-INVENTORY-A1 when:

1. `AN_VANTARIS_IBMS-backend.zip` is extracted to `AN_VANTARIS_IBMS-backend/`.
2. Full Console frontend source is added to `AN_VANTARIS_IBMS-main/`.
3. Prisma / PostgreSQL / MinIO modules are introduced.
4. Any new top-level package is added to the workspace.
