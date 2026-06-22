# EDGE C1-02 Production Install and Hardware-Key Guard Report

Date: 2026-06-18  
Workspace: `/Volumes/Work/VANTARIS_UFMS_FULL`  
Module scope: `AN_VANTARIS_EDGE` only

## 1) Modified file list

- `.gitignore` (EDGE local runtime ignore only)
- `AN_VANTARIS_EDGE/deploy/PRODUCTION_DIRECTORY_LAYOUT_V1.md`
- `AN_VANTARIS_EDGE/deploy/systemd/vantaris-edge.service`
- `AN_VANTARIS_EDGE/deploy/templates/edge.env.example`
- `AN_VANTARIS_EDGE/deploy/offline/precheck-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline/install-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline/uninstall-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline/upgrade-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline/rollback-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline/healthcheck-edge.sh`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/MANIFEST.edge.json`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/APT_DEPENDENCIES.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/APT_OPTIONAL_SECURITY.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/NODE_RUNTIME.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/NODE_PRODUCTION_DEPENDENCIES.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/HSM_DEPENDENCIES.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/CONNECTOR_DEPENDENCIES.edge.txt`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/PRODUCTION_EXCLUDE.edge.txt`
- `AN_VANTARIS_EDGE/src/runtime/hardware-key-guard.ts`
- `AN_VANTARIS_EDGE/src/runtime/types.ts`
- `AN_VANTARIS_EDGE/src/runtime/health-snapshot.ts`
- `AN_VANTARIS_EDGE/src/runtime/diagnostics-exporter.ts`
- `AN_VANTARIS_EDGE/src/runtime/c1-runtime-foundation.ts`
- `AN_VANTARIS_EDGE/src/runtime/index.ts`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh`

## 2) Production directory layout summary

- Added Ubuntu 22.04 production layout baseline with required directories under `/opt`, `/etc`, `/var/lib`, and `/var/log`.
- Release model uses `/opt/vantaris/edge/releases/<version>` and `/opt/vantaris/edge/current` symlink for upgrade/rollback flow.
- Runtime data/outbox/dlq/quarantine paths are separated for least privilege operations.
- Explicit notes: no secrets in repository, no direct DB write, EDGE-only deployment scope.
- Security positioning remains IEC 62443 aligned baseline and not certified.

## 3) systemd template summary

- Added `vantaris-edge` unit template at `deploy/systemd/vantaris-edge.service`.
- Runs as non-root service account `vantaris-edge`.
- Uses `EnvironmentFile=/etc/vantaris/edge/edge.env`.
- Uses fixed runtime path `ExecStart=/opt/vantaris/edge/current/bin/vantaris-edge-runtime`.
- Includes baseline hardening:
  - `NoNewPrivileges=true`
  - `PrivateTmp=true`
  - `ProtectSystem=full`
  - `ProtectHome=true`
  - `ReadWritePaths=/var/lib/vantaris/edge /var/log/vantaris/edge /etc/vantaris/edge`
  - `CapabilityBoundingSet=`
- Includes service resilience with `Restart=on-failure` and `RestartSec`.

## 4) Offline install scaffold summary

- Added scaffold scripts under `deploy/offline/` for precheck/install/uninstall/upgrade/rollback/healthcheck.
- All scripts are bash with `set -euo pipefail`.
- All scripts support `--dry-run`.
- Scripts are safe scaffold only: no destructive action by default, no package install by default, no service start by default, no external network call.
- Scripts are executable and provide explicit operator-facing echo output.

## 5) Dependency manifest summary

- Added offline bundle manifest and package lists under `deploy/offline-bundle/`.
- `APT_DEPENDENCIES.edge.txt` includes required baseline packages for runtime ops, diagnostics, and PKCS#11 plumbing.
- `APT_OPTIONAL_SECURITY.edge.txt` includes optional hardening packages, and marks `softhsm2` as dev/ci only.
- Added node runtime and production dependency placeholders for offline package governance.
- Added HSM and connector dependency placeholder lists for foundation stage only.
- Added production exclude list for packaging hygiene.

## 6) Hardware-key guard behavior

- Added runtime guard scaffold in `src/runtime/hardware-key-guard.ts`.
- Parses environment-style input fields for required/provider/serial/label/present/runtimeMode.
- No real HSM SDK integration and no challenge-response implementation in this stage.
- Guard never fabricates verification; without explicit real verifier input, status remains `missing` or `implementation_pending`.

## 7) Locked mode behavior

- In production mode with hardware-key required and no verified key, runtime is forced to locked posture.
- `lockedReason` is set to `hardware_key_verification_required_for_production`.
- Non-production modes expose guard state without forcing production lock path.

## 8) Health snapshot update

- Health snapshot includes:
  - `hardwareKey.required`
  - `hardwareKey.present`
  - `hardwareKey.provider`
  - `hardwareKey.serial`
  - `hardwareKey.status`
  - `lockedReason`
  - `runtimeMode`
- Health status can now surface `locked` when production key verification is missing.

## 9) Diagnostics evidence update

- Diagnostics pack now includes `hardwareKey` object:
  - `required`
  - `present`
  - `provider`
  - `serial`
  - `status`
  - `lockedReason`
  - `runtimeMode`
- Production + required + no real verifier path outputs locked posture with `missing` or `implementation_pending`, not `verified`.

## 10) Smoke / validation results

- `npm run typecheck:edge` PASS
- `npm run typecheck:link` PASS
- `npm run typecheck:edge-link` PASS
- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh` PASS
- `bash scripts/validate-package-boundaries.sh` PASS (existing warnings)
- `bash scripts/validate-ufms-ibms-isolation.sh` PASS (existing warnings)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh` PASS (13 cases)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh` PASS

## 11) Whether LINK was modified

- No. `AN_VANTARIS_LINK` runtime implementation was not modified.

## 12) Whether legacy integrations / UFMS / Code / DB / Console / NexusAI was modified

- No runtime/content changes were made under legacy twin integration modules, `AN_VANTARIS_Code`, `AN_VANTARIS_DB`, `AN_VANTARIS_Console`, `AN_VANTARIS_NexusAI`, or non-EDGE UFMS runtime modules.

## 13) Remaining blockers

- No functional blocker for C1-02 foundation scope.
- Known repository-level warnings from boundary/isolation scans remain historical/unrelated and pre-existing.

## 14) Current readiness

`UFMS_EDGE_C1_02_PRODUCTION_INSTALL_HARDWARE_KEY_GUARD_PASS`
