# LINK-C1-03 — EDGE Handoff Alignment Matrix

Status: PASS_WITH_GAPS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records how AN_VANTARIS_LINK currently aligns with the frozen
AN_VANTARIS_EDGE final handoff closure.

AN_VANTARIS_EDGE is treated as frozen for LINK handoff.

LINK may consume EDGE handoff concepts and tracked evidence, but LINK must not
modify EDGE runtime, adapters, connector registry, package files, schemas,
evidence, or .runtime artifacts.

## 2. EDGE Frozen State Consumed by LINK

EDGE final handoff state:

- Runtime: Not Enabled
- Pilot: Not Approved
- Production: Not Approved
- Writeback: Prohibited
- Direct UFMS DB Access: Prohibited
- LINK Bypass: Prohibited

LINK development must preserve this state.

Until a later controlled pilot enablement gate is approved, LINK must remain in
dry-run, synthetic delivery, local validation, local queue, local evidence, and
non-production delivery mode.

## 3. LINK Current Source Inventory

Current LINK source modules inspected:

- link-ingress.ts
- link-queue.ts
- link-delivery.ts
- link-retry.ts
- link-dlq.ts

Existing capabilities found:

- Zone 1 EDGE to Zone 2 LINK ingress guard
- transport header extraction
- wire JSON parsing
- protocol version validation
- gatewayId validation
- timestamp skew validation
- wire event signature validation
- immutable wire event freeze
- partition router and partitioned queue push
- queue state tracking
- delivery single-attempt dispatch
- delivery ACK / RETRY / DLQ result mapping
- retry backoff decision
- DLQ in-memory and optional append-only log backing
- offset commit store support

## 4. EDGE-to-LINK Alignment Matrix

| EDGE handoff concept | LINK current support | Status | Required follow-up |
|---|---:|---|---|
| normalized read-only records | WireTransportEvent / LinkHandoffEvent path exists | PARTIAL | Add explicit EDGE handoff intake contract |
| connector decision state | Not explicit in inspected files | GAP | Add field-level mapping or blocked-state guard |
| adapter evidence reports | Not consumed by runtime | ACCEPTABLE_FOR_C1 | Keep evidence-only consumption |
| runtime not enabled | Not explicit in inspected files | GAP | Add EDGE production state guard |
| pilot not approved | Not explicit in inspected files | GAP | Add pilot approval state guard |
| production not approved | Not explicit in inspected files | GAP | Add production approval state guard |
| writeback prohibited | Not explicit in inspected files | GAP | Add writeback rejection rule |
| direct UFMS DB access prohibited | No DB access seen in inspected files | PASS | Keep boundary scan gate |
| LINK bypass prohibited | LINK is positioned as gateway | PASS | Preserve through C2-C4 |
| endpoint approval schema | Not explicit in inspected files | GAP | Add endpoint approval reference in delivery contract |
| credential reference schema | Signing secret exists, credential refs not explicit | PARTIAL | Add credential reference contract without secrets |
| rollback plan schema | Not runtime-consumed | ACCEPTABLE_FOR_C1 | Keep as deployment evidence follow-up |
| operator authorization schema | Not explicit in inspected files | GAP | Add operator action scope for DLQ replay later |
| evidence collection schema | Evidence docs exist, no aggregate LINK gate yet | PARTIAL | Add C1 aggregate evidence gate |

## 5. EDGE Gap Register Seed

The following potential EDGE-related gaps are registered for controlled handling.

| Gap ID | Type | Description | LINK impact | Action |
|---|---|---|---|---|
| EDGE-GAP-001 | Non-blocking | EDGE runtime is not enabled | LINK C1-C4 may continue in dry-run mode | Track for EDGE-C8 |
| EDGE-GAP-002 | Non-blocking | EDGE pilot is not approved | LINK may not perform production delivery | Track for EDGE-C8/C9 |
| EDGE-GAP-003 | Non-blocking | EDGE production is not approved | LINK production delivery remains blocked | Track for EDGE-LINK-C10/C11 |
| EDGE-GAP-004 | Review-needed | Explicit EDGE output field mapping must be confirmed before C2 | LINK C2 contract may require mapping evidence | Validate in LINK-C2 |
| EDGE-GAP-005 | Review-needed | EDGE blocked production state must be represented in LINK guard | LINK C2/C4 must enforce blocked state | Implement in LINK first; patch EDGE only if missing |

No EDGE blocking gap is confirmed at C1-03.

## 6. GA-Relevant LINK Gaps

The following are blockers before International GA:

1. Explicit EDGE handoff intake contract is missing.
2. EDGE blocked production state is not enforced in LINK ingress/delivery.
3. Queue state model is still transport-minimal.
4. DLQ reason taxonomy is not sufficient for field operations.
5. Ingress/queue ACK lifecycle is not yet aligned with EDGE expectations.
6. LINK has no C1 aggregate evidence gate yet.
7. LINK package currently has limited validation scripts.

## 7. Development Direction

LINK next stages must proceed in this order:

1. LINK-C1-04 LINK Architecture Freeze
2. LINK-C1-05 C1 Aggregate Gate
3. LINK-C2 Ingress Contract & Security Alignment
4. LINK-C3 Queue / Partition / Durable State
5. LINK-C4 Delivery / ACK / Idempotency
6. LINK-C5 Retry / DLQ taxonomy
7. LINK-C6 Audit / Evidence
8. LINK-C7 Runtime Operations
9. LINK-C8 Offline Deployment Package
10. LINK-C9 EDGE-LINK Integration Readiness

If a confirmed EDGE blocking gap is found later, LINK work pauses and a controlled
EDGE-C8 gap patch task must be opened.

## 8. Boundary Decision

No EDGE files may be modified during LINK development unless explicitly
authorized in a later controlled integration task.

LINK may read tracked EDGE evidence and handoff documents only.

EDGE .runtime artifacts are not accepted as LINK contract source and must not be
tracked.

## 9. Result

LINK_C1_03_EDGE_HANDOFF_ALIGNMENT_MATRIX_PASS_WITH_GAPS

LINK may continue to LINK-C1-04 Architecture Freeze.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
