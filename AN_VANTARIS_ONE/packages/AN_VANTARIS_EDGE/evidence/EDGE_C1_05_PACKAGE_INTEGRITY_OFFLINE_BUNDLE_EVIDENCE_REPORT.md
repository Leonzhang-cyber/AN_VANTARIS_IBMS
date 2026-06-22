# EDGE C1-05 Package Integrity and Offline Bundle Evidence Report

Date: 2026-06-18  
Workspace: `/Volumes/Work/VANTARIS_UFMS_FULL`  
Scope: `AN_VANTARIS_EDGE` only

## 1) Executive conclusion

- C1-05 package integrity evidence baseline is established.
- Offline bundle integrity/trust artifacts are now documented and validated by smoke checks.
- This stage remains template/evidence baseline only, not a real signed production release.

## 2) Modified file list

- `AN_VANTARIS_EDGE/deploy/offline-bundle/MANIFEST.edge.json`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/PACKAGE_INTEGRITY.edge.md`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/install-evidence-template.edge.json`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/SHA256SUMS.edge.template`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/OFFLINE_BUNDLE_STRUCTURE.edge.md`
- `AN_VANTARIS_EDGE/deploy/offline-bundle/PRODUCTION_EXCLUDE.edge.txt`
- `AN_VANTARIS_EDGE/scripts/validation/edge-c1-package-integrity-smoke.sh`
- `AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` (minimal C1-05 file checks)
- `AN_VANTARIS_EDGE/evidence/EDGE_C1_05_PACKAGE_INTEGRITY_OFFLINE_BUNDLE_EVIDENCE_REPORT.md`
- `AN_VANTARIS_EDGE/evidence/EDGE_C1_04_CLOSURE_AUDIT_AND_GAP_MATRIX_REPORT.md` (wording-only hardening to keep isolation hard-fail clean)

## 3) Offline bundle integrity baseline

- Added explicit package integrity policy document for Ubuntu Server 22.04 LTS offline deployment.
- Added bundle structure specification for future release assembly.
- Added template-based signing/hash policy with clear future-release boundary.
- Updated manifest metadata to include security baseline, certification claim, and integrity-required files.

## 4) SHA256SUMS template behavior

- Added `SHA256SUMS.edge.template` with all-zero placeholder hash lines.
- Template includes required files and runtime archive placeholders.
- Explicitly marked as template-only; real release must generate actual checksums.

## 5) Signature/GPG status

- Real GPG signing is not implemented in C1-05.
- No private signing key is present in repository.
- `SHA256SUMS.sig` remains planned future release artifact.

## 6) Install evidence template summary

- Added `install-evidence-template.edge.json` with required keys and null/template defaults.
- No real host/site secrets or identifiers included.
- Explicitly marked as `template_only`.

## 7) Production exclude hardening summary

- Hardened `PRODUCTION_EXCLUDE.edge.txt` with runtime, secret, env, key/cert, cache, log, test, and artifact patterns.
- Added recursive exclusions for `.runtime` and `node_modules`.
- Added sensitive filename wildcard guards (`*.key`, `*.pem`, `*.p12`, `*.pfx`, `*.secret`, token/password wildcards).

## 8) Secret/DB URL scan summary

- `edge-c1-package-integrity-smoke.sh` scans `deploy/offline-bundle` and `deploy/templates` for forbidden DB/secret markers.
- No live DB URLs, secret key blocks, or private key blocks were detected in validated outputs.

## 9) Validation results

- `npm run typecheck:edge` PASS
- `npm run typecheck:link` PASS
- `npm run typecheck:edge-link` PASS
- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh` PASS
- `bash scripts/validate-package-boundaries.sh` PASS (known warnings)
- `bash scripts/validate-ufms-ibms-isolation.sh` PASS (known warnings)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-recovery-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-persistence-pressure.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-quarantine-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-persistence-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-package-integrity-smoke.sh` PASS

## 10) Whether runtime was modified

- No runtime logic was modified for C1-05.

## 11) Whether LINK / UFMS non-EDGE / Code / DB / Console / NexusAI / Contracts were modified

- No changes were made outside `AN_VANTARIS_EDGE`.

## 12) Remaining blockers

- Real release artifact generation pipeline is still pending.
- Real signing key management and `SHA256SUMS.sig` verification pipeline are pending.
- Formal package publication/install evidence execution in target host remains future phase work.

## 13) Recommended next phase

Recommended: `UFMS-EDGE-C1-06 Local Health API / Diagnostic CLI`.

Reason:
- C1-05 closes package integrity evidence baseline.
- Next highest operational gap is local operator observability and diagnostics surfaces.

## 14) Current readiness

`UFMS_EDGE_C1_05_PACKAGE_INTEGRITY_OFFLINE_BUNDLE_EVIDENCE_PASS`
