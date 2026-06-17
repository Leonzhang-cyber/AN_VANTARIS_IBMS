# IBMS API Groups

**Task:** IBMS-CONTRACTS-A0  
**Source:** Backend inventory B2 (`47d2667`)  
**Status:** Grouping defined — OpenAPI generation deferred to A1

---

## Overview

当前 backend 通过单一 Flask Blueprint `api_bp`（prefix `/api`）注册所有路由。以下分组按 **逻辑模块** 和 **Contracts 域** 划分，供 A1 OpenAPI 与 Schema 工作使用。

---

## 1. DID API

### Current Prefix

```
/api/did/*
```

### Representative Routes (from B2)

| Route | Method | Notes |
|---|---|---|
| `/api/did/system/init` | POST | System root entity init |
| `/api/did/entity` | POST | Create sub-entity + issue VC |
| `/api/did/vp/generate` | POST | Verifiable Presentation |
| `/api/did/vp/verify` | POST | VP verification |
| `/api/did/vc/reissue` | POST | VC reissue |
| `/api/did/vc/revoke` | POST | VC revoke |
| `/api/did/vc/status` | POST | VC status |
| `/api/did/challenge` | GET | Auth challenge |
| `/api/did/subordinates/*` | GET | Hierarchy queries |
| `/api/did/entity/<did>` | GET | Entity detail |
| `/api/did/login` | POST | **Login → JWT** |
| `/api/did/me` | GET | Current user (`@jwt_required`) |
| `/api/did/chain/*` | GET | Blockchain anchor queries |
| `/api/did/verify/entity/<did>` | GET | Entity verification |

### Logical Module

**Core / Security / DID**

### Contracts Domain

`did.*` — schemas, OpenAPI file: `ibms-did-api.openapi.yaml`

### Current Risk

| Risk | Detail |
|---|---|
| JWT issuance | `/api/did/login` produces bearer token — must be contract-defined |
| DID/VC/VP operations | Cryptographic boundary; parent private key in request body |
| Blockchain anchoring | Chain queries coupled to identity layer |
| Auth coverage | Most routes lack `@jwt_required` — boundary verification needed |
| Private key exposure | Startup may print system root private key |

---

## 2. System API

### Current Prefix

```
/api/system/*
```

Includes:

- `/api/system/entity-types` — entity type CRUD
- `/api/system/permissions` — permission CRUD
- `/api/system/*-standard-fields*` — standard field definitions
- `/api/system/*-standard-methods*` — standard method definitions
- `/api/system/versions` — menu version management
- `/api/system/menus*` — menu CRUD
- `/api/system/menu/*` — menu config, init-data
- `/api/system/version-menus/*` — version-menu sync

### Logical Module

**Core / System Administration**

### Contracts Domain

`system.*` — OpenAPI file: `ibms-system-api.openapi.yaml`

### Current Risk

| Risk | Detail |
|---|---|
| Raw SQL | `menu_api.py` uses extensive `text()` SQL — not Repository-isolated |
| Permission boundary | Permission CRUD exists but menu/IoT routes unprotected |
| RBAC | **RBAC boundary not fully confirmed** across all system routes |
| Partial JWT | `system_api.py` protected; `menu_api.py` **not** protected |

---

## 3. IoT API

### Current Prefix

```
/api/iot/*
```

### Representative Routes (from B2)

| Route | Method | Notes |
|---|---|---|
| `/api/iot/device/register` | POST | Device registration |
| `/api/iot/device/*` | GET/PUT/PATCH/DELETE | Device CRUD |
| `/api/iot/standard-fields` | GET/POST/PUT/DELETE | Field definitions |
| `/api/iot/standard-methods` | GET/POST/PUT/DELETE | Method definitions |
| `/api/iot/device/*/command` | POST | **Device command** |
| `/api/iot/ingest/http` | POST | **HTTP telemetry ingress** |
| `/api/iot/device/*/reconnect` | POST | Driver reconnect |
| `/api/iot/*/field-mappings-info` | GET | Mapping metadata |
| `/api/iot/*/method-mappings-info` | GET | Mapping metadata |

### Logical Module

**Link-like Module / Edge Interface / Core** (device registry spans Core + Link)

### Contracts Domain

`iot.*` — OpenAPI file: `ibms-iot-api.openapi.yaml`

### Current Risk

| Risk | Detail |
|---|---|
| Telemetry ingress | `/api/iot/ingest/http` — unauthenticated external intake |
| Device command | Command APIs must require explicit permission |
| MQTT credentials | Hardcoded in config/simulators — must externalize |
| Driver boundary | Protocol drivers embed OT connectivity logic |
| No JWT | All IoT routes lack `@jwt_required` in B2 |

---

## 4. SSE / Streaming API

### Current Prefix

```
/api/iot/device/<device_code>/stream
/api/iot/device/<device_code>/latest
/api/iot/device/<device_code>/test-sse-push
```

### Logical Module

**Link-like / Core realtime delivery**

### Contracts Domain

`iot.stream.*` or `link.stream.*` — may share `ibms-iot-api.openapi.yaml` or separate streaming spec

### Current Risk

| Risk | Detail |
|---|---|
| Auth boundary | SSE endpoints lack JWT — must be reviewed |
| Rate limiting | Connection count and per-device limits needed |
| CORS | OPTIONS handler present — production policy TBD |
| Test endpoint | `/test-sse-push` must not be public in production |

---

## 5. Data Modeling API

### Current Prefix

```
/api/modeling/*
```

### Representative Routes (from B2)

| Route | Method | Notes |
|---|---|---|
| `/api/modeling/csv/list` | GET | List CSV datasets |
| `/api/modeling/csv/<device_code>` | GET | CSV stats |
| `/api/modeling/<device_code>/train` | POST | **Train model** |
| `/api/modeling/<device_code>/predict` | POST | Single predict |
| `/api/modeling/<device_code>/predict_future` | POST | Multi-day forecast |
| `/api/modeling/<device_code>/model_info` | GET | Model metadata |
| `/api/modeling/<device_code>/<method>` | GET/POST | Generic predictor call |

### Logical Module

**NexusAI Interface / Data Modeling**

### Contracts Domain

`modeling.*` — OpenAPI file: `ibms-modeling-api.openapi.yaml`

### Current Risk

| Risk | Detail |
|---|---|
| No JWT | **Modeling API JWT protection not confirmed** — train/predict publicly reachable |
| Model artifacts | `*.pkl` must not be committed; access via Storage policy |
| Resource abuse | Training endpoint can consume CPU — rate limit required |
| Data leakage | CSV list exposes device telemetry summaries |

---

## 6. Simulator / testMQTT Routes

### Current Location

```
src/testMQTT/*
```

Includes standalone Flask apps (e.g. `mock_isapi_camera.py` with `/ISAPI/*` routes) and CLI simulators (MQTT, RTSP, ISUP, HVAC).

### Logical Module

**Edge Simulator / Test Tooling**

### Contracts Domain

**None for production** — optional `ibms-edge-simulator.openapi.yaml` for dev-only documentation

### Current Risk

| Risk | Detail |
|---|---|
| Not production API | Must not be treated as Core/Link contract surface |
| Isolation | Simulators must not run in production runtime |
| Hardcoded credentials | MQTT username/password in simulator source |
| Standalone Flask | Mock ISAPI runs separate app — not on `api_bp` |

---

## 7. Cross-Group Summary

| Group | Prefix | Module | OpenAPI (future) | Auth Status (B2) |
|---|---|---|---|---|
| DID | `/api/did/*` | Core / Security | `ibms-did-api.openapi.yaml` | Partial |
| System | `/api/system/*` | Core | `ibms-system-api.openapi.yaml` | Partial (menu unprotected) |
| IoT | `/api/iot/*` | Link-like / Edge | `ibms-iot-api.openapi.yaml` | Unprotected |
| SSE | `/api/iot/device/*/stream` | Link-like | (shared or separate) | Unprotected |
| Modeling | `/api/modeling/*` | NexusAI | `ibms-modeling-api.openapi.yaml` | Unprotected |
| Simulator | `testMQTT/*` | Edge (dev) | Dev-only | N/A |

---

## 8. Future Console API Layer

Console will consume aggregated **Core API** surface. Future files:

- `ibms-core-api.openapi.yaml` — Core-orchestrated business API (future)
- `ibms-console-api.openapi.yaml` — Console-specific client contract (future)

Console **must not** call IoT ingress, modeling, or simulator routes directly per A2 forbidden access matrix.
