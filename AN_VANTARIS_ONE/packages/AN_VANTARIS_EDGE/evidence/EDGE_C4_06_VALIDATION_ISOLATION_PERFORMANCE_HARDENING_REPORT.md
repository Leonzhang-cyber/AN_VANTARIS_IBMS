# EDGE C4-06 Validation Isolation and Performance Hardening Report

## Scope

This report captures `UFMS-EDGE-C4-06` validation isolation, concurrency safety, and performance hardening under `AN_VANTARIS_EDGE/**`.

## Baseline commit

- `48b8e15 feat(edge): add service lifecycle recovery foundation`

## Root cause of shared sandbox race

- C4-03, C4-04, and C4-05 dry-run/smoke scripts previously used fixed writable sandbox roots.
- Concurrent executions could remove or overwrite each other artifacts and occasionally trigger `ENOENT`.

## Affected scripts

- `edge-c4-sbom-inventory-{dry-run,smoke}.sh`
- `edge-c4-runtime-hardening-{dry-run,smoke}.sh`
- `edge-c4-service-lifecycle-{dry-run,smoke}.sh`

## Unique session design

- New session root: `AN_VANTARIS_EDGE/.runtime/validation-sessions/<task-id>/<execution-id>/`.
- One execution maps to one unique writable session directory.

## Execution ID design

- Format: `<task-id>-<utc-ms>-pid<pid>-<random-suffix>`.
- Random suffix uses `openssl rand` when available with a deterministic local fallback.

## Safe cleanup design

- Cleanup is constrained to `.runtime/validation-sessions/**`.
- Repository root, EDGE root, traversal paths, and symlink targets are rejected.
- Failed sessions are preserved for diagnostics.

## Parent/child nested execution design

- Smoke triggers nested dry-run with `EDGE_VALIDATION_PARENT_EXECUTION_ID`.
- Parent and child run in isolated session directories.

## Concurrency test matrix

- C4-03 dual dry-run and dry-run/smoke.
- C4-04 dual dry-run and dry-run/smoke.
- C4-05 dual dry-run and dry-run/smoke.
- Cross-task C4-03/C4-04/C4-05 dry-run concurrency.

## Timing results

- Session timing metadata is emitted to `validation-timing.jsonl`.
- Timing data is local development baseline only.

## Timeout limitations

- Local child-process timeout helper uses TERM then KILL for owned child PID only.
- No `killall`/`pkill` usage.
- Capability is foundation-level and host-dependent.

## Existing validation coverage comparison

- Existing C4-03/C4-04/C4-05 CASE checks are retained.
- C4-06 adds validation session and concurrency checks without reducing prior coverage.

## Product behavior impact

- No connector/runtime/network/DB/LINK/UFMS API behavior changes.
- No C4-01/C4-02/C4-03/C4-04/C4-05 business semantic changes.

## Dry-run result

- `edge-c4-validation-isolation-dry-run: PASS`

## Lightweight smoke result

- `edge-c4-validation-isolation-smoke: PASS`

## Package validation

- `validate-edge-package: PASS`

## Boundary scan

- `edge-boundary-scan: PASS`

## Isolation result

- `validate-ufms-ibms-isolation: PASS with warnings`
- `hard_fail_count=0`

## Production limitations

- Validation isolation is foundation-only.
- Performance measurements are local baselines and not production-certified.

## Acceptance result

`VALIDATION_ISOLATION_FOUNDATION_ACCEPTED`

## Readiness key

`UFMS_EDGE_C4_06_VALIDATION_ISOLATION_PERFORMANCE_HARDENING_PASS`
