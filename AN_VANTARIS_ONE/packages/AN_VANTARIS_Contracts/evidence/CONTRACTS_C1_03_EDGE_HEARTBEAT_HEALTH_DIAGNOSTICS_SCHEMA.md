# CONTRACTS-C1-03 — EDGE Heartbeat / Health / Diagnostics Schema

Status: PASS
Scope: AN_VANTARIS_Contracts only
Date: 2026-06-20

## 1. Purpose

This evidence defines the shared EDGE heartbeat / health / diagnostics schema.

The schema promotes EDGE heartbeat, LINK liveness, health snapshot, and
diagnostics bundle concepts from internal EDGE contracts into a shared,
versioned contract under AN_VANTARIS_Contracts.

## 2. Schema Added

Added schema:

- AN_VANTARIS_Contracts/schemas/edge-link/edge-heartbeat-health-diagnostics.v1.json

## 3. Coverage

The schema covers:

- messageType
- gatewayId
- edgeId
- tenantId
- siteId
- heartbeatId
- health stream
- sequenceNumber
- runtimeStatus
- LINK connectivity status
- liveness status
- heartbeat ACK
- missedAckCount
- consecutiveMissedHeartbeatCount
- outbox summary
- adapter summary
- connector summary
- resource summary
- security status
- policy status
- diagnostics bundle
- diagnostics manifest
- containsSecretMaterial=false
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

CONTRACTS_C1_03_EDGE_HEARTBEAT_HEALTH_DIAGNOSTICS_SCHEMA_PASS

Shared EDGE heartbeat / health / diagnostics schema is now defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
