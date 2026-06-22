# LINK-C2-00 — Ingress Contract & Security Alignment Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C2.

LINK-C2 focuses on aligning LINK ingress with the frozen EDGE handoff output and
hardening the security gate before queue, delivery, retry, DLQ, and deployment
work continue.

C2 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C1-03 EDGE Handoff Alignment Matrix
- LINK-C1-04 LINK Architecture Freeze
- LINK-C1-05 C1 Aggregate Gate

Current HEAD before this evidence:

- bb74954 docs(link): close c1 aggregate gate

EDGE remains frozen for LINK handoff.

## 3. C2 Scope

LINK-C2 may modify AN_VANTARIS_LINK only.

Allowed C2 work:

- Add LINK-side EDGE handoff intake contract
- Add blocked production state representation
- Add ingress ACK lifecycle contract
- Add security reason taxonomy
- Add endpoint approval reference model
- Add credential reference model without storing secrets
- Add C2 validation harnesses
- Add C2 evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C2 work:

- Modifying AN_VANTARIS_EDGE runtime
- Modifying AN_VANTARIS_EDGE adapters
- Modifying AN_VANTARIS_EDGE connector registry
- Modifying AN_VANTARIS_EDGE package files
- Tracking AN_VANTARIS_EDGE .runtime artifacts
- Direct UFMS DB access
- UFMS schema or migration changes
- UFMS auth or login changes
- Production delivery enablement
- Credential material in source code

## 4. EDGE State That C2 Must Preserve

C2 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited

LINK C2 must treat unapproved production state as blocked.

## 5. C2 Contract Targets

C2 must introduce or confirm the following LINK-side concepts:

### 5.1 EDGE Handoff Intake Contract

Required fields or equivalents:

- protocolVersion
- eventId
- traceId
- correlationId
- gatewayId
- edgeId
- siteId
- tenantId
- sourceSystem
- connectorType
- adapterType
- recordType
- occurredAt
- receivedAt
- payloadHash
- normalizedPayload
- evidenceRef
- decisionState
- productionState

### 5.2 Production State Guard

Required states:

- runtimeEnabled
- pilotApproved
- productionApproved
- writebackRequested
- productionDeliveryAllowed

Default C2 behavior:

- runtimeEnabled: false
- pilotApproved: false
- productionApproved: false
- writebackRequested: false
- productionDeliveryAllowed: false

### 5.3 Ingress ACK Lifecycle

Required ACK statuses:

- RECEIVED
- VALIDATED
- QUEUED
- REJECTED
- BLOCKED
- DLQ

C2 only needs ingress/validation ACK readiness.
Delivery ACK remains C4 scope.

### 5.4 Security Reason Taxonomy

Required C2 reason codes:

- LINK_SECURITY_SIGNATURE_INVALID
- LINK_SECURITY_TIMESTAMP_SKEW
- LINK_SECURITY_REPLAY_DETECTED
- LINK_SECURITY_GATEWAY_MISSING
- LINK_SECURITY_GATEWAY_NOT_ALLOWED
- LINK_SCHEMA_INVALID
- LINK_PROTOCOL_UNSUPPORTED
- LINK_EDGE_PRODUCTION_BLOCKED
- LINK_WRITEBACK_PROHIBITED
- LINK_QUEUE_BACKPRESSURE

## 6. C2 Task Breakdown

LINK-C2 planned tasks:

- LINK-C2-01 EDGE Handoff Intake Contract
- LINK-C2-02 Production State Guard Contract
- LINK-C2-03 Ingress ACK Lifecycle Contract
- LINK-C2-04 Security Reason Taxonomy
- LINK-C2-05 Ingress Contract Validation Harness
- LINK-C2-06 Typecheck and Boundary Validation
- LINK-C2-07 C2 Aggregate Gate

## 7. EDGE Gap Handling

If C2 discovers a confirmed EDGE blocking gap, LINK work must pause.

Blocking gap examples:

- EDGE has no stable output field equivalent for required LINK intake
- EDGE cannot provide trace / event / gateway identity
- EDGE cannot represent blocked production state
- EDGE output would require LINK to bypass its own security gate
- EDGE output implies writeback or production delivery before approval

If no confirmed blocking gap exists, EDGE remains frozen and LINK continues.

## 8. C2 Success Criteria

C2 is successful when:

- LINK has an explicit EDGE handoff intake contract
- LINK can represent blocked EDGE production state
- LINK has an ingress ACK lifecycle contract
- LINK has security reason taxonomy
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 9. Result

LINK_C2_00_INGRESS_CONTRACT_SECURITY_ALIGNMENT_PLAN_PASS

LINK-C2 is opened.

LINK may continue to LINK-C2-01 EDGE Handoff Intake Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
