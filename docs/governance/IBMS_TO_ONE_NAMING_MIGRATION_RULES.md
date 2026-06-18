# IBMS to ONE Naming Migration Rules

## 1. 可以先改的命名

- 文档标题
- 产品说明
- 架构图说明
- `README` 中的平台定位
- Contracts `productFamily`
- Console 显示名
- 新模块说明

## 2. 不能立即改的命名

- DB table names
- migration id
- Python import path
- frontend route
- existing API path
- auth/session key
- existing deployment script
- legacy compatibility docs

## 3. 保留兼容命名

- `ibms-core`
- `legacy_ibms`
- `IBMS Adapter`
- `IBMS Domain`
- `legacy IBMS API compatibility`

## 4. 禁止操作

- 禁止全局搜索替换 `IBMS` 为 `ONE`
- 禁止删除 `IBMS` 业务域
- 禁止在同一 commit 中混合 rebrand + DB migration + runtime refactor
- 禁止将 `UFMS` runtime/source/schema/auth/login/seed/migration 混入 ONE

## 5. 分阶段改名路线

- `A1` naming governance
- `A2` target architecture
- `A3` legacy module mapping
- `A4` contracts ONE alignment
- `A5` skeleton
- `A6` ibms-core module plan
- `A7` rebrand readiness
- 后续 `REBRAND-ONE-A0/A1/A2`
