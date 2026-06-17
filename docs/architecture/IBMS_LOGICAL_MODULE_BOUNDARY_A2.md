# VANTARIS IBMS Logical Module Boundary A2

**Task:** IBMS-BOUNDARY-A2  
**Date:** 2026-06-16  
**Status:** Defined

---

## 1. Overview

本文档定义 VANTARIS IBMS 八个逻辑模块的职责边界。当前所有后端逻辑模块物理上合并在 `AN_VANTARIS_IBMS-backend` 单体内；Console 物理上位于 `AN_VANTARIS_IBMS-main`。Contracts 为独立协议目录，不参与运行时。

---

## 2. Console

**Physical Package:** `AN_VANTARIS_IBMS-main`  
**Current State:** Placeholder (README only); full UI pending implementation.

### 2.1 Responsibilities

| Area | Description |
|---|---|
| Web UI | SPA / Web application shell |
| Dashboard | Operational overview, KPI widgets |
| Asset pages | Asset list, detail, hierarchy views |
| Alarm pages | Alarm list, acknowledge, filter |
| Event / incident pages | Event timeline, incident management |
| Work order pages | WO create, assign, track, close |
| Reports | Report request UI, download via signed URL |
| Administration | User/role/site config UI (via Core API) |
| Integration status view | Link/Edge connection health display |
| System health view | Core/Data/Storage health indicators |

### 2.2 Access Rules

- ✅ **Allowed:** HTTPS calls to Backend/Core API with JWT.
- ❌ **Forbidden:** Direct access to DB, Link-like Module, Edge Interface, NexusAI Interface, Storage with long-lived credentials.

### 2.3 Current Mapping (from inventory)

| Path | Status |
|---|---|
| `AN_VANTARIS_IBMS-main/` | Placeholder — awaiting full frontend implementation |

---

## 3. Core

**Physical Package:** `AN_VANTARIS_IBMS-backend/src` (logical partition)  
**Current State:** Partially implemented — system API, DID, blockchain anchor, Flask bootstrap.

### 3.1 Responsibilities

| Area | Description |
|---|---|
| Business API | REST endpoints for all business domains |
| Auth / RBAC / tenant / site scope | JWT validation, role/permission enforcement, multi-tenant isolation |
| Asset | Asset CRUD, hierarchy, lifecycle |
| Alarm | Alarm rules, state, escalation |
| Event | Event ingestion orchestration, correlation |
| Work Order | WO lifecycle, assignment, SLA |
| Rule Engine | Business rule evaluation and triggering |
| Audit | Operation audit trail, before/after snapshots |
| Notification Intent | Create notification intents (delivery via Link) |
| Report orchestration | Trigger report generation, coordinate Storage |
| System Health | Aggregate health from Data, Link, Storage, NexusAI |
| AI orchestration | Route AI requests to NexusAI Interface, persist results |

### 3.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/main.py` | Bootstrap, lifecycle |
| `src/api/system/` | System/user/menu API |
| `src/api/did/` | Identity API |
| `src/system/` | User/system/menu services |
| `src/DID/` | DID/VC/VP services |
| `src/blockchain/` | Anchor integration |
| `src/common/utils/jwt_util.py` | Auth utilities |

### 3.3 Boundaries

- Core **owns** business decisions (create WO, execute rules, authorize actions).
- Core **delegates** persistence to Data, files to Storage, delivery to Link, inference to NexusAI.
- Core **must not** embed protocol drivers or direct OT control logic.

---

## 4. Data

**Physical Package:** `AN_VANTARIS_IBMS-backend/src` (logical partition)  
**Current State:** SQLAlchemy-based DB init present; dedicated migration/backup modules not yet separated.

### 4.1 Responsibilities

| Area | Description |
|---|---|
| ORM / Repository | Data access objects, query abstraction |
| DB connection | Connection pool, health check |
| Migration | Schema migration scripts |
| Backup / restore | Scheduled backup, restore drill |
| Retention policy | Data lifecycle, archival, purge |
| DB health | Connection status, replication lag |

### 4.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/common/core/database.py` | DB init & session |
| `src/system/dao.py`, `menu_dao.py` | System DAO |
| `src/DID/dao.py` | Identity DAO |
| `src/Iot/dao.py` | IoT DAO |
| `src/scripts/migrate_csv_data.py` | Data migration script |

### 4.3 Boundaries

- Data **does not** handle business processes.
- Data **does not** create work orders, execute rules, send notifications, or call AI.
- Data **provides** persistence primitives to Core via Repository/ORM interface.

---

## 5. Link-like Module

**Physical Package:** `AN_VANTARIS_IBMS-backend/src` (logical partition)  
**Current State:** IoT API, device drivers, SSE — embedded in backend monolith.  
**Future:** May be extracted as independent Link service.

### 5.1 Responsibilities

| Area | Description |
|---|---|
| Ingress API | External system message intake endpoints |
| External integration | CMMS, SIEM, webhook receivers |
| Message validation | Schema validation, deduplication |
| Queue-like delivery | Async message queue semantics |
| Retry semantics | Exponential backoff, dead-letter |
| Delivery status | Ack/nack tracking |
| Notification adapter | Email, Teams, SMS, webhook dispatch |
| Webhook / CMMS / SIEM / Email / Teams adapter | Protocol-specific outbound adapters |

### 5.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/api/iot/iot_api.py` | IoT HTTP ingress |
| `src/api/iot/sse_api.py` | SSE push delivery |
| `src/Iot/` | Device management layer |
| `src/Iot/drivers/` | Protocol drivers (MQTT, HTTP, Modbus, etc.) |

### 5.3 Boundaries

- Link **does not** directly write Business DB.
- Link **does not** directly create work orders.
- Link **does not** directly execute Core business rules.
- Link **delivers** validated events/messages to Core via internal API.
- Link **executes** notification delivery based on Core intents.

---

## 6. Edge Interface

**Physical Package:** `AN_VANTARIS_IBMS-backend/src` (logical partition)  
**Current State:** Not an independent Edge Agent; simulators and import adapters only.

### 6.1 Responsibilities

| Area | Description |
|---|---|
| Edge registration API | Register edge nodes, heartbeat |
| Import adapter | Bulk data import from edge sources |
| Simulated device data | MQTT/HTTP/RTSP/ISUP simulators for dev/test |
| Future Edge Agent contract | Protocol spec for real edge agents |

### 6.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/testMQTT/` | Device simulators (HVAC, air quality, RTSP, ISUP, ISAPI) |
| `src/Iot/drivers/` | Protocol adapters serving as edge ingress |
| `src/Iot/device_manager.py` | Device registration & lifecycle |

### 6.3 Boundaries

- Edge Interface **does not** implement real PLC control.
- Edge Interface **does not** modify OT devices.
- Edge Interface **forwards** ingested data to Link-like/Core boundary via controlled API.
- Real Edge Agent deployment is a **future** concern.

---

## 7. NexusAI Interface

**Physical Package:** `AN_VANTARIS_IBMS-backend/src` (logical partition)  
**Current State:** Data modeling / HVAC ML predictor embedded in backend.

### 7.1 Responsibilities

| Area | Description |
|---|---|
| AI triage request | Classify/prioritize alarms and events |
| Summary request | Generate incident/event summaries |
| Recommendation request | Suggest remediation actions |
| RCA suggestion request | Root cause analysis suggestions |
| AI result storage through Core | Results persisted only via Core orchestration |

### 7.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/data_modeling/` | Modeling service & predictors |
| `src/data_modeling/predictors/hvac_sim_001.py` | HVAC ML predictor |
| `src/api/data_modeling/modeling_api.py` | Modeling API ingress |
| `data/models/hvac.pkl` | ML model artifact |

### 7.3 Boundaries

- NexusAI **does not** directly create work orders.
- NexusAI **does not** directly write Business DB.
- NexusAI **does not** bypass user permissions — all requests authenticated via Core.
- NexusAI **does not** hold long-lived MinIO/storage keys.

---

## 8. Storage

**Physical Package:** `AN_VANTARIS_IBMS-backend` (logical partition)  
**Current State:** Local CSV and model file storage; MinIO integration planned.

### 8.1 Responsibilities

| Area | Description |
|---|---|
| Attachment | User-uploaded files, evidence attachments |
| Screenshot | Alarm/event screenshots |
| Evidence package | Bundled evidence for incidents |
| Report file | Generated report PDF/Excel/CSV |
| Object metadata | File metadata, versioning, retention |
| Short-lived signed URL policy | Time-limited download/upload URLs |

### 8.2 Current Mapping

| Path | Module Area |
|---|---|
| `src/data_modeling/csv_storage.py` | CSV file storage adapter |
| `data/csv/` | Simulation/training data files |
| `data/models/` | ML model files |

### 8.3 Boundaries

- Console **does not** hold long-lived MinIO keys.
- NexusAI **does not** hold long-lived MinIO keys.
- Storage **does not** make business permission decisions — Core authorizes, Storage executes.
- All upload/download operations **must** be audited.

---

## 9. Contracts

**Physical Package:** `contracts/` (root, documentation-only)  
**Current State:** Placeholder directories initialized in A0–A3 phase.

### 9.1 Responsibilities

| Area | Description |
|---|---|
| JSON Schema | Request/response payload schemas |
| OpenAPI | REST API specifications |
| Error codes | Standardized error code registry |
| Status machine | Entity state transition definitions |
| Examples | Sample payloads for integration |
| Version policy | Semantic versioning, deprecation policy |

### 9.2 Boundaries

- Contracts **does not run** — no runtime process.
- Contracts **does not** hold business logic.
- Contracts **does not** directly connect to database.
- All cross-module interfaces **will eventually** be registered in Contracts.

---

## 10. Module Interaction Summary

```
Console ──(HTTPS/JWT)──▶ Core
                           │
              ┌────────────┼────────────┬──────────────┐
              ▼            ▼            ▼              ▼
            Data        Storage    NexusAI         Link-like
                                              ▲         │
                                              │         ▼
                                       Edge Interface  External Systems
```

All interfaces marked with dashed future boundaries will be formalized in `contracts/` during IBMS-CONTRACTS-A0/A1.

---

## 11. Related Documents

- [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](./IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md)
- [IBMS_CODE_INVENTORY_A1.md](./IBMS_CODE_INVENTORY_A1.md)
- [IBMS_MODULAR_BOUNDARY_A0.md](./IBMS_MODULAR_BOUNDARY_A0.md)
