# IBMS Core License / Patch / Menu Policy

## 1. License

`ibms-core` 未来应作为 license feature：

`feature.ibms_core.enabled`

可选子功能：

- `feature.ibms_core.dashboard`
- `feature.ibms_core.asset_view`
- `feature.ibms_core.alarm_view`
- `feature.ibms_core.reporting`
- `feature.ibms_core.integration_view`

不得把 Edge/Link/NexusAI/DB/Console 管理权限包含在 `ibms-core` license 内。

## 2. Patch

`ibms-core` patch 只能修改：

- `ibms-core` business UI
- `ibms-core` business service
- `ibms-core` module config
- `ibms-core` reports/views

不得修改：

- Edge runtime
- Link runtime
- DB migration unless separately approved
- global auth
- global license center
- global patch center
- NexusAI runtime
- UFMS runtime

## 3. Menu

`ibms-core` 菜单应作为业务模块菜单，不应继续代表整个平台。

Allowed menu areas:

- Dashboard
- Operations
- Assets & Topology business view
- Alarms & Events business view
- Reports

Forbidden:

- Edge Admin
- Link Admin
- DB Admin
- Global License Center
- Patch Center
- NexusAI Admin
- Trust/DID/VC Admin

## 4. Role Permission

权限应使用 module-scoped permission：

- `ibms.core.view`
- `ibms.core.operate`
- `ibms.core.configure`
- `ibms.core.report.export`

不得使用平台超级权限替代模块权限。
