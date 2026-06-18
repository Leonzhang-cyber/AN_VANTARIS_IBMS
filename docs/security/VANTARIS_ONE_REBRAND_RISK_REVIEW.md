# VANTARIS ONE Rebrand Risk Review

## 1. Premature runtime rename

- description: 未完成契约与边界前提前改 runtime 名称/路径
- impact: 构建与运行链路中断
- control: docs-only first, runtime rename only in later approved phases
- current status: Open
- next mitigation task: `REBRAND-ONE-R0-DOCS-BRAND-ALIGNMENT`

## 2. Global replace damage

- description: 全局替换 IBMS->ONE 导致隐性路径和语义破坏
- impact: 大范围回归与不可控差异
- control: no global replace policy + phased commits
- current status: Controlled by governance
- next mitigation task: `REBRAND-ONE-R0-DOCS-BRAND-ALIGNMENT`

## 3. API compatibility break

- description: 提前改 API path/namespace 破坏前后端兼容
- impact: 调用失败与功能中断
- control: namespace introduction after contracts baseline and compatibility wrapper
- current status: Open
- next mitigation task: `CONTRACTS-A0-MANIFEST-BASELINE`

## 4. DB migration break

- description: 未经 DB 合同与迁移计划改表名/结构
- impact: 迁移链断裂与数据风险
- control: DB changes via AN_VANTARIS_DB + migration contract only
- current status: Open
- next mitigation task: `DB-SCHEMA-BASELINE`

## 5. Frontend route break

- description: 路由改名早于兼容层与菜单策略
- impact: 页面不可达和用户混乱
- control: legacy route compatibility until validated cutover
- current status: Open
- next mitigation task: `CODE-MODULE-A0`

## 6. Package boundary confusion

- description: 模块职责重叠导致 ownership 漂移
- impact: 迁移顺序失控
- control: enforce A2/A6 boundary docs and module registry plan
- current status: Open
- next mitigation task: `CODE-MODULE-A0`

## 7. Edge source missing

- description: Edge runtime package不存在，源抽取尚未执行
- impact: Edge roadmap不可落地
- control: dedicated source audit before extraction
- current status: Open
- next mitigation task: `EDGE-SOURCE-AUDIT`

## 8. Link source missing

- description: Link runtime package不存在，契约域未转化为实现
- impact: delivery layer readiness不足
- control: link contract baseline first, then implementation
- current status: Open
- next mitigation task: `LINK-A0`

## 9. Contracts partial coverage

- description: contracts 域仍为 PARTIAL，关键 schema 缺口存在
- impact: runtime 对齐和 API 引入受阻
- control: prioritize P0 contract backlog and manifest policy
- current status: Open
- next mitigation task: `CONTRACTS-A0-MANIFEST-BASELINE`

## 10. UFMS contamination

- description: UFMS runtime/source/schema/auth/login/seed/migration 混入 ONE
- impact: 边界污染与合规风险
- control: adapter-only rule + stop-on-detection guard
- current status: Monitored
- next mitigation task: `UFMS-ADAPTER-CONTRACT-A0`

## 11. License/patch naming drift

- description: license/patch 标识与模块命名不一致
- impact: 发布与授权口径冲突
- control: module-scoped feature keys and manifest governance
- current status: Open
- next mitigation task: `LICENSE-A0`

## 12. Audit evidence gap

- description: 迁移阶段证据与审计记录不完整
- impact: 追溯能力下降
- control: evidence report gate per phase and CDE trace policy
- current status: Open
- next mitigation task: `CDE-CONTRACT-A0`

## 13. Rollback not tested

- description: 回滚计划存在但未演练
- impact: 出现问题时恢复不确定
- control: phase rollback drill before runtime migration
- current status: Open
- next mitigation task: `ROLLBACK-DRILL-A0`

## 14. Deployment mismatch

- description: rebrand 后部署元数据与服务拓扑不一致
- impact: 环境部署失败或配置漂移
- control: deployment alignment in R6 with explicit port/service matrix
- current status: Open
- next mitigation task: `DEPLOYMENT-ALIGN-A0`
