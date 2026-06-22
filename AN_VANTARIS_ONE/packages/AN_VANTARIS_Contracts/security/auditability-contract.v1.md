# Auditability Contract v1

## 1. Audit event categories

- auth
- config_change
- contract_change
- deployment_change
- edge_handoff
- link_delivery
- dlq_move
- replay_request
- db_persistence
- console_action
- ai_decision
- security_event
- patch_event

## 2. Required audit fields

- auditId
- schemaVersion
- eventCategory
- actorType
- actorId
- machineId
- targetType
- targetId
- action
- outcome
- occurredAt
- traceId
- correlationId
- sourcePackage
- deploymentProfile
- moduleProfile
- evidenceRef

## 3. Retention and integrity baseline

- append-only intent
- tamper-evident hash future option
- no secret payloads
- PII minimization
- audit export support
- project-specific retention policy

## 4. Package responsibilities

### EDGE audit responsibilities

- capture edge_handoff attempt/outcome metadata
- capture machine identity and profile context

### LINK audit responsibilities

- capture link_delivery transitions
- capture dlq_move and replay_request lifecycle events

### Code/API audit responsibilities

- capture persistence-facing and control-plane contract actions
- maintain correlation across inbound and outbound operations

### DB audit responsibilities

- preserve persistence change evidence references
- support export and retention policy implementation hooks

### Console audit responsibilities

- capture operator actions and privileged workflow traces
- preserve actor type and target references

### NexusAI audit responsibilities

- capture ai_decision and evidence linkage metadata
- capture recommendation-to-action trace references
