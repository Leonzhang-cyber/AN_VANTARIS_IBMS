# IBMS to ONE Migration Decision Matrix

| Decision Area | Recommended Decision | Reason | Blocker | Next Task |
| ------------- | -------------------- | ------ | ------- | --------- |
| whether to rename root directory now | NO, later | 当前仍是 legacy workspace，立即改根目录会破坏路径与脚本 | runtime/import/deploy coupling | `ONE-TRANSITION-A7-REBRAND-READINESS` |
| whether to create AN_VANTARIS_ONE skeleton now | YES in A5, not A3 | A3 仅盘点映射，不创建骨架 | A3 scope freeze | `ONE-TRANSITION-A5-SKELETON` |
| whether to move backend now | NO | backend 仍承载 API 与核心业务，迁移需先完成边界拆分 | hidden runtime coupling | `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN` |
| whether to move frontend now | NO | frontend 路由和菜单兼容要求仍在 | route/menu compatibility | `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN` |
| whether to extract EDGE now | after source confirmation | driver 在 backend 内且与 dao/service/api 存在耦合 | protocol-driver coupling | `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN` |
| whether to introduce LINK now | later | Link 需依赖 route policy 与 envelope contract 完整定义 | contracts and delivery policy pending | `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT` |
| whether to rename DB tables now | NO | 现阶段禁止直接重命名，避免迁移链断裂 | migration safety | `REBRAND-ONE-A1` |
| whether to rename API paths now | NO | 前后端兼容和合同稳定优先 | API compatibility risk | `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT` |
| whether to freeze module registry now | YES, planning in A6 | 需要先冻结逻辑归属，避免后续漂移 | module ownership not yet formalized in runtime | `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN` |
| whether to align Contracts next | YES in A4 | Contracts 是统一命名和接口演进锚点 | A4 not executed yet | `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT` |
