# EDGE C1-03 Restart Recovery and Persistence Pressure Report

Date: 2026-06-18  
Workspace: `/Volumes/Work/VANTARIS_UFMS_FULL`  
Scope: `AN_VANTARIS_EDGE` only

Compatibility note: validated after `UFMS-EDGE-C1-02B` hardware-key optional switch baseline.

## 1) Modified file list

- `AN_VANTARIS_EDGE/src/runtime/durable-local-buffer.ts`
- `AN_VANTARIS_EDGE/src/runtime/diagnostics-exporter.ts`
- `AN_VANTARIS_EDGE/src/runtime/c1-runtime-foundation.ts`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-recovery-dry-run.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-persistence-pressure.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-quarantine-dry-run.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-persistence-smoke.sh`
- `AN_VANTARIS_EDGE/evidence/EDGE_C1_03_RESTART_RECOVERY_PERSISTENCE_PRESSURE_REPORT.md`
- `AN_VANTARIS_EDGE/evidence/EDGE_C1_02_PRODUCTION_INSTALL_HARDWARE_KEY_GUARD_REPORT.md` (wording normalization to keep isolation validator hard-fail clean)

## 2) Durable buffer enhancement summary

- Added ledger-line validator with structured warning output (`invalid_json`, `invalid_record`, `state_without_message`, `empty_line`).
- Added tolerant recovery path that does not crash on corrupt JSONL lines.
- Added warning collection during recovery and exposure through `restartRecoveryEvidence`.
- Added `countByStatus`, `recoverFromLedger`, `exportLedgerSnapshot`, and `ledgerPath`.
- Added max-record guard (`maxRecordBytes`) so oversized records are quarantined instead of accepted.
- Added `quarantineInvalidSample` helper and lightweight `compactLedger`.

## 3) Restart recovery behavior

- Restart dry-run appends canonical local envelopes into outbox ledger, injects one corrupt line, and simulates restart by creating a new buffer instance.
- Recovery reads ledger safely, preserves valid records, and records warning entries for corrupt content.
- Recovered pending records are replayed locally, then partially marked `accepted_local` / `failed`.
- Expiry/purge path is exercised via short/expired TTL sample.

## 4) Pressure evidence behavior

- Persistence pressure script appends `100` messages by default.
- Supports `EDGE_C1_PRESSURE_COUNT` override.
- Enforces hard max safe limit `1000` and fails if exceeded.
- Replays appended messages locally and marks deterministic accepted/failed distribution.
- Exports pressure evidence with duration and counters; no external service calls.

## 5) Quarantine behavior

- Quarantine dry-run validates local quarantine handling for:
  - invalid mapping sample
  - unsupported message sample
  - checksum missing sample
- Invalid samples are written into local quarantine artifacts.
- Quarantine output remains local and non-outbound.

## 6) Diagnostics evidence update

- C1 diagnostics payload now includes:
  - `restartRecoveryEvidence`
  - `persistencePressure`
  - `quarantine`
  - existing `hardwareKey`, connector/plugin registry, health snapshot, boundary assertions
- Runtime dry-run now checks these C1-03 diagnostics summaries explicitly.

## 7) Evidence output paths

- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-runtime-evidence.json`
- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-restart-recovery-evidence.json`
- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-persistence-pressure-evidence.json`
- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-quarantine-evidence.json`
- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-health-snapshot.json`
- `AN_VANTARIS_EDGE/.runtime/evidence/edge-c1-ledger-snapshot.json`

## 8) Smoke / validation results

- `npm run typecheck:edge` PASS
- `npm run typecheck:link` PASS
- `npm run typecheck:edge-link` PASS
- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh` PASS
- `bash scripts/validate-package-boundaries.sh` PASS (existing warnings)
- `bash scripts/validate-ufms-ibms-isolation.sh` PASS (existing warnings)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh` PASS (16 cases)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-recovery-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-persistence-pressure.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-quarantine-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-persistence-smoke.sh` PASS

## 9) Whether LINK was modified

- No. `AN_VANTARIS_LINK` source was not modified.

## 10) Whether I-BMS / UFMS / Code / DB / Console / NexusAI was modified

- No. No modifications were made outside `AN_VANTARIS_EDGE` for this task.

## 11) Remaining blockers

- No functional blocker for C1-03 scope.
- Existing repository warnings from package-boundary / isolation validators remain historical and unrelated to this EDGE-local change set.

## 12) Current readiness

`UFMS_EDGE_C1_03_RESTART_RECOVERY_PERSISTENCE_PRESSURE_PASS`
