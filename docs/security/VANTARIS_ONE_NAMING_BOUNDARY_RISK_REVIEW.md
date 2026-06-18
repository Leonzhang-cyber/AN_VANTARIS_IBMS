# VANTARIS ONE Naming Boundary Risk Review

## 1. Risk: global rename breaks runtime

一次性全局替换 `IBMS -> ONE` 会导致 import、配置、脚本、文档引用同时失效，形成不可控回归。

## 2. Risk: DB table rename breaks migration

提前重命名表/字段会破坏既有 schema 与迁移链，导致迁移不可重复和环境不一致。

## 3. Risk: API rename breaks frontend/backend compatibility

提前改 API namespace 或 path 会让前后端、contracts、已有客户端同时断裂。

## 4. Risk: UFMS/IBMS contamination

将 UFMS runtime/source/schema/auth/login/seed/migration 直接混入 ONE 会破坏系统边界与审计可追溯性。

## 5. Risk: Edge/Link naming collision

平台共享层 (`Edge`, `Link`) 与业务层命名若不冻结，易出现模块职责重叠与路由冲突。

## 6. Risk: license/patch feature naming drift

补丁、授权、特性交付若沿用混杂命名，会导致发布、计费、审计口径不一致。

## Controls

- no global replace
- docs-first rename
- compatibility layer
- module naming freeze
- DB rename only via migration framework
- API namespace only after Contracts alignment
- UFMS only through adapter contract
