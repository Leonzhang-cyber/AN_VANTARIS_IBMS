# EDGE C5-01 File Import Controlled Read-only Foundation Report

## Scope

`UFMS-EDGE-C5-01` introduces local controlled read-only file ingestion foundation for the `file` connector only.

## Baseline

- `d1bae69 feat(edge): add production connector enablement gate`

## File connector current maturity

- `currentMaturity=FOUNDATION_READY`
- `requestedMode=FOUNDATION_ONLY`
- `permittedMode=SYNTHETIC_ONLY`
- `syntheticFixtureOnly=true`
- `realConnectivityEnabled=false`
- `productionDependencyIncluded=false`
- `supportsWriteback=false`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`

## Path safety model

- allowlisted root restricted to validation-session sandbox
- independent verify found semantic conflict when `deniedRoots` included filesystem root (`/`)
- fixed evaluation order:
  1) canonical candidate path resolution
  2) canonical allowedRoot boundary check
  3) explicit deniedRoot check without overriding valid allowedRoot
- traversal rejected
- symlink rejected
- regular-file requirement enforced
- valid allowlisted absolute sandbox paths are accepted

## Type and size policy

- allowed extensions: `.json`, `.csv`
- default max file size: `10485760` bytes (10 MiB) foundation default
- hidden/device/socket/directory candidates rejected

## Stable-file model

- dual-stat observation with controlled short window
- changes in size/mtime/inode produce `FILE_NOT_STABLE`

## Duplicate model

- deterministic identity: `sha256 + size + extension + relative path`
- duplicate mode: `SHA256_LOCAL_FOUNDATION`
- duplicate result: `DUPLICATE_DETECTED`

## Quarantine decision-only model

- mode fixed to `DECISION_ONLY`
- reason and suggested target are generated
- no source move/delete/rename/permission mutation

## JSON/CSV parser model

- JSON accepts object/array, rejects malformed or scalar in foundation policy
- CSV requires header, consistent columns, deterministic delimiter, row-limit policy
- formula-like cells are treated as plain text

## Source immutability proof

- validation checks content hash, filename, and permissions remain unchanged
- source mutation flags remain false in policy

## Validation results

- dry-run: `edge-c5-file-import-readonly-dry-run: PASS` (53 cases)
- smoke: `edge-c5-file-import-readonly-smoke: PASS`
- package validation: PASS
- boundary scan: PASS
- isolation result: PASS (`hard_fail_count=0`)
- shell evaluator reuses TypeScript validator/reader logic via runtime TS transpilation loader
- TS validator and shell evaluator semantic consistency is covered in dry-run for:
  - valid allowlisted path
  - outside allowlist
  - traversal
  - symlink
  - unsupported extension

## Production limitations

- no real customer directory access
- no network filesystem enablement
- no controlled pilot approval
- no production read-only approval
- no writeback enablement

## Acceptance result

- `FILE_IMPORT_READ_ONLY_FOUNDATION_ACCEPTED`
- `UFMS_EDGE_C5_01_FILE_IMPORT_CONTROLLED_READ_ONLY_FOUNDATION_PASS`
