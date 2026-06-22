# CONTRACTS-C1-04 — LINK Delivery / Idempotency / Receipt Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the shared LINK delivery / idempotency / receipt schema.

The schema promotes LINK delivery target, endpoint approval, delivery attempt,
receipt, idempotency, retry reference, and DLQ reference concepts from internal
LINK contracts into a shared, versioned contract under AN_VANTARIS_Contracts.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/edge-link/link-delivery-idempotency-receipt.v1.json

## 3. Coverage

The schema covers:

- deliveryId
- deliveryType
- handoff envelope reference
- recordType
- eventId
- traceId
- gatewayId
- edgeId
- streamId
- sequenceNumber
- payloadHash
- targetKind
- endpointRef
- approvalStatus
- idempotencyKey
- duplicate policy
- delivery attempt
- delivery receipt
- retryRef
- dlqRef
- evidenceRefs
- boundary flags

## 4. Boundary

This task does not modify LINK runtime.

This task does not modify EDGE runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not approve delivery endpoints.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 5. Result

CONTRACTS_C1_04_LINK_DELIVERY_IDEMPOTENCY_RECEIPT_SCHEMA_PASS

Shared LINK delivery / idempotency / receipt schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
