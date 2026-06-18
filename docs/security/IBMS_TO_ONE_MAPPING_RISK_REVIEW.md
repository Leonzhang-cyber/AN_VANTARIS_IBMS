# IBMS to ONE Mapping Risk Review

## 1. Wrong module ownership risk

- description: 映射阶段若把能力归属到错误模块，会导致后续拆分方向偏离
- impact: 架构重工、责任边界失真
- control: A1/A2 frozen naming + A3 evidence-based path mapping
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 2. Hidden runtime coupling risk

- description: backend 内存在跨域调用与隐式依赖，路径盘点无法完全揭示
- impact: 迁移时出现不可预期故障
- control: 分阶段拆分 + compatibility wrapper + integration smoke
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 3. Protocol driver DB/UI coupling risk

- description: drivers 当前位于 backend runtime，可能耦合 DAO、API、SSE、模型层
- impact: EDGE 抽取中断或行为漂移
- control: 先契约化再插件化抽取，不直接搬迁耦合代码
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 4. API compatibility break risk

- description: 过早更改 API path/namespace 会破坏前后端兼容
- impact: 控制台与集成端请求失败
- control: 保持 legacy API，A4 合同对齐后再增量 namespace
- current status: Controlled by rule
- next mitigation task: `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT`

## 5. DB migration break risk

- description: 在映射阶段改表名/迁移ID会破坏迁移连续性
- impact: 环境不可重放、数据风险上升
- control: DB rename only via migration framework, staged approval
- current status: Controlled by rule
- next mitigation task: `REBRAND-ONE-A1`

## 6. UFMS contamination risk

- description: 将 UFMS runtime/source/schema/auth/login/seed/migration 混入 ONE
- impact: 边界破坏和安全合规失败
- control: UFMS only through adapter contract, stop-on-detection policy
- current status: Monitored
- next mitigation task: `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT`

## 7. Naming drift risk

- description: 团队在不同文档或模块中采用不一致命名
- impact: 资产归属和交付口径冲突
- control: A1 naming policy + decision matrix governance
- current status: Open
- next mitigation task: `ONE-TRANSITION-A7-REBRAND-READINESS`

## 8. Frontend menu drift risk

- description: 菜单、路由、权限映射不同步导致导航断层
- impact: 功能不可达与权限绕行风险
- control: menu compatibility first, route stability until contracts align
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 9. Security boundary drift risk

- description: 模块边界和安全域划分不一致，可能出现跨模块越权
- impact: 访问控制与审计链断裂
- control: module boundary governance + adapter-only cross-boundary access
- current status: Open
- next mitigation task: `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT`

## 10. Audit evidence loss risk

- description: 迁移过程中审计和证据链字段未统一映射
- impact: 合规审计不可追溯
- control: cde-traceability ownership + hash/evidence contract first
- current status: Open
- next mitigation task: `ONE-TRANSITION-A4-CONTRACTS-ONE-ALIGNMENT`
