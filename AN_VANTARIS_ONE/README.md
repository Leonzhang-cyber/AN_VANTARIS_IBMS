# VANTARIS ONE

VANTARIS ONE is the Unified Intelligent Building & Facility Operations Platform.

中文定位：

VANTARIS ONE 是全向智能建筑与设施运营平台。

## A5 Skeleton Notice

- 当前目录是目标架构骨架，不是当前 production runtime
- 当前生产/开发基础仍在 `AN_VANTARIS_IBMS` 现有目录中
- IBMS 将作为 `ibms-core` 业务模块迁入 VANTARIS ONE
- 当前骨架只用于后续模块迁移、审计和边界冻结
- 不允许直接把 backend/frontend 源码复制进来
- 不允许在 skeleton 内直接引入 UFMS runtime
- 不允许把 skeleton 当作已完成可运行平台

## 6+1 Target Packages

- `AN_VANTARIS_EDGE`
- `AN_VANTARIS_LINK`
- `AN_VANTARIS_Code`
- `AN_VANTARIS_Console`
- `AN_VANTARIS_NexusAI`
- `AN_VANTARIS_DB`
- `AN_VANTARIS_Contracts`
