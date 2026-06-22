# LINK-C4-00 — Delivery / ACK / Idempotency Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C4 Delivery / ACK / Idempotency.

LINK-C4 focuses on defining and validating LINK-owned delivery target contracts,
delivery attempt records, idempotency metadata, delivery receipts, and ACK mapping
from LINK queue records to approved upper-layer APIs.

C4 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C3-00 Queue / Partition / Durable State Plan
- LINK-C3-01 Queue State Contract
- LINK-C3-02 Queue Item Contract Alignment
- LINK-C3-03 Partition Metadata and Priority Lane Contract
- LINK-C3-04 Local Durable Queue / Recovery Path Contract
- LINK-C3-05 Queue Validation Harness
- LINK-C3-05B Multi-EDGE Concurrent Queue Validation Harness
- LINK-C3-05C Stable Telemetry Duplicate Awareness Harness
- LINK-C3-06 Typecheck and Boundary Validation Evidence
- LINK-C3-06B Multi-EDGE and Stable Telemetry Evidence Addendum
- LINK-C3-07 C3 Aggregate Gate

Current HEAD before this evidence:

- 6a3c55a docs(link): close c3 aggregate gate

EDGE stable value suppression follow-up has been completed and validated.

## 3. C4 Scope

LINK-C4 may modify AN_VANTARIS_LINK only.

Allowed C4 work:

- Add delivery target contract
- Add delivery attempt contract
- Add delivery receipt contract
- Add idempotency key contract
- Add delivery ACK mapping contract
- Add production-delivery-blocked guard for delivery
- Add synthetic delivery validation harness
- Add C4 evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C4 work:

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

## 4. EDGE and LINK State That C4 Must Preserve

C4 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited
- LINK Production Delivery: Blocked

C4 may implement synthetic delivery contracts and dry-run validation only.

## 5. C4 Contract Targets

C4 must introduce or confirm the following LINK-side concepts:

### 5.1 Delivery Target Contract

Required fields or equivalents:

- targetId
- targetType
- baseUrl
- apiVersion
- endpointPath
- timeoutMs
- approved
- approvalRef
- credentialRef
- productionDeliveryAllowed

### 5.2 Delivery Attempt Contract

Required fields or equivalents:

- deliveryId
- queueId
- eventId
- traceId
- gatewayId
- targetId
- attemptNumber
- maxAttempts
- startedAt
- completedAt
- status
- httpStatus
- retryable
- reasonCode
- idempotencyKey

### 5.3 Idempotency Contract

Required fields or equivalents:

- idempotencyKey
- eventId
- traceId
- gatewayId
- payloadHash
- recordType
- occurredAt
- queueId
- dedupeKey if available

Required outgoing headers:

- X-VANTARIS-Idempotency-Key
- X-VANTARIS-Trace-Id
- X-VANTARIS-Gateway-Id
- X-VANTARIS-Link-Queue-Id
- X-VANTARIS-Link-Delivery-Id

### 5.4 Delivery ACK / Receipt Contract

Required delivery receipt states:

- DELIVERY_BLOCKED
- DELIVERY_DRY_RUN_ACCEPTED
- DELIVERY_ATTEMPTED
- DELIVERY_ACCEPTED
- DELIVERY_RETRYABLE
- DELIVERY_REJECTED
- DELIVERY_DLQ

C4 must preserve production delivery blocked state.

## 6. C4 Task Breakdown

LINK-C4 planned tasks:

- LINK-C4-01 Delivery Target Contract
- LINK-C4-02 Idempotency Contract
- LINK-C4-03 Delivery Attempt and Receipt Contract
- LINK-C4-04 Production Delivery Block Guard
- LINK-C4-05 Synthetic Delivery Validation Harness
- LINK-C4-06 Typecheck and Boundary Validation Evidence
- LINK-C4-07 C4 Aggregate Gate

## 7. Multi-EDGE and Stable Telemetry Considerations

C4 delivery must preserve C3 guarantees:

- alarm records must not be delayed by stable telemetry
- stable telemetry duplicate awareness must be preserved through idempotency
- payloadHash and dedupeKey must contribute to duplicate risk analysis
- gatewayId and traceId must be carried into delivery headers
- queueId and deliveryId must be traceable
- multi-EDGE delivery must avoid cross-gateway ambiguity

## 8. C4 Success Criteria

C4 is successful when:

- LINK has delivery target contract
- LINK has idempotency key contract
- LINK has delivery attempt and receipt contract
- LINK has delivery production-block guard
- LINK synthetic delivery validation passes
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 9. Result

LINK_C4_00_DELIVERY_ACK_IDEMPOTENCY_PLAN_PASS

LINK-C4 is opened.

LINK may continue to LINK-C4-01 Delivery Target Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
