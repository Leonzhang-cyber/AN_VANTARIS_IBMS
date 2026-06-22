# LINK-C5-00 — Retry / DLQ Taxonomy Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C5 Retry / DLQ Taxonomy.

LINK-C5 focuses on defining and validating LINK-owned retry policy, backoff,
jitter, retry storm protection, DLQ reason taxonomy, DLQ movement, replay-aware
retry behavior, and delivery failure classification.

C5 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C4-00 Delivery / ACK / Idempotency Plan
- LINK-C4-01 Delivery Target Contract
- LINK-C4-02 Delivery Idempotency Contract
- LINK-C4-02B Idempotency Reliability Alignment Fix
- LINK-C4-03 Delivery Attempt and Receipt Contract
- LINK-C4-04 Production Delivery Block Guard
- LINK-C4-05 Synthetic Delivery Validation Harness
- LINK-C4-06 Typecheck and Boundary Validation Evidence
- LINK-C4-07 C4 Aggregate Gate

Current HEAD before this evidence:

- 598d4ae docs(link): close c4 aggregate gate

EDGE-C8 reliability closure has been completed and validated.

## 3. C5 Scope

LINK-C5 may modify AN_VANTARIS_LINK only.

Allowed C5 work:

- Add retry policy contract
- Add retry decision contract
- Add backoff and jitter model
- Add retry budget model
- Add retry storm protection model
- Add DLQ reason taxonomy
- Add DLQ movement contract
- Add replay-aware retry handling
- Add C5 validation harness
- Add C5 evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C5 work:

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

## 4. State That C5 Must Preserve

C5 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited
- LINK Production Delivery: Blocked

C5 may implement retry and DLQ contracts and dry-run validation only.

## 5. C5 Contract Targets

### 5.1 Retry Policy Contract

Required fields or equivalents:

- policyId
- maxAttempts
- initialDelayMs
- maxDelayMs
- jitterMs
- retryBudget
- retryWindowMs
- targetRetryBudget
- gatewayRetryBudget
- streamRetryBudget
- replayRetryBudget
- retryableReasonCodes
- nonRetryableReasonCodes

### 5.2 Retry Decision Contract

Required decision outputs:

- shouldRetry
- retryable
- attemptNumber
- maxAttempts
- nextRetryAt
- backoffMs
- jitterMs
- reasonCode
- retryBudgetRemaining
- stormProtected
- dlqRequired

### 5.3 DLQ Taxonomy

Required DLQ categories:

- SECURITY
- SCHEMA
- POLICY
- DELIVERY
- RETRY_EXHAUSTED
- REPLAY
- QUEUE
- UNKNOWN

Required reason examples:

- LINK_SECURITY_SIGNATURE_INVALID
- LINK_SCHEMA_INVALID
- LINK_POLICY_BLOCKED
- LINK_DELIVERY_TARGET_REJECTED
- LINK_DELIVERY_TIMEOUT
- LINK_DELIVERY_RETRY_EXHAUSTED
- LINK_REPLAY_WINDOW_EXCEEDED
- LINK_QUEUE_EXPIRED
- LINK_QUEUE_BACKPRESSURE

### 5.4 DLQ Movement Contract

Required fields or equivalents:

- dlqId
- queueId
- deliveryId
- eventId
- traceId
- gatewayId
- streamId
- sequenceNumber
- targetId
- reasonCode
- category
- retryable
- replayEligible
- movedAt
- evidenceRef

## 6. C5 Task Breakdown

LINK-C5 planned tasks:

- LINK-C5-01 Retry Policy Contract
- LINK-C5-02 Retry Decision / Backoff / Jitter Contract
- LINK-C5-03 DLQ Reason Taxonomy
- LINK-C5-04 DLQ Movement Contract
- LINK-C5-05 Retry / DLQ Validation Harness
- LINK-C5-06 Typecheck and Boundary Validation Evidence
- LINK-C5-07 C5 Aggregate Gate

## 7. EDGE-LINK Reliability Considerations

C5 must align with EDGE-C8 and LINK-C4 reliability concepts:

- gatewayId
- streamId
- sequenceNumber
- eventId
- traceId
- payloadHash
- reliabilityKey
- duplicateRiskKey
- replay window
- sequence gap
- retry storm protection

Retry must not cause replay storms after EDGE reconnect.

DLQ must preserve enough metadata for later operator diagnostics and controlled
replay.

## 8. C5 Success Criteria

C5 is successful when:

- LINK has retry policy contract
- LINK has retry decision contract
- LINK has DLQ reason taxonomy
- LINK has DLQ movement contract
- LINK validation harness passes
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 9. Result

LINK_C5_00_RETRY_DLQ_TAXONOMY_PLAN_PASS

LINK-C5 is opened.

LINK may continue to LINK-C5-01 Retry Policy Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
