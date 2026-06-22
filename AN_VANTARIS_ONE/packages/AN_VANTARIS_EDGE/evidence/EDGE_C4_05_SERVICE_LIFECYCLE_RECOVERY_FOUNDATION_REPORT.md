# EDGE C4-05 Service Lifecycle and Recovery Foundation Report

## Scope

This report captures `UFMS-EDGE-C4-05` service lifecycle and recovery foundation under `AN_VANTARIS_EDGE/**`.

## Baseline commit

- `0aa9cbe feat(edge): add runtime filesystem hardening foundation`

## Foundation classification

- `SERVICE_LIFECYCLE_FOUNDATION_ONLY`

## Lifecycle state model

- States: `STOPPED`, `STARTING`, `RUNNING`, `DEGRADED`, `STOPPING`, `FAILED`, `RECOVERING`, `CRASH_LOOP_BLOCKED`, `MANUAL_INTERVENTION_REQUIRED`.

## Legal transitions

- Legal transitions are explicitly listed in machine-readable model and validated in dry-run.

## Illegal transition rejection

- Illegal shortcuts (for example `STOPPED->RUNNING`, `FAILED->RUNNING`) are explicitly rejected.

## Startup precheck

- Startup precheck model covers release integrity, hardening presence, path safety, state compatibility, and manual blocks.

## Graceful shutdown model

- Modeled sequence includes stop new work, drain, metadata persistence, evidence emission, and `STOPPING->STOPPED`.

## Failure classification

- Failure classes include transient, integrity, permission, storage, buffer risk, audit risk, dependency, crash-loop, manual stop, and unknown.

## Restart/backoff

- Restart policy is bounded (`initialDelay=5`, multiplier `2`, max delay `300`, max attempts `5`).
- Sensitive failure classes block automatic restart.

## Retry budget

- Retry budget is capped and modeled in deterministic dry-run.

## Crash-loop detection

- Crash-loop window and thresholds are defined with blocked recovery behavior.

## Manual intervention

- Crash-loop and critical failures require manual intervention state.

## State preservation

- Recovery preserves shared state and lifecycle history.

## Buffer/audit/evidence preservation

- Policy forbids automatic clearing or deletion of buffer, audit, and evidence.

## Rollback recommendation

- Rollback recommendation is modeled for critical corruption/integrity classes.

## Systemd lifecycle recommendations

- Lifecycle-specific recommendations are recorded with `appliedByC4_05=false`.
- No service unit changes are applied in C4-05.

## Sandbox simulation

- Lifecycle plan, state snapshot, and append-only history are simulated in `.runtime/c4-05-sandbox`.

## Dry-run result

- `edge-c4-service-lifecycle-dry-run: PASS`

## Lightweight smoke result

- `edge-c4-service-lifecycle-smoke: PASS`

## Production limitations

- C4-05 does not apply service lifecycle to host runtime.
- C4-05 does not start, stop, or restart real services.
- C4-05 does not send real process signals.

## Explicit safety statements

- Explicit no-service-start statement: no real service start operation performed.
- Explicit no-service-stop statement: no real service stop operation performed.
- Explicit no-systemctl statement: no real service manager command executed.
- Explicit no-process-signal statement: no real process signal operation executed.
- Explicit no-system-path-write statement: no writes under `/opt`, `/etc`, `/var`, or `/usr`.
- Explicit no-network statement: no network operation performed in C4-05 foundation.

## Acceptance result

`SERVICE_LIFECYCLE_FOUNDATION_ACCEPTED_NOT_APPLIED`

## Readiness key

`UFMS_EDGE_C4_05_SERVICE_LIFECYCLE_RECOVERY_FOUNDATION_PASS`
