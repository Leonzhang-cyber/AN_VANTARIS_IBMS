# IBMS Core Domain Boundary

## 1. Domain Objects Owned by ibms-core

`ibms-core` 仅拥有业务视图与配置类对象，例如：

- IBMS dashboard layout
- IBMS operation profile
- IBMS system view
- IBMS module menu configuration
- IBMS view preferences
- IBMS operational KPI view

## 2. Domain Objects Not Owned by ibms-core

- Site / Building / Floor / Space / Asset / Device / Point: `asset_foundation` / `asset-topology`
- Gateway / Connector / SourceSystem / TagMapping: `integration-management` / Edge config domain
- Telemetry / Event / Alarm: `event_alarm`
- FaultCase: `ufms-adapter` / fault intelligence boundary or `event_alarm` depending future contract
- WorkOrder / Inspection / MaintenancePlan: `mms`
- ESG readings/report: `esg`
- AI model/inference/job: `ai` / `NexusAI`
- CDE case/step/evidence/hashAnchor: `cde-traceability`
- License / Patch / DID / VC: `platform_core` / trust
- User / Role / Permission: `platform_core` / `Console`

## 3. API Boundary

`ibms-core` API 未来目标 namespace：

`/api/v1/ibms/*`

但当前 legacy API 不立即改名。  
新 namespace 只能在 Contracts approval 后新增。  
旧 API 保留 compatibility。

## 4. UI Boundary

`ibms-core` UI 可以出现在：

- Dashboard
- Operations
- Assets & Topology business views
- Alarms & Events business views
- Reports

但不应把 Console、Edge Admin、Link Admin、DB Admin、NexusAI Admin 混入 `ibms-core`。

## 5. DB Boundary

短期不改现有表名。  
长期可进入：

- `ibms_core` schema/domain
- `legacy_ibms` compatibility layer

DB 迁移必须通过 `AN_VANTARIS_DB` 和 Contracts，不由 `ibms-core` 私自完成。
