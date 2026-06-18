# IBMS Core Module Plan

## 1. Position

`ibms-core` 是 VANTARIS ONE 的核心业务模块之一，不再代表整个平台。  
VANTARIS ONE 是平台，`ibms-core` 是楼宇与设施运营业务域。  
`ibms-core` 依赖平台能力，但不能拥有 Edge、Link、DB、NexusAI、Console、Contracts 的底座职责。

## 2. Included Capabilities

`ibms-core` 可包含：

- building operation overview
- asset/device operation views
- system status
- building system dashboard
- facility operation workflows
- alarm/event workspace as business view
- integration overview as business view
- reporting views
- basic operational configuration
- module-level menu entries

## 3. Excluded Capabilities

`ibms-core` 不包含：

- protocol driver runtime
- Edge connector runtime
- Link reliable delivery
- DB migration ownership
- platform auth core
- global license center
- global patch center
- NexusAI inference runtime
- CDE platform evidence chain ownership
- UFMS internal runtime
- direct DB schema mutation of other modules

## 4. Relationship with Other Modules

- `asset-topology` provides asset/device/point foundation
- `integration-management` owns source systems/connectors/tag mapping configuration
- `alarm-event` owns normalized alarms/events
- `mms` owns work orders/maintenance plans
- `esg` owns energy/sustainability readings and reports
- `cde-traceability` owns decision/evidence chain
- `NexusAI` provides AI inference through adapter
- `Edge/Link` provide data acquisition and delivery
- `Console` manages module/license/patch/admin control plane
- `Contracts` governs all cross-module objects and APIs

## 5. Migration Principle

- keep legacy IBMS runtime stable
- docs-first mapping
- no global rename
- no DB rename
- no API breaking change
- migrate by module boundary
- introduce compatibility wrappers before changing runtime paths
- remove legacy only after GA approval
