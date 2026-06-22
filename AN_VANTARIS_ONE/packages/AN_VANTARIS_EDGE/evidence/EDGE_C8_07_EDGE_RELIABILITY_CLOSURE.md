# EDGE-C8-07 — EDGE Reliability Evidence Closure

Status: PASS
Scope: AN_VANTARIS_EDGE only
Date: 2026-06-20

## 1. Purpose

This evidence closes the controlled EDGE-C8 reliability follow-up identified during LINK-C3 and LINK-C4 planning.

The purpose is to reduce LINK ingress pressure and prepare EDGE-side reliable send semantics before future EDGE-LINK integration.

This closure covers:

- stable value suppression
- change detection policy
- deadband / heartbeat behavior
- EDGE outbox reliability contract
- streamId / sequenceNumber semantics
- ACK tracking
- retry / replay request semantics
- stable suppression and outbox relationship

This closure does not enable EDGE runtime, pilot, production, writeback, or direct UFMS DB access.

## 2. Completed EDGE-C8 Reliability Items

Completed items:

- EDGE-C8-01 Stable Value Suppression and Change Detection Policy
- EDGE-C8-02 Stable Value Suppression Contract
- EDGE-C8-03 Stable Value Suppression Validation Harness
- EDGE-C8-04 Stable Value Suppression Evidence Closure
- EDGE-C8-05 EDGE Outbox Reliability Contract
- EDGE-C8-06 EDGE Outbox Retry / Replay Validation Harness
- EDGE-C8-07 EDGE Reliability Evidence Closure

## 3. Current HEAD Before Evidence

Current HEAD before this evidence:

- 66db6f8 test(edge): add outbox retry replay validation

## 4. Source and Validation Files Added

Added or updated files:

- AN_VANTARIS_EDGE/evidence/EDGE_C8_01_STABLE_VALUE_SUPPRESSION_POLICY.md
- AN_VANTARIS_EDGE/evidence/EDGE_C8_04_STABLE_VALUE_SUPPRESSION_CLOSURE.md
- AN_VANTARIS_EDGE/src/runtime/contracts/stable-value-suppression-contract.ts
- AN_VANTARIS_EDGE/src/runtime/contracts/edge-outbox-reliability-contract.ts
- AN_VANTARIS_EDGE/scripts/validate-c8-stable-suppression.mjs
- AN_VANTARIS_EDGE/scripts/validate-c8-outbox-reliability.mjs
- AN_VANTARIS_EDGE/tsconfig.c8-stable-suppression.json
- AN_VANTARIS_EDGE/tsconfig.c8-outbox.json
- AN_VANTARIS_EDGE/package.json
- AN_VANTARIS_EDGE/src/runtime/index.ts

## 5. Validation Commands

Commands executed:

- npm --prefix AN_VANTARIS_EDGE run validate:c8-stable-suppression
- npm --prefix AN_VANTARIS_EDGE run validate:c8-outbox
- npm --prefix AN_VANTARIS_EDGE run typecheck
- bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh
- git status --short

## 6. Validation Results

Results:

- Stable value suppression validation harness: PASS
- EDGE outbox retry / replay validation harness: PASS
- EDGE typecheck: PASS
- EDGE boundary scan: PASS
- Git status: clean after generated dist-c8 and dist-c8-outbox cleanup
- EDGE runtime artifacts: not tracked
- LINK files: not modified by this closure

Validation markers confirmed:

- EDGE_C8_03_STABLE_VALUE_SUPPRESSION_VALIDATION_PASS
- EDGE_C8_06_OUTBOX_RETRY_REPLAY_VALIDATION_PASS

## 7. Stable Value Suppression Coverage Confirmed

Confirmed:

- stable dedupeKey generation
- telemetry default policy uses DEADBAND
- analog absolute deadband below threshold does not emit
- analog absolute deadband above threshold emits
- percentage deadband works
- heartbeatDue can force emission
- suppressed no-change decision increments suppressedCount
- heartbeat decision emits without increasing suppressedCount
- digital/status policy uses CHANGE_ONLY
- alarm policy uses AGGREGATED_REPEAT and is not telemetry-suppressed
- evidence policy remains conservative

## 8. EDGE Outbox Reliability Coverage Confirmed

Confirmed:

- outbox stream key generation
- reliability key generation
- streamId and sequenceNumber representation
- sequence reference validation
- outbox item creation
- outbox ACK initial state
- retry policy defaults
- capacity policy defaults
- retry eligibility
- retry exhaustion handling
- queued ACK prevents retry
- replay request creation
- outbox state transition record
- stable suppression no-change does not create outbox record
- heartbeat stable decision can create outbox record
- heartbeat outbox item validates

## 9. EDGE-to-LINK Reliability Decision

EDGE must be prepared to support future EDGE-LINK reliability using:

- gatewayId
- edgeId
- streamId
- sequenceNumber
- eventId
- traceId
- payloadHash
- ACK tracking
- retry state
- replay request
- max in-flight policy
- retry budget
- replay budget
- outbox capacity policy

LINK must still enforce duplicate awareness, ingress ledger, idempotency, and delivery blocking in later C4/C5 stages.

## 10. Stable Suppression and Outbox Relationship

Decision:

- stable telemetry with no meaningful change should not create a new outbox send record
- stable telemetry should update local snapshot and suppressedCount
- heartbeatDue may create a new outbox record
- full snapshot may create outbox records
- reconnect first sample may create outbox records
- alarm/event/health/evidence/audit/config records must remain conservative
- LINK duplicate awareness and idempotency remain required

## 11. Boundary Confirmation

This closure does not enable EDGE runtime.

This closure does not approve pilot or production use.

This closure does not allow writeback.

This closure does not allow direct UFMS DB access.

This closure does not bypass LINK.

This closure does not add credentials or secrets.

No UFMS backend, frontend, DB, schema, migration, auth, login, credentials, or environment files were modified.

## 12. Remaining Work

Future controlled integration work may connect these contracts to actual EDGE normalized record emission and EDGE-LINK runtime behavior.

Those future tasks must remain controlled and must not enable production runtime without explicit pilot/production approval gates.

LINK-C4 should now align idempotency and delivery ACK contracts with:

- streamId
- sequenceNumber
- gatewayId
- eventId
- traceId
- payloadHash
- dedupeKey
- queueId
- deliveryId

## 13. Result

EDGE_C8_07_EDGE_RELIABILITY_CLOSURE_PASS

EDGE stable suppression and outbox reliability contracts are now defined and validated.

Runtime remains not enabled.
Pilot remains not approved.
Production remains not approved.
Writeback remains prohibited.
