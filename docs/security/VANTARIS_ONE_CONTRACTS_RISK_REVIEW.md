# VANTARIS ONE Contracts Risk Review

## 1. Contract drift risk

- description: contracts 与 runtime 实现长期偏离
- impact: 接口行为不一致，集成故障
- control: contract-first + mandatory alignment review gates
- current status: Open
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 2. Runtime private schema risk

- description: 模块绕过 contracts 使用私有跨模块 schema
- impact: 隐性耦合上升，迁移难度增大
- control: ban private cross-module schema, enforce contract registry
- current status: Open
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 3. Edge/Link envelope inconsistency risk

- description: Edge 输出与 Link 消费 envelope 不一致
- impact: ACK/retry/DLQ/replay 链路不可控
- control: define envelope/ack/retry/dlq contracts before extraction
- current status: MISSING contracts
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 4. API namespace breaking change risk

- description: 在 contract approval 前修改 API namespace
- impact: frontend/backend/client 兼容性中断
- control: namespace change only after contract approval
- current status: Controlled by governance
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 5. DB schema rename without migration contract risk

- description: 未经迁移契约约束直接改表名/字段
- impact: migration 断链和数据回放失败
- control: DB rename only via migration contract and framework
- current status: Controlled by rule
- next mitigation task: `REBRAND-ONE-A1`

## 6. License/Patch manifest bypass risk

- description: 部分模块绕过 manifest 校验执行补丁或授权
- impact: 供应链与授权合规风险
- control: module manifest + patch manifest + license VC mandatory checks
- current status: MISSING contracts
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 7. DID/VC misuse risk

- description: DID/VC 语义未统一导致错误验证或误用
- impact: 信任链与身份鉴权失效
- control: unified DID/VC contract profiles and verification policies
- current status: PARTIAL
- next mitigation task: `ONE-TRANSITION-A4.1-TRUST-CONTRACT-PROFILE`

## 8. UFMS adapter contract contamination risk

- description: UFMS 接入绕过 adapter contract 直接侵入 ONE runtime
- impact: 边界污染与架构失控
- control: UFMS only through approved adapter contract; strict boundary guard
- current status: Monitored
- next mitigation task: `ONE-TRANSITION-A6-IBMS-CORE-MODULE-PLAN`

## 9. AI/CDE trace contract gap risk

- description: AI 推理与 CDE 证据链缺少统一 trace contract
- impact: 推理不可追溯，审计不完整
- control: define AI request/response/trace + CDE evidence schema set
- current status: TO_BE_ALIGNED
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 10. Generated artifact mismatch risk

- description: 生成代码/SDK 与源契约版本不一致
- impact: 客户端和服务端契约冲突
- control: generated artifact must reference source contract version/hash
- current status: Open
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 11. Backward compatibility break risk

- description: 公开 API/Event 未保留兼容策略即发生破坏性变更
- impact: 现网调用失败
- control: semantic versioning + new version for breaking changes
- current status: Controlled by governance
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`

## 12. Security boundary under-specified risk

- description: 端口/网络边界/安全契约定义不足
- impact: 部署时安全域配置错误与暴露面增大
- control: explicit port/network boundary contract catalog
- current status: PARTIAL
- next mitigation task: `ONE-TRANSITION-A5-SKELETON`
