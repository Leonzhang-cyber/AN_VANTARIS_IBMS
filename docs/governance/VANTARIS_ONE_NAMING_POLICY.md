# VANTARIS ONE Naming Policy

## 1. Product Brand

- 正式对外产品名: `VANTARIS ONE`
- 英文定位: `Unified Intelligent Building & Facility Operations Platform`
- 中文定位: `全向智能建筑与设施运营平台`

## 2. Engineering Platform Name

- 目标工程平台名: `AN_VANTARIS_ONE`

## 3. Legacy Source Name

- 当前工程名: `AN_VANTARIS_IBMS`
- 定位: legacy workspace / current implementation base / migration source

## 4. Core Module Names (Frozen)

- `AN_VANTARIS_EDGE`
- `AN_VANTARIS_LINK`
- `AN_VANTARIS_Code`
- `AN_VANTARIS_Console`
- `AN_VANTARIS_NexusAI`
- `AN_VANTARIS_DB`
- `AN_VANTARIS_Contracts`

## 5. Business Module Names (Frozen)

- `ibms-core`
- `asset-topology`
- `integration-management`
- `alarm-event`
- `mms`
- `esg`
- `digital-twin`
- `command-center`
- `cde-traceability`
- `reports`
- `notification`
- `evidence`
- `ufms-adapter`
- `nexus-ai-adapter`
- `edge-link-adapter`

## 6. Naming Principle

- `VANTARIS ONE` 是总平台（platform umbrella）
- `IBMS` 在新治理下是平台内业务模块（`ibms-core`），不再作为总平台名
- `UFMS` 是独立故障/风险智能引擎或外部 adapter，不能直接混入 ONE runtime
- `Edge / Link / DB / Console / NexusAI / Contracts` 是共享平台底座能力
- 不允许继续使用 `IBMS` 表示总平台
- 不允许把 `UFMS` 内部代码复制进 ONE
- 不允许一次性全局替换 `IBMS -> ONE`
