# EDGE C4-01 Offline Lifecycle Scaffold Report

## Scope

This report captures C4-01 scaffold delivery for offline install/upgrade/rollback lifecycle governance under `AN_VANTARIS_EDGE/**` only.

## Baseline commit

- `caeaad7 docs(edge): freeze current capability audit findings`

## Safety boundary

- Scope limited to scaffold scripts, lifecycle plans, and dry-run evidence.
- No runtime connector behavior changes.
- No normalization/buffer/delivery/audit runtime behavior changes.
- No cross-package integration enabling.

## Release layout

- Target production layout model is documented in `RELEASE_LAYOUT.edge.md`.
- C4-01 does not create real `/opt/vantaris-edge`.
- Current/previous pointers are simulated only in sandbox.

## Install plan

- Install scaffold defined in `INSTALL_PLAN.edge.json`.
- `executionMode` is `DRY_RUN_ONLY`.
- Install script supports dry-run sandbox simulation only.

## Upgrade plan

- Upgrade scaffold defined in `UPGRADE_PLAN.edge.json`.
- Upgrade requires existing active release state and version change.
- Upgrade simulation creates backup metadata and pointer switch in sandbox.

## Backup plan

- Pre-upgrade backup metadata is simulated in `shared/backups/*.json`.
- Backup scope is lifecycle/config metadata only in C4-01 scaffold.

## Rollback plan

- Rollback scaffold defined in `ROLLBACK_PLAN.edge.json`.
- Rollback simulation requires existing previous pointer.
- Active/previous pointer switch is sandbox-only.

## Rollback verification

- `rollback-state.json` is produced with `verified=true`.
- `active-release.json` and `release-history.jsonl` are updated in dry-run mode.

## Uninstall guard

- `uninstall-edge.sh` provides impact plan only.
- Output includes mandatory `REAL_UNINSTALL_DISABLED`.
- Protected shared paths are never deleted in C4-01.

## Shared data preservation

- `shared/data`, `shared/buffer`, `shared/audit`, `shared/evidence`, and `shared/backups` are preserved through upgrade/rollback simulation.
- Release directory is treated as immutable per-version tree.

## State files

- `active-release.json`
- `release-history.jsonl`
- `rollback-state.json`
- All lifecycle state files are written with `mode=DRY_RUN`.

## Dry-run cases

- `edge-c4-offline-lifecycle-dry-run.sh` implements 18 required CASE validations.
- Success output includes:
  - `edge-c4-offline-lifecycle-dry-run: PASS`
  - `UFMS_EDGE_C4_01_OFFLINE_INSTALL_UPGRADE_ROLLBACK_SCAFFOLD_PASS`

## Lightweight smoke result

- `edge-c4-offline-lifecycle-smoke.sh` is lightweight and scoped to C4-01 only.
- Smoke validates required files, safety flags, executable scripts, dry-run guards, prohibited command absence, runtime git hygiene, and invokes C4-01 dry-run.

## Production limitations

- C4-01 is scaffold-only and not production-enabled.
- Real deployment lifecycle operations remain disabled.

## Explicit safety statements

- Explicit no real install statement: real install is disabled in C4-01.
- Explicit no systemd change statement: no host service manager action is executed.
- Explicit no `/opt` write statement: no real host `/opt` writes are performed.
- Explicit no `sudo` statement: no privileged command escalation is used.
- Explicit no LINK/DB/UFMS API statement: no LINK call, no DB write, no UFMS API access in C4-01 scaffold.

## Readiness key

`UFMS_EDGE_C4_01_OFFLINE_INSTALL_UPGRADE_ROLLBACK_SCAFFOLD_PASS`
