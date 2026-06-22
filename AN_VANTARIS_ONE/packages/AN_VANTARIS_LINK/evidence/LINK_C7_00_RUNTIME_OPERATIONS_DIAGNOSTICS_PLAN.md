# LINK-C7-00 — Runtime Operations / Diagnostics Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence opens LINK-C7 Runtime Operations / Diagnostics.

LINK-C7 focuses on defining and validating LINK-owned runtime health, readiness,
queue summary, DLQ summary, delivery summary, retry / replay summary, gateway
liveness summary, evidence summary, and diagnostics bundle contracts.

C7 does not enable production delivery.

## 2. Baseline

Previous stage completed:

- LINK-C6-00 Audit / Evidence Chain Plan
- LINK-C6-01 Audit Event Contract
- LINK-C6-02 Evidence Chain Contract
- LINK-C6-03 Evidence Chain Validation Harness
- LINK-C6-04 Typecheck and Boundary Validation Evidence
- LINK-C6-05 C6 Aggregate Gate

Current HEAD before this evidence:

- 7b4f809 docs(link): close c6 aggregate gate

EDGE-C8 P0 reliability and diagnostics aggregate gate has been completed and validated.

## 3. C7 Scope

LINK-C7 may modify AN_VANTARIS_LINK only.

Allowed C7 work:

- Add LINK health snapshot contract
- Add LINK readiness snapshot contract
- Add queue / DLQ / delivery / retry / replay summaries
- Add gateway heartbeat / liveness summary model
- Add evidence chain summary model
- Add diagnostics bundle contract
- Add diagnostics validation harness
- Add C7 validation evidence files
- Extend LINK package scripts only if scoped to AN_VANTARIS_LINK

Prohibited C7 work:

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

## 4. State That C7 Must Preserve

C7 must preserve:

- EDGE Runtime: Not Enabled
- EDGE Pilot: Not Approved
- EDGE Production: Not Approved
- EDGE Writeback: Prohibited
- EDGE Direct UFMS DB Access: Prohibited
- EDGE LINK Bypass: Prohibited
- LINK Production Delivery: Blocked

C7 may implement operations and diagnostics contracts and dry-run validation only.

## 5. C7 Contract Targets

### 5.1 LINK Health Snapshot

Required fields or equivalents:

- linkNodeId
- healthStatus
- readyStatus
- generatedAt
- ingressStatus
- queueStatus
- dlqStatus
- deliveryStatus
- retryStatus
- replayStatus
- gatewayLivenessStatus
- evidenceStatus
- productionDeliveryAllowed=false

### 5.2 Runtime Summaries

Required summary groups:

- queue depth
- oldest queue age
- DLQ count
- delivery attempt count
- delivery success / blocked / retry / DLQ count
- retry budget remaining
- replay requested count
- gateway online / degraded / offline count
- evidence chain count

### 5.3 Diagnostics Bundle

Required fields or equivalents:

- bundleId
- linkNodeId
- generatedAt
- health snapshot
- queue summary
- DLQ summary
- delivery summary
- retry / replay summary
- gateway liveness summary
- evidence summary
- manifest
- containsSecretMaterial=false
- productionDeliveryAllowed=false

## 6. C7 Task Breakdown

LINK-C7 planned tasks:

- LINK-C7-01 Runtime Health Snapshot Contract
- LINK-C7-02 Runtime Diagnostics Bundle Contract
- LINK-C7-03 Runtime Diagnostics Validation Harness
- LINK-C7-04 Typecheck and Boundary Validation Evidence
- LINK-C7-05 C7 Aggregate Gate

## 7. C7 Success Criteria

C7 is successful when:

- LINK has health snapshot contract
- LINK has diagnostics bundle contract
- LINK diagnostics validation passes
- LINK typecheck passes
- LINK boundary scan passes
- EDGE .runtime remains untracked
- Production delivery remains blocked

## 8. Result

LINK_C7_00_RUNTIME_OPERATIONS_DIAGNOSTICS_PLAN_PASS

LINK-C7 is opened.

LINK may continue to LINK-C7-01 Runtime Health Snapshot Contract.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
