# IBMS Core Module Risk Review

## 1. IBMS remains incorrectly treated as total platform

- description: 迁移后仍把 IBMS 作为平台总入口而非业务模块
- impact: 平台边界失真与治理冲突
- control: enforce A1 naming governance and module registry scope
- current status: Open
- next mitigation task: `ONE-TRANSITION-A7-REBRAND-READINESS`

## 2. Platform-core mixed into ibms-core

- description: platform-core 职责误并入 ibms-core
- impact: 模块职责混乱和升级耦合
- control: keep platform-core ownership in `AN_VANTARIS_Code` shared layer
- current status: Open
- next mitigation task: `CODE-MODULE-A0`

## 3. Edge driver runtime mixed into ibms-core

- description: 协议驱动与连接器逻辑混入 ibms-core
- impact: 业务模块承载基础集成风险
- control: Edge extraction after dedicated source audit
- current status: Open
- next mitigation task: `EDGE-SOURCE-AUDIT`

## 4. Link delivery logic mixed into ibms-core

- description: ACK/retry/DLQ/replay 被放入 ibms-core
- impact: 业务层承担传输可靠性复杂度
- control: Link contracts and Link module boundary first
- current status: Open
- next mitigation task: `LINK-A0`

## 5. DB migration owned by ibms-core

- description: ibms-core 自行主导 DB migration 与 schema rename
- impact: 迁移链破坏和跨域冲突
- control: DB changes only via `AN_VANTARIS_DB` + Contracts
- current status: Controlled by policy
- next mitigation task: `DB-SCHEMA-BASELINE`

## 6. API compatibility broken during extraction

- description: 提前替换 legacy API path 导致调用方中断
- impact: 前后端与集成接口失效
- control: compatibility wrapper and staged namespace introduction
- current status: Open
- next mitigation task: `ONE-TRANSITION-A7-REBRAND-READINESS`

## 7. Menu drift / user confusion

- description: 菜单重构与模块归属不同步
- impact: 用户认知混乱与功能可达性问题
- control: module-scoped menu policy and staged console mapping
- current status: Open
- next mitigation task: `ONE-TRANSITION-A7-REBRAND-READINESS`

## 8. License scope too broad

- description: ibms-core license 误覆盖平台管理能力
- impact: 授权模型越权与计费边界不清
- control: feature-scoped license keys and exclusion rules
- current status: Open
- next mitigation task: `LICENSE-A0`

## 9. Patch modifies forbidden platform areas

- description: ibms-core patch 混入 Edge/Link/DB/Auth 全局改动
- impact: 变更不可控和回滚风险上升
- control: patch scope policy and separated commit gates
- current status: Open
- next mitigation task: `PATCH-POLICY-A0`

## 10. UFMS runtime contamination

- description: UFMS runtime/source/schema/auth/login/seed/migration 混入 ibms-core
- impact: 边界污染与安全审计失败
- control: ufms-adapter-only boundary, strict stop-on-detection
- current status: Monitored
- next mitigation task: `UFMS-ADAPTER-CONTRACT-A0`

## 11. Audit/CDE evidence bypass

- description: 业务改动未进入 CDE/audit 链
- impact: 决策与操作不可追溯
- control: cde-traceability integration and audit event contracts
- current status: Open
- next mitigation task: `CDE-CONTRACT-A0`

## 12. NexusAI direct business mutation

- description: NexusAI 绕过 Code 直接修改业务状态
- impact: 自动化风险不可控
- control: Code-mediated mutation only + inference trace requirement
- current status: Open
- next mitigation task: `NEXUSAI-BOUNDARY-A0`
