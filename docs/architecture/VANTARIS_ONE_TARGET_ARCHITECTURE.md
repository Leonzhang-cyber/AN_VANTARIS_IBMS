# VANTARIS ONE Target Architecture

## 1. Platform Definition

VANTARIS ONE 是统一智能建筑与设施运营平台，不是传统单体 IBMS。  
IBMS 是 VANTARIS ONE 内的 `ibms-core` 业务模块。  
UFMS 是独立故障与风险智能引擎，或通过 `ufms-adapter` 接入，不直接混入 ONE runtime。

## 2. Target 6+1 Engineering Assets

冻结结构如下：

- `AN_VANTARIS_EDGE`
- `AN_VANTARIS_LINK`
- `AN_VANTARIS_Code`
- `AN_VANTARIS_Console`
- `AN_VANTARIS_NexusAI`
- `AN_VANTARIS_DB`
- `AN_VANTARIS_Contracts`

说明：

- 前 6 个为运行模块（runtime modules）
- `AN_VANTARIS_Contracts` 为工程契约资产，不一定作为客户现场独立运行包，但必须作为 API / Schema / Event / Patch / License / DID / VC 的唯一契约源

## 3. High-level Data Path

标准数据路径：

`Device / BMS / FAS / ACS / CCTV / Lift / PLC / SCADA / IoT`
`-> AN_VANTARIS_EDGE`
`-> AN_VANTARIS_LINK`
`-> AN_VANTARIS_Code`
`-> AN_VANTARIS_DB`
`-> Console / NexusAI / CDE / MMS / ESG / UFMS Adapter`

## 4. Module Responsibility Summary

### AN_VANTARIS_EDGE

- 多协议接入
- 多设备接入
- 协议插件
- 自定义协议
- tag mapping
- data normalization
- local buffer
- edge rule
- edge health
- diagnostics
- 不直接写 ONE DB

### AN_VANTARIS_LINK

- secure delivery
- envelope validation
- schema validation
- ACK / retry / DLQ / replay
- 断线续传接收
- route policy
- audit
- HA / failover
- 不做业务逻辑
- 不直接写业务 DB

### AN_VANTARIS_Code

- business runtime
- platform-core
- module registry
- license gate
- patch manager
- migration guard
- `ibms-core / mms / esg / cde / reports / notification`
- API host

### AN_VANTARIS_Console

- control plane
- user / role / permission
- module management
- license center
- patch center
- Edge/Link/DB/AI admin
- audit export
- backup/restore admin

### AN_VANTARIS_NexusAI

- AI gateway
- RCA
- RAG
- model registry
- AI safety guard
- edge AI manager
- inference trace to CDE
- 不直接修改业务 DB

### AN_VANTARIS_DB

- PostgreSQL data foundation
- schemas
- migrations
- backup/restore
- schema version
- audit archive
- trust / hash anchor tables

### AN_VANTARIS_Contracts

- object model
- API contracts
- event contracts
- edge/link envelope
- module manifest
- patch manifest
- license VC
- DID / VC
- AI request/response
- CDE schema
- error/status code
- ports/security/versioning
