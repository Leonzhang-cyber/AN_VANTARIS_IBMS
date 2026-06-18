# VANTARIS ONE Skeleton Risk Review

## 1. Skeleton mistaken as runtime

- description: 误把骨架目录当作可部署运行平台
- impact: 发布失败和错误运维动作
- control: explicit `SKELETON_ONLY` markers and boundary docs
- current status: Controlled
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 2. Accidental runtime source copy

- description: 未经审计复制 backend/frontend runtime 源码到 skeleton
- impact: 边界污染与迁移审计失效
- control: strict file-type validation and scope checks in A5
- current status: Controlled
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 3. Edge driver coupling carried into new package

- description: 抽取时携带 DAO/DB/UI/SSE 耦合
- impact: Edge 模块边界失真
- control: EDGE source audit before extraction
- current status: Open
- next mitigation task: `EDGE-SOURCE-AUDIT`

## 4. Link implemented before contract baseline

- description: 在 Link 契约缺失时先写 runtime
- impact: delivery behavior inconsistent and non-replayable
- control: link contracts first (envelope/ack/retry/dlq/route)
- current status: Open
- next mitigation task: `LINK-A0`

## 5. DB migration mixed with skeleton

- description: A5 混入 DB migration 变更
- impact: 任务边界破坏，迁移链风险
- control: forbid migration operations and DB schema edits in A5
- current status: Controlled
- next mitigation task: `DB-SCHEMA-BASELINE`

## 6. UFMS contamination

- description: UFMS runtime/source/schema/auth/login/seed/migration 混入 skeleton
- impact: 跨系统污染与治理失效
- control: UFMS boundary guard and adapter-only rule
- current status: Monitored
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 7. Naming drift between skeleton and governance

- description: skeleton 命名与 A1/A2 冻结名称偏离
- impact: 后续迁移映射冲突
- control: enforce frozen 6+1 package names
- current status: Controlled
- next mitigation task: `ONE-TRANSITION-A7-REBRAND-READINESS`

## 8. Package boundary bypass

- description: future migration bypasses boundary files and直接跨模块耦合
- impact: architecture regression
- control: boundary review gate before source migration commits
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 9. Future audit evidence gap

- description: migration decisions and source lineage not fully captured
- impact: audit traceability degradation
- control: maintain migration-source docs and staged decision logs
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`
