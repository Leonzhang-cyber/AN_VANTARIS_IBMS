# CONTRACTS-C3-04 — UFMS APP API Delivery Boundary Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the future UFMS APP API Delivery Boundary schema.

The schema describes how LINK delivery may later target UFMS APP API boundaries using
machine identity, idempotency, delivery receipts, and canonical EDGE-LINK handoff references.

This is boundary-only. It does not implement UFMS backend/frontend, EDGE runtime,
LINK runtime, database schema, authentication, login, credentials, VANTARIS ONE, UMMS,
or UCDE.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/consumer-boundary/ufms-app-api-delivery-boundary.v1.json

## 3. Coverage

The schema covers:

- boundaryId
- deliveryBoundaryType
- canonical handoff envelope reference
- LINK delivery receipt reference
- UFMS API target
- endpointRef
- routeTemplate
- machineIdentityRequired=true
- endpointApproved=false
- payloadRef
- recordType
- eventId
- traceId
- gatewayId
- edgeId
- streamId
- sequenceNumber
- payloadHash
- assetRef
- deviceRef
- pointRef
- locationRef
- delivery mode
- idempotency key
- productionDeliveryAllowed=false
- retry / DLQ flags
- receipt expectation
- evidence references
- boundary flags

## 4. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement UFMS runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable LINK production delivery.

This task does not enable EDGE runtime.

This task does not approve UFMS endpoints.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 5. Result

CONTRACTS_C3_04_UFMS_APP_API_DELIVERY_BOUNDARY_SCHEMA_PASS

UFMS APP API Delivery Boundary schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
