# EDGE C2-08 Validation Tooling Hygiene Report

## Scope

This phase hardens EDGE package validation tooling behavior across environments where `rg` may be unavailable, with no runtime feature change.

## Root cause

`AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` directly invoked `rg` for logs/buffer placeholder checks and forbidden marker scanning. On macOS hosts without ripgrep installed, the script emitted `rg: command not found` and could not complete cleanly.

## Fix summary

- Added runtime detection for `rg` using `command -v rg`.
- Kept ripgrep path when available.
- Added macOS-compatible fallback behavior:
  - file listing fallback: `find ... -type f`
  - pattern scanning fallback: `grep -R -n -i -E`
- Preserved all existing validation scopes:
  - required directories/files
  - C1-05 offline bundle evidence files
  - logs/buffer placeholder policy
  - forbidden secret marker scanning

## Files changed

- `scripts/validate-edge-package.sh`
- `evidence/EDGE_C2_08_VALIDATION_TOOLING_HYGIENE_REPORT.md`

## Validation result

- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh`: PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh`: PASS
- `bash scripts/validate-ufms-ibms-isolation.sh`: PASS with warnings (`hard_fail_count=0`)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c2-foundation-freeze-smoke.sh`: PASS

## Boundary confirmation

- No changes outside allowed EDGE validation/evidence scope.
- No modification to LINK/DB/Console/NexusAI/Contracts or any other package runtime.

## No runtime change confirmation

- No edits under `AN_VANTARIS_EDGE/src/runtime/**`.
- No C2 runtime pipeline behavior changes.

## No LINK/DB/API/device integration confirmation

- No real LINK integration added.
- No DB integration added.
- No UFMS API integration added.
- No real device or protocol integration added.

## Readiness key

`UFMS_EDGE_C2_08_VALIDATION_TOOLING_HYGIENE_PASS`
