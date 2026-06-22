# LINK-C3-00 — Queue / Partition / Durable State Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C3 Queue / Partition / Durable State.

LINK-C3 focuses on upgrading LINK queue and partition behavior so it can support
EDGE-compatible intake records, controlled backpressure, queue state tracking,
local recovery, and later delivery orchestration.

C3 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C2-00 Ingress Contract & Security Alignment Plan
- LINK-C2-01 EDGE Handoff Intake Contract
- LINK-C2-02 Production State Guard Contract
- LINK-C2-03 Ingress ACK Lifecycle Contract
- LINK-C2-04 Security Reason Taxonomy
- LINK-C2-05 Ingress Contract Validation Harness
- LINK-C2-06 Typecheck and Boundary Validation Evidence
- LINK-C2-07 C2 Aggregate Gate

Current HEAD before this evidence:

- e6d97f4 docs(link): close c2 aggregate gate

EDGE remains frozen for LINK handoff.

## 3. C3 Scope

LINK-C3 may modify AN_VANTARIS_LINK only.

Allowed C3 work:

- Add LINK-owned queue state contract
- Add queue item contract aligned with C2 EDGE handoff intake contract
- Add partition routing metadata contract
- Add priority lane model
- Add local durable queue planning or implementation
- Add queue recovery dry-run harness
- Add queue summary diagnostics contract
- Add C3 validation scripts and evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C3 work:

- Modifying AN_VANTARIS_EDGE runtime
- Modifying AN_VANTARIS_EDGE adapters
- Modifying AN_VANTARIS_EDGE connector registry
- Tracking AN_VANTARIS_EDGE .runtime artifacts
- Direct UFMS DB access
- UFMS schema or migration changes
- UFMS auth or login changes
- Production delivery enablement
- Credential material in source code
- Writeback to OT / device / source system

## 4. EDGE State That C3 Must Preserve

C3 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited

LINK C3 queue work must not imply production delivery approval.

## 5. C3 Contract Targets

C3 must introduce or confirm the following LINK-side concepts:

### 5.1 Queue Item Contract

Required fields or equivalents:

- queueId
- eventId
- traceId
- gatewayId
- partitionKey
- partitionId
- priority
- state
- attempts
- maxAttempts
- enqueuedAt
- updatedAt
- availableAt
- expiresAt
- payloadHash
- reasonCode
- evidenceRef

### 5.2 Queue State Model

Required states:

- RECEIVED
- VALIDATED
- QUEUED
- DELIVERING
- DELIVERED
- ACKED
- RETRY_PENDING
- DLQ
- REJECTED
- EXPIRED

C3 may map existing PENDING / RETRYING / FAILED states to this expanded model
without breaking existing delivery behavior.

### 5.3 Partition Metadata

Required partition metadata:

- tenantId
- siteId
- gatewayId
- sourceSystem
- recordType
- priority
- partitionKey
- partitionId

### 5.4 Durable State / Recovery

C3 must define at least one of:

- local durable append-only queue log
- recovery dry-run from partition log
- documented equivalent recovery path

Generated runtime state must not be tracked.

## 6. C3 Task Breakdown

LINK-C3 planned tasks:

- LINK-C3-01 Queue State Contract
- LINK-C3-02 Queue Item Contract Alignment
- LINK-C3-03 Partition Metadata and Priority Lane Contract
- LINK-C3-04 Local Durable Queue / Recovery Path
- LINK-C3-05 Queue Validation Harness
- LINK-C3-06 Typecheck and Boundary Validation Evidence
- LINK-C3-07 C3 Aggregate Gate

## 7. EDGE Gap Handling

If C3 discovers a confirmed EDGE blocking gap, LINK work must pause.

Blocking gap examples:

- EDGE handoff cannot provide gateway identity for partitioning
- EDGE handoff cannot provide eventId or traceId for queue traceability
- EDGE handoff cannot provide payload hash or equivalent deduplication input
- EDGE output requires LINK to bypass C2 security or production-state guards

If no confirmed blocking gap exists, EDGE remains frozen and LINK continues.

## 8. C3 Success Criteria

C3 is successful when:

- LINK has a GA-ready queue state contract
- LINK queue item contract aligns with C2 EDGE handoff intake contract
- LINK can express partition metadata and priority
- LINK has a durable state or recovery path
- LINK queue validation harness passes
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 9. Result

LINK_C3_00_QUEUE_PARTITION_DURABLE_STATE_PLAN_PASS

LINK-C3 is opened.

LINK may continue to LINK-C3-01 Queue State Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
