# VANTARIS ONE Target Architecture Risk Review

## 1. Monolith migration risk

- description: 从 legacy IBMS 向平台化模块拆分时，存在职责未剥离干净与耦合回流风险
- impact: 发布复杂度和故障域扩大，影响稳定性
- control: 分阶段拆分（A1-A7）、模块边界冻结、契约优先
- current status: Open (controlled by governance)

## 2. Over-renaming risk

- description: 过早改名或大范围替换导致路径、接口、文档同时失配
- impact: 构建失败、运行回归、协作混乱
- control: docs-first rename, no global replace
- current status: Mitigating

## 3. Edge/Link boundary risk

- description: Edge 与 Link 职责重叠会引发重复处理和路由不一致
- impact: 数据丢失、重复消费、运维复杂度上升
- control: Edge only collect/normalize, Link only deliver/route/audit
- current status: Open

## 4. Direct DB write risk

- description: Edge/Link/AI 直接写业务库会绕过业务规则和审计链
- impact: 数据一致性和合规性破坏
- control: DB write through Code approved access layer only
- current status: Controlled by policy

## 5. UFMS contamination risk

- description: UFMS runtime/source/schema/auth/login/seed/migration 混入 ONE
- impact: 边界破坏、交付不可控、安全审计失败
- control: UFMS only via adapter contract boundary, strict stop rule
- current status: Monitored

## 6. NexusAI overreach risk

- description: AI 模块越权写业务状态或绕过业务流程
- impact: 错误自动化决策影响关键业务状态
- control: NexusAI via Code/CDE APIs only, no direct business DB writes
- current status: Open

## 7. Patch/license bypass risk

- description: 模块绕过 patch/license gate 直接部署或激活
- impact: 合规与授权风险，版本不可追溯
- control: Console + Code patch manager + manifest/VC verification
- current status: Open

## 8. Contract drift risk

- description: 实现与 Contracts 漂移，导致接口与事件语义不一致
- impact: 集成失败、回滚困难
- control: AN_VANTARIS_Contracts as single source of contract truth
- current status: Open

## 9. HA not implemented risk

- description: 生产环境仅单节点部署
- impact: 单点故障导致服务中断
- control: Mode C HA baseline (multi-node/standby/cluster)
- current status: Planned

## 10. IEC62443 zone/conduit misconfiguration risk

- description: OT/IT 区域与 conduit 划分不当
- impact: 横向移动风险上升，安全域失效
- control: Mode D zoning, strict firewall and conduit policy
- current status: Planned

## 11. Secret leakage risk

- description: 文档、配置、脚本泄露敏感密钥或凭证
- impact: 凭证泄露和供应链安全事件
- control: no secrets in repo, placeholder-only docs, secret scanning gates
- current status: Monitored

## 12. Legacy IBMS compatibility risk

- description: 迁移期兼容策略不明确导致存量系统中断
- impact: 老客户升级失败、接口断裂
- control: `ibms-core` + legacy compatibility layer + staged migration plan
- current status: Open
