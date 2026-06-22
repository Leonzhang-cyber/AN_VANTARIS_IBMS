# EDGE C1-02B Hardware-Key Optional Switch Report

Date: 2026-06-18  
Workspace: `/Volumes/Work/VANTARIS_UFMS_FULL`  
Scope: `AN_VANTARIS_EDGE` only

## 1) Product decision

- Hardware-key / USB HSM guard is optional in current EDGE stage.
- Default mode is guard disabled (`EDGE_HARDWARE_KEY_REQUIRED=false`).
- Enforcement happens only when explicitly enabled by config.

## 2) Config switch behavior

- `EDGE_HARDWARE_KEY_REQUIRED=false`:
  - `hardwareKey.required=false`
  - `hardwareKey.status=disabled`
  - `lockedReason=null`
  - no lock forced by hardware-key policy.
- `EDGE_HARDWARE_KEY_REQUIRED=true` + `EDGE_RUNTIME_MODE=production` + no real verified key:
  - `hardwareKey.required=true`
  - `hardwareKey.status=locked`
  - `lockedReason=hardware_key_verification_required_for_production`
  - health status becomes `locked`.
- `EDGE_HARDWARE_KEY_REQUIRED=true` + non-production mode + no verified key:
  - status remains `missing` or `implementation_pending`
  - no forced production lock behavior.

## 3) Default behavior

- Updated `edge.env.example` default to:
  - `EDGE_HARDWARE_KEY_REQUIRED=false`
  - `EDGE_LOCKED_MODE_ENABLED=true`
- Added explicit comments describing optional default and enable path.

## 4) Required=true production locked behavior

- Guard logic now locks runtime only in production when required=true and there is no explicit real verifier success.
- Lock reason remains stable and explicit.

## 5) Health snapshot behavior

- Health snapshot continues to expose:
  - `hardwareKey.required`
  - `hardwareKey.present`
  - `hardwareKey.provider`
  - `hardwareKey.serial`
  - `hardwareKey.status`
  - `lockedReason`
  - `runtimeMode`
- Optional mode reports hardware key as disabled without hardware-key lock.

## 6) Diagnostics evidence behavior

- Diagnostics payload continues to expose `hardwareKey` with required/status/lockedReason/runtimeMode.
- Added validation coverage for:
  - optional default no lock
  - required production lock
  - no fake verified state.

## 7) Validation results

- `npm run typecheck:edge` PASS
- `npm run typecheck:link` PASS
- `npm run typecheck:edge-link` PASS
- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh` PASS
- `bash scripts/validate-package-boundaries.sh` PASS (existing warnings)
- `bash scripts/validate-ufms-ibms-isolation.sh` PASS (existing warnings)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh` PASS

## 8) No fake verified confirmation

- No fake verified path was introduced.
- `verified` is only allowed when explicit real verifier success input is provided.

## 9) No real HSM SDK confirmation

- No real HSM SDK integration was introduced.
- No challenge-response implementation was added.

## 10) No LINK / legacy integration / UFMS / Code / DB / Console / NexusAI modification confirmation

- No source changes outside `AN_VANTARIS_EDGE` for this task.

## 11) Remaining blockers

- No functional blocker for C1-02B scope.
- Existing global validation warnings remain historical/unrelated.

## 12) Current readiness

`UFMS_EDGE_C1_02B_HARDWARE_KEY_OPTIONAL_SWITCH_PASS`
