# EDGE C2-05 Local Delivery Orchestrator and Retry Policy Execution Report

## scope

This phase adds a local delivery orchestrator foundation that reads local buffer records, builds delivery batch previews, evaluates retry/backoff decisions, updates local cursor state, and exports evidence under `.runtime`.

## files changed

- `src/runtime/delivery-orchestrator-types.ts`
- `src/runtime/delivery-orchestrator.ts`
- `src/runtime/local-buffer-store.ts`
- `src/runtime/connector-manager.ts`
- `src/runtime/edge-diagnostics-cli.ts`
- `src/runtime/index.ts`
- `scripts/validation/edge-c2-local-delivery-orchestrator-dry-run.sh`
- `scripts/validation/edge-c2-local-delivery-orchestrator-smoke.sh`
- `evidence/EDGE_C2_05_LOCAL_DELIVERY_ORCHESTRATOR_REPORT.md`

## delivery orchestrator behavior

- Selects only `staged` / `pending` / `failed` local buffer records.
- Builds local batch preview with per-item retry decision.
- Supports dry-run local status transitions for pending/failed/acknowledged outcomes.
- Exports local-only evidence and cursor snapshots.

## retry policy behavior

- Policy fields: `maxAttempts`, `baseDelayMs`, `maxDelayMs`, `batchSize`.
- Failed/pending items get exponential backoff with clamp to `maxDelayMs`.
- Records exceeding `maxAttempts` are marked as `exhausted` in preview decisions.
- Non-retryable statuses become `skipped`.

## cursor behavior

- Cursor advances with processed batch size.
- Stores `nextCursorIndex`, `processedCount`, and `lastProcessedRecordId`.
- Cursor is exported to dedicated C2-05 evidence file.

## evidence paths

- `.runtime/evidence/edge-c2-local-delivery-orchestrator-evidence.json`
- `.runtime/evidence/edge-c2-local-delivery-batch-preview.json`
- `.runtime/evidence/edge-c2-local-delivery-cursor.json`

## validation results

- C2-05 dry-run and smoke pass.
- C2-04/C2-03/C2-02/C2-01 smoke remain pass.
- C1 smoke suite remains pass.
- Typecheck and boundary/isolation validators remain pass.

## runtime artifact hygiene

- `.runtime` remains ignored by git.
- Runtime evidence artifacts are not committed.

## forbidden items confirmation

- No real LINK delivery.
- No database integration.
- No UFMS API integration.
- No real device access.
- No real protocol library integration.
- No VANTARIS ONE or legacy twin stack coupling.

## readiness key

`UFMS_EDGE_C2_05_LOCAL_DELIVERY_ORCHESTRATOR_PASS`
