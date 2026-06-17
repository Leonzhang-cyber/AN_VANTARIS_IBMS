# VANTARIS IBMS Split A0 Modular Split Rules

## 1. Task Scope

- define split rules only
- no source moved
- no package created
- no runtime changed

Based on SOURCE-A0/A1/A2 inventory (commits on `main` after `21c49b6`).

---

## 2. Physical Package Rule

Current phase recommends **five physical packages** (not microservices):

| Physical package | Role |
|---|---|
| `AN_VANTARIS_IBMS-backend` | Python/Flask Core API monolith (canonical, security-hardened) |
| `AN_VANTARIS_IBMS-frontend` (future) | Vue Console SPA — sourced from `ibms_front` |
| `main` / workspace root README | Monorepo docs + orchestration only — **not** a third app unless content added |
| `contracts/` | API schemas, OpenAPI, permission matrix — documentation-only runtime |
| `docs/` | Architecture, security, split governance |

**Do not** immediately split into:

- Separate IoT service
- Separate DID service
- Separate modeling service
- Separate menu microservice

Microservice extraction requires stable contracts, observability, and ops ownership — post phase B6.

**Reference-only (not runtime):**

- `AN_VANTARIS_IBMS-ibms_backend/` — original backend snapshot
- `AN_VANTARIS_IBMS-ibms_front/` — original frontend snapshot
- Root `*.zip` archives

---

## 3. Logical Module Rule

Logical modules map to code boundaries **inside** physical packages:

| Logical module | Backend (Flask) | Frontend (Vue) |
|---|---|---|
| **Core/Auth/System** | `api/system`, `system/`, jwt/permission utils | Login, Administration, Settings |
| **Console/UI Shell** | `menu_api` | Layout, router, Home, CommandCenter |
| **Data/DB** | SQLAlchemy models, migrations | — (no direct access) |
| **IoT/Edge Interface** | `Iot/`, `api/iot`, `sse_api` | SystemsDevices, Device, IntegrationHub |
| **DID/Trust** | `DID/`, `blockchain/`, `api/did` | Blockchain/* views, did_api.js |
| **Modeling/NexusAI Interface** | `data_modeling/`, `api/data_modeling` | Intelligence, Prediction, AiVideoAnalytics |
| **Contracts/API** | Route handlers ↔ OpenAPI | `src/api/*`, request.js |
| **Simulator/Test** | `testMQTT/`, `tests/` | DeveloperCenter sandbox (mock) |
| **Storage/Artifacts** | `data/csv`, `data/models`, test media | `src/images/`, large binaries |

---

## 4. Boundary Rule

Mandatory boundaries:

1. **Frontend does not connect to DB** — all data via HTTP(S) to Core API.
2. **Backend API only** — Console uses REST/SSE endpoints under `/api`.
3. **Contracts define API boundary** — new routes require OpenAPI + permission matrix update first.
4. **Secrets via env only** — no hardcoded credentials in canonical packages (`IBMS_*` pattern).
5. **Simulator not production** — `testMQTT`, test SSE push, simulator scripts gated and excluded from prod images.
6. **Test/data artifacts not copied into runtime** unless explicitly approved (pkl, csv, mp4, large zip).
7. **Contracts package is not imported** by Python or Vue runtime — reference only.
8. **Original source packages are read-only reference** during phase B — no overwrite of hardened backend.

---

## 5. Versioning and naming

- Canonical names use `AN_VANTARIS_IBMS-*` prefix aligned with workspace.
- Original delivery names (`ibms_backend`, `ibms_front`, `ibms_main`) retained as **source snapshot** labels until B3 skeleton.
- Logical module names align with existing `IBMS_LOGICAL_MODULE_BOUNDARY_A2.md` and `IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md`.
