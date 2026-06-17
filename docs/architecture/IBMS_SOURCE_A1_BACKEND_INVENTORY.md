# VANTARIS IBMS Source A1 Backend Inventory

## 1. Task Scope

- backend source inventory only
- no source changed
- no merge/copy performed

Compared packages:

- **Original:** `AN_VANTARIS_IBMS-ibms_backend/`
- **Current (canonical):** `AN_VANTARIS_IBMS-backend/`

---

## 2. Backend Package Summary

### 2.1 Original `ibms_backend`

| Area | Details |
|---|---|
| **Path** | `AN_VANTARIS_IBMS-ibms_backend/` (~35M) |
| **Tech stack** | Python 3, Flask, Flask-CORS, SQLAlchemy, PyMySQL, Flask-JWT-Extended patterns via custom `jwt_util`, paho-mqtt, Web3, scikit-learn (modeling) |
| **Entrypoint** | `src/main.py` — creates Flask app, registers `api_bp`, init DB, DID service, blockchain anchor, IoT device manager |
| **Requirements** | `requirements.txt` (80 lines) — same line count as current backend |
| **API blueprints** | Single `api_bp` at `/api` prefix; submodules: `system`, `menu`, `did`, `iot`, `sse`, `data_modeling` |
| **Database layer** | `src/common/core/database.py`, models under `src/common/models/`, SQLAlchemy URI from `src/common/config/default.py` (**hardcoded**) |
| **Auth layer** | `jwt_util.py`; `@jwt_required` on **system_api** (~21 routes) and **did_api** `/did/me` only; **no** menu/modeling/iot JWT guards |
| **Permission layer** | **Absent** — no `permission_util.py`, no `@require_permission` |
| **IoT/MQTT** | `src/Iot/` (drivers, services, device_manager), MQTT config in default.py, ingest/command/SSE routes in `iot_api.py`, `sse_api.py` |
| **DID/blockchain** | `src/DID/`, `src/blockchain/`, `src/api/did/did_api.py` — entity, VC/VP, chain hash, login |
| **Modeling/AI** | `src/data_modeling/`, `src/api/data_modeling/modeling_api.py` — csv list, train, predict, model_info; **unprotected routes** |
| **System/menu** | `system_api.py` (entity types, permissions, standard fields/methods); `menu_api.py` (19 routes) — **menu routes unprotected** |
| **Scripts** | `src/scripts/deploy_anchor.py`, `migrate_csv_data.py` |
| **Simulator/test** | `src/testMQTT/` (CSV + mp4), `src/tests/` |
| **Data artifacts** | `data/csv/`, `data/models/hvac.pkl` |
| **Python file count** | ~90 under `src/` |

### 2.2 Route inventory (original)

| Module | Route prefix | Approx routes | JWT (original) |
|---|---|---|---|
| system_api | `/api/system/*` | 21 | Yes |
| menu_api | `/api/system/menu*`, versions, menus | 19 | **No** |
| did_api | `/api/did/*` | 18 | Partial (`/did/me` only) |
| iot_api | `/api/iot/*` | 28+ | **No** |
| sse_api | `/api/iot/device/*/stream`, test-sse | 5 | **No** |
| modeling_api | `/api/modeling/*` | 7 | **No** |

---

## 3. Comparison With Current Backend

| Area | Original ibms_backend | Current AN_VANTARIS_IBMS-backend | Decision |
|---|---|---|---|
| Package layout / API modules | Same module tree (`api/system`, `did`, `iot`, `modeling`) | Same structure + `scripts/` at repo root | **same lineage** |
| Python file count | ~90 | ~93 (+ `permission_util.py`, audit/security helpers) | **newer** |
| requirements.txt | 80 lines | 80 lines (same family) | **same** |
| Config / secrets | Hardcoded DB, JWT, MQTT, DID key in `default.py` | Env-first (`IBMS_*` vars) with dev-only placeholders | **newer / hardened** |
| JWT on system_api | Yes | Yes | **same** |
| JWT on menu_api | No | Yes (all 19 routes, commit `56234d8`) | **older → security gap** |
| JWT + permissions on modeling | No | Yes (`modeling:read/train/predict`) | **older** |
| JWT + permissions on IoT | No | Yes (`device:*`, `iot:write`, `iot:ingest`) | **older** |
| JWT + permissions on DID | Partial | Yes + `did:manage/issue/revoke` | **older** |
| permission_util.py | Missing | Present | **newer** |
| Seed scripts | Under `src/scripts` only | Root `scripts/seed_permissions.py`, `assign_root_permissions.py` | **newer** |
| testMQTT / simulator guards | Unguarded test SSE push | `@jwt_required` on test-sse-push (A8B) | **newer** |
| __pycache__ | Present in snapshot | Minimal in tracked tree | **artifact noise in original** |
| Canonical for runtime | Reference only | **Yes** | **use current backend** |

**Conclusion:** Same origin; `AN_VANTARIS_IBMS-backend` is a **security-evolved superset**. Original `ibms_backend` must **not** replace current backend without losing JWT/menu/permission hardening.

---

## 4. Candidate Logical Modules

Mapping original backend code to IBMS logical modules:

| Logical module | Original paths | Notes |
|---|---|---|
| **Core/Auth/System** | `src/api/system/system_api.py`, `src/system/`, `src/common/utils/jwt_util.py` | Entity types, permissions CRUD, standard fields/methods |
| **Console/API surface (backend side)** | `menu_api.py` | Menu/version config — now JWT-protected in current backend |
| **Data/DB** | `src/common/core/database.py`, `src/common/models/` | SQLAlchemy models and session |
| **IoT/Edge Interface** | `src/Iot/`, `src/api/iot/`, `src/api/iot/sse_api.py` | Device registry, command, ingest, SSE stream |
| **DID/Trust** | `src/DID/`, `src/blockchain/`, `src/api/did/` | DID entities, VC/VP, chain anchor |
| **Modeling/NexusAI Interface** | `src/data_modeling/`, `src/api/data_modeling/` | CSV + train/predict pipeline |
| **Contracts/API** | Route definitions across `src/api/*` | Should align with `contracts/openapi/` |
| **Simulator/Test** | `src/testMQTT/`, `src/tests/` | Not for production startup |
| **Storage/Artifacts** | `data/csv/`, `data/models/*.pkl` | Externalize in split |

---

## 5. Split Recommendation

- **Do not** split original backend into multiple physical microservices in phase A.
- **Canonical backend** = `AN_VANTARIS_IBMS-backend` (already in repo, security line).
- **Original `ibms_backend`** = read-only reference for module discovery and gap analysis only.
- Next step: define **package-internal modular boundaries** (Core, IoT, DID, Modeling) inside single Flask app; align with `contracts/` and existing `IBMS_LOGICAL_MODULE_BOUNDARY_A2.md`.
- Physical split (if ever) should follow contract boundaries after B4 module migration and B5 contract validation — not before.
