# CONTRACTS-C1-02 — EDGE-LINK ACK / Replay / Reliability Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the shared EDGE-LINK ACK / replay / reliability schema.

The schema promotes ACK, duplicate detection, sequence gap detection, replay
window, and reliability ledger concepts from internal EDGE and LINK contracts
into a shared, versioned contract under AN_VANTARIS_Contracts.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/edge-link/edge-link-ack-replay-reliability.v1.json

## 3. Coverage

The schema covers:

- schemaVersion
- messageId
- messageType
- gatewayId
- edgeId
- tenantId
- siteId
- streamId
- sequenceNumber
- eventId
- traceId
- payloadHash
- ACK status
- duplicate flag
- gap detection flag
- sequence gap range
- replay window
- reliability ledger snapshot
- evidenceRefs
- boundary flags

## 4. Boundary

This task does not modify EDGE runtime.

This task does not modify LINK runtime.

This task does not implement VANTARIS ONE, UMMS, UCDE, or UFMS runtime.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not enable production delivery.

This task does not enable EDGE runtime.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 5. Result

CONTRACTS_C1_02_EDGE_LINK_ACK_REPLAY_RELIABILITY_SCHEMA_PASS

Shared EDGE-LINK ACK / replay / reliability schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
