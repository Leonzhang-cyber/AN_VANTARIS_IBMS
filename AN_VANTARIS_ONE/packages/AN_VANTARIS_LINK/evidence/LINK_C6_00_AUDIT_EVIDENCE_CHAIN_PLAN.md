# LINK-C6-00 — Audit / Evidence Chain Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C6 Audit / Evidence Chain.

LINK-C6 focuses on defining and validating LINK-owned audit and evidence records
across ingress, queue, delivery, retry, DLQ, replay, and reliability stages.

C6 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C5-00 Retry / DLQ Taxonomy Plan
- LINK-C5-01 Retry Policy Contract
- LINK-C5-02 Retry Decision / Backoff / Jitter Contract
- LINK-C5-03 DLQ Reason Taxonomy
- LINK-C5-04 DLQ Movement Contract
- LINK-C5-05 Retry / DLQ Validation Harness
- LINK-C5-06 Typecheck and Boundary Validation Evidence
- LINK-C5-07 C5 Aggregate Gate

Current HEAD before this evidence:

- e3983be docs(link): close c5 aggregate gate

EDGE-C8 reliability closure has been completed and validated.

## 3. C6 Scope

LINK-C6 may modify AN_VANTARIS_LINK only.

Allowed C6 work:

- Add audit event contract
- Add evidence chain contract
- Add evidence hash / reference model
- Add ingress / queue / delivery / retry / DLQ evidence record types
- Add replay / reliability evidence record types
- Add evidence chain validation harness
- Add C6 validation evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C6 work:

- Modifying AN_VANTARIS_EDGE runtime
- Modifying AN_VANTARIS_EDGE adapters
- Modifying AN_VANTARIS_EDGE connector registry
- Tracking AN_VANTARIS_EDGE .runtime artifacts
- Direct UFMS DB access
- UFMS schema or migration changes
- UFMS auth or login changes
- Real production delivery enablement
- Credential material in source code
- Writeback to OT / device / source system

## 4. State That C6 Must Preserve

C6 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited
- LINK Production Delivery: Blocked

C6 may implement audit and evidence contracts and dry-run validation only.

## 5. C6 Contract Targets

### 5.1 Audit Event Contract

Required fields or equivalents:

- auditId
- auditType
- severity
- stage
- eventId
- traceId
- gatewayId
- streamId
- sequenceNumber
- queueId
- deliveryId
- dlqId
- reasonCode
- occurredAt
- recordedAt
- actorType
- evidenceRefs

### 5.2 Evidence Chain Contract

Required fields or equivalents:

- evidenceChainId
- traceId
- eventId
- gatewayId
- streamId
- sequenceNumber
- records
- previousHash
- currentHash
- chainComplete
- productionDeliveryAllowed=false

### 5.3 Evidence Record Types

Required evidence record types:

- INGRESS_RECEIVED
- INGRESS_VALIDATED
- QUEUE_ENQUEUED
- QUEUE_DURABLE_APPEND
- DELIVERY_DRY_RUN
- DELIVERY_BLOCKED
- RETRY_DECISION
- DLQ_MOVED
- REPLAY_REQUESTED
- RELIABILITY_ACK
- SECURITY_REJECTED
- POLICY_BLOCKED

## 6. C6 Task Breakdown

LINK-C6 planned tasks:

- LINK-C6-01 Audit Event Contract
- LINK-C6-02 Evidence Chain Contract
- LINK-C6-03 Evidence Hash / Reference Contract
- LINK-C6-04 Evidence Chain Validation Harness
- LINK-C6-05 Typecheck and Boundary Validation Evidence
- LINK-C6-06 C6 Aggregate Gate

## 7. C6 Success Criteria

C6 is successful when:

- LINK has audit event contract
- LINK has evidence chain contract
- LINK has evidence hash/reference model
- LINK can connect C2 ingress, C3 queue, C4 delivery, and C5 DLQ fields
- LINK evidence chain validation passes
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 8. Result

LINK_C6_00_AUDIT_EVIDENCE_CHAIN_PLAN_PASS

LINK-C6 is opened.

LINK may continue to LINK-C6-01 Audit Event Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
