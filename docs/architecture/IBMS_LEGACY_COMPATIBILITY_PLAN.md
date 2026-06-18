# IBMS Legacy Compatibility Plan

## 1. Compatibility Principle

- 不删除 IBMS
- 不全局替换 `IBMS -> ONE`
- IBMS 降级为 `ibms-core`
- 保留 legacy API compatibility
- DB 表名短期保留
- 前端路由短期保留
- 新 API namespace 通过 Contracts 对齐后再新增

## 2. Compatibility Areas

### API compatibility

- 保持现有 API path 与响应契约稳定
- 新 namespace 通过并行方式引入，不破坏现有调用方

### DB compatibility

- 保持现有表名和主键策略（短期）
- 所有结构变更仅通过 migration framework 受控执行

### Frontend route compatibility

- 保持现有路由路径和页面入口
- 新命名先落在菜单与展示层，不立即改 route

### Menu compatibility

- 保持当前菜单接口与结构兼容
- 通过 `platform-core + Console` 渐进映射模块归属

### Auth/session compatibility

- 保持当前 auth/session key 与 token 处理链路
- 新信任与VC机制以兼容层方式叠加

### Deployment compatibility

- 现有部署脚本短期保留
- 后续通过包装器和版本门控逐步收敛到 ONE 模式

### Documentation compatibility

- 采用 docs-first 迁移，保留 legacy 名称说明与映射关系
- 旧文档不直接删除，按阶段标注 deprecated

## 3. Deprecation Strategy

- Stage 1: docs-first naming
- Stage 2: compatibility wrapper
- Stage 3: new namespace
- Stage 4: runtime migration
- Stage 5: legacy deprecation
- Stage 6: removal only after GA approval
