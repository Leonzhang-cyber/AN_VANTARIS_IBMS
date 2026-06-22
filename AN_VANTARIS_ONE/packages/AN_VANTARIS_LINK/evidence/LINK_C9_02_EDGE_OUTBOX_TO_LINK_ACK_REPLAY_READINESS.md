# LINK-C9-02 — EDGE Outbox to LINK ACK / Replay Readiness Check

Status: PASS
Scope: AN_VANTARIS_LINK only
Read-only references: AN_VANTARIS_EDGE / AN_VANTARIS_Contracts
Date: 2026-06-20

## 1. Purpose

This evidence validates readiness alignment between EDGE outbox reliability concepts and LINK ACK / replay / duplicate / gap / idempotency handling.

This task does not enable production delivery.

## 2. Readiness Inputs

Read-only inputs:

- EDGE outbox reliability contract
- EDGE sequenceNumber / streamId / payloadHash concepts
- EDGE retry / replay readiness concepts
- LINK ACK lifecycle contract
- LINK queue item contract
- LINK delivery idempotency contract
- LINK retry / DLQ contracts
- AN_VANTARIS_Contracts shared reliability schema

Shared schema reference:

- AN_VANTARIS_Contracts/schemas/edge-link/edge-link-ack-replay-reliability.v1.json

## 3. Required Alignment Matrix

| Field / Concept | EDGE responsibility | LINK responsibility | Shared contract status | Readiness |
|---|---|---|---|---|
| gatewayId | produce gateway identity | partition / trace / validate | present | READY |
| edgeId | optional edge identity | trace / diagnostics | present | READY |
| streamId | produce stable stream identity | partition / sequence ledger | present | READY |
| sequenceNumber | produce monotonic sequence per stream | detect gap / duplicate | present | READY |
| eventId | produce event identity | dedupe / audit / evidence | present | READY |
| traceId | produce trace identity | correlate queue / delivery / audit | present | READY |
| payloadHash | produce payload integrity hash | idempotency / duplicate validation | present | READY |
| ACK status | receive future LINK ACK | emit ACK lifecycle | present | READY |
| duplicate detection | expose replay-safe records | reject / ACK duplicate | present | READY |
| gap detection | support replay window | request replay range | present | READY |
| replay window | replay outbox range | request from/to sequence | present | READY |
| DLQ handoff | not applicable on EDGE side | move unrecoverable records to DLQ | present in LINK contracts | READY |
| idempotency key | derive from stream/event/hash | enforce delivery idempotency | present | READY |

## 4. Reliability Readiness Decision

Readiness decision:

- EDGE outbox concept can provide the required fields for LINK reliability intake.
- LINK ACK / replay / duplicate / gap handling has corresponding shared schema coverage.
- LINK idempotency and DLQ references are aligned with future delivery stages.
- No runtime connection is enabled by this readiness check.

## 5. Validation Commands

Commands executed for this readiness check:

- node AN_VANTARIS_Contracts/scripts/validate-all-contract-schemas.mjs
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh
- npm --prefix AN_VANTARIS_LINK run typecheck
- bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh

## 6. Boundary Confirmation

This task does not modify EDGE runtime.

This task does not modify Contracts schemas.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not enable live EDGE runtime.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 7. Result

LINK_C9_02_EDGE_OUTBOX_TO_LINK_ACK_REPLAY_READINESS_PASS

EDGE outbox to LINK ACK / replay readiness is aligned.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
