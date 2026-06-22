# EDGE C6-01 / C6-01A File Production Adapter Report

## Scope

`UFMS-EDGE-C6-01` introduces the first real-connectivity production adapter for the `file` connector: a controlled, local, read-only, single-file reader isolated from runtime registration.

`UFMS-EDGE-C6-01A` closes independent verification findings from the first read-only review without runtime registration, dependency changes, or gate promotion.

## Baseline

- `0a99aa8 docs(edge): freeze real connectivity architecture`

## Modified files

- `src/connectors/file/production/file-production-adapter.types.ts`
- `src/connectors/file/production/file-production-path-policy.ts`
- `src/connectors/file/production/file-production-normalizer.ts`
- `src/connectors/file/production/file-production-readonly-adapter.ts`
- `src/connectors/file/production/index.ts`
- `deploy/offline-bundle/scripts/verify-file-production-readonly-adapter-edge.sh`
- `scripts/validation/edge-c6-file-production-adapter-dry-run.sh`
- `scripts/validation/edge-c6-file-production-adapter-smoke.sh`
- `scripts/validation/lib/file-production-adapter-dry-run-cases.cjs`
- `deploy/offline-bundle/connector-enablement/CONNECTOR_EVIDENCE_INDEX.edge.json`
- `evidence/EDGE_C6_01_FILE_PRODUCTION_ADAPTER_REPORT.md`

## First independent verification (C6-01)

- **Final decision:** FAIL
- **Verifier negative matrix:** 16/20 REJECTED, **4 LEAKED**
- **Leaked negatives:**
  1. connector-manager registration not checked
  2. package.json dependency drift not checked
  3. `requireRegularFile` removal not detected
  4. `export const write` not detected
- **Adapter findings:**
  - `pathReferenceId` embedded raw relative/absolute path segments (for example `/etc/passwd` leaked into reference IDs)
  - JSONL performed file-level Foundation validation only; per-record Foundation validation was missing after line parse

## C6-01A fixes

### Path reference redaction

- `createPathReferenceId()` now returns opaque references: `file-root:<rootReferenceId>:<sha256-stable-hash-16>`
- Uses Node built-in `crypto.createHash('sha256')`; hash is reference-only, not authentication
- Error messages and result payloads do not include raw input path, canonical path, realpath, allowlisted absolute path, or session absolute path

### JSONL per-record Foundation validation

- Each non-empty JSONL line: parse → dangerous-key/resource checks → **Foundation validation** → normalized append
- Validator invoked: `validateFoundationJsonRecord()` in `file-production-normalizer.ts`
- Underlying Foundation call: existing `parseJsonImportFile(JSON.stringify(record), policy)` from `file-import-parser.ts`
- Coverage: per-record JSON object shape/depth/field semantics enforced by Foundation parser policy (`jsonMaxDepth`, object/array/scalar rules); does not replace file-level `validateFileCandidate()` for path/candidate semantics
- Foundation rejections map to `FILE_FOUNDATION_VALIDATION_FAILED` with safe `lineNumber`; invalid JSON remains `FILE_JSONL_INVALID`; dangerous keys remain `FILE_DANGEROUS_KEY_REJECTED`; partial success is prohibited

### Verifier hardening

- Scans `src/runtime/index.ts`, `src/runtime/connector-manager.ts`, and `src/runtime/connector-registry.ts` for production adapter references (direct import, require, dynamic import, alias/barrel patterns)
- Compares `AN_VANTARIS_EDGE/package.json`, repo `package.json`, and `package-lock.json` against `git show HEAD:` (fail closed on drift)
- Verifies regular-file checks in path policy (`lstat` + `isFile()`) and adapter read path (`inspectRegularFilePath`, `postStat.isFile()`)
- Detects exposed write APIs (`export const write`, `export function write`, `readonly write`, bracket exports, etc.) on comment-stripped production sources
- Requires opaque path hash, `validateFoundationJsonRecord()` invocation in adapter, and JSONL record Foundation integration
- Static scanning limitations: heuristic regex/comment stripping; real adapter negative fixtures and dry-run matrix supplement AST-level gaps

## Adapter architecture

Production code lives under `src/connectors/file/production/` and is isolated from foundation modules under `src/connectors/file/`.

Call chain:

1. File production configuration validation
2. Allowlisted root resolution via `rootReferenceId + inputRelativePath`
3. Canonical path resolution and regular-file inspection
4. Foundation candidate/policy validation (JSON/CSV file-level; JSONL per-record via `parseJsonImportFile`)
5. Bounded read-only open and UTF-8 validation
6. JSON / JSONL / CSV parsing
7. Normalization to canonical field records
8. Result returned to explicit caller only

The adapter exports `readOnce` only. It is not imported by `src/runtime/index.ts`, `connector-manager.ts`, or `connector-registry.ts`.

## Path security

- Explicit allowlisted root via resolver (`rootReferenceId` → session directory in validation)
- Relative input paths only; absolute paths rejected
- Canonical absolute path resolution with `realpath`
- Segment walk with `lstat` symlink rejection
- Denied system roots (`/etc`, `/tmp`, `/var`, etc.) fail closed
- Directory, FIFO, socket, block/char device rejection
- Path logging uses opaque path reference IDs only

### `/` universal deny fix and boundary

- Prior bug: treating `/` as a universal deny caused all absolute-path rejection conflation
- Fix: `/` is denied only when the **allowlisted root itself** resolves to `/` (`allowedRoot === '/'`)
- Root `/` remains explicitly rejected for production allowlist mapping
- This does **not** grant universal access, default allowlist to `/`, or accept arbitrary absolute input paths

## Symlink policy

- Symlink files rejected during segment walk and pre-open inspection
- Symlink directory escape rejected before target resolution

## TOCTOU handling

- Pre-open `lstat` captures dev/inode/size
- Read-only `open` followed by `fstat` identity comparison
- Size re-check at open; mismatch returns `FILE_CHANGED_DURING_OPEN`
- Handles always closed in `finally`

Node cannot fully eliminate platform TOCTOU races. Production enablement still requires deployment-layer directory permissions and mount strategy.

## Supported formats

- JSON (object or array)
- JSONL (one object per non-empty line, per-record Foundation validated)
- CSV (UTF-8, optional BOM, comma delimiter, quoted fields, escaped quotes)

Not supported in this phase: XLS/XLSX, ZIP/TAR, executables, scripts, binary payloads, arbitrary delimiters, multiline quoted CSV fields.

## Parser limits

Enforced limits (positive integers with caps):

- `maxFileBytes`
- `maxLineBytes`
- `maxRecordCount`
- `maxJsonDepth`
- `maxFieldCount`
- `maxFieldLength`
- `maxCsvColumns`
- `maxProcessingMilliseconds`

Invalid config (`0`, negative, string, `NaN`, `Infinity`, above cap) fails closed with `FILE_CONFIG_INVALID`.

## CSV formula policy

Fields with spreadsheet-formula prefixes (`=`, `+`, `-`, `@`) are rejected by default (`formulaPrefixPolicy=REJECT`).

## JSON dangerous-key policy

Prototype pollution keys (`__proto__`, `prototype`, `constructor`) are rejected at any depth (`dangerousKeyPolicy=REJECT`).

## Foundation validation integration

Production adapter calls existing foundation modules:

- `validateFileReadOnlyPolicy` (JSON/CSV policy schema)
- `validateFileCandidate` (file candidate/path semantics)
- `parseJsonImportFile` / `parseCsvImportFile` (parse + record policy)
- `validateFoundationJsonRecord` → `parseJsonImportFile(JSON.stringify(record), policy)` for each JSONL record

Foundation files and synthetic transport behavior were not modified.

## Error taxonomy

Stable codes include:

- `FILE_PATH_NOT_ALLOWLISTED`
- `FILE_PATH_TRAVERSAL_REJECTED`
- `FILE_SYMLINK_REJECTED`
- `FILE_SPECIAL_TYPE_REJECTED`
- `FILE_NOT_FOUND`
- `FILE_NOT_REGULAR`
- `FILE_SIZE_LIMIT_EXCEEDED`
- `FILE_LINE_LIMIT_EXCEEDED`
- `FILE_RECORD_LIMIT_EXCEEDED`
- `FILE_FORMAT_NOT_ALLOWED`
- `FILE_ENCODING_INVALID`
- `FILE_JSON_INVALID`
- `FILE_JSONL_INVALID`
- `FILE_CSV_INVALID`
- `FILE_FORMULA_PREFIX_REJECTED`
- `FILE_DANGEROUS_KEY_REJECTED`
- `FILE_CHANGED_DURING_OPEN`
- `FILE_READ_TIMEOUT`
- `FILE_READ_FAILED`
- `FILE_FOUNDATION_VALIDATION_FAILED`

Errors do not include file contents, credentials, raw customer paths, canonical paths, or realpath values.

## Tests

- Adapter harness: `scripts/validation/lib/file-production-adapter-dry-run-cases.cjs` (actual filename; not `.js`)
- Fixtures under `.runtime/validation-sessions/<unique-session>/` only
- C6-01A additions: path redaction negatives, JSONL per-record Foundation negatives, verifier matrix expansion

## Verifier

`deploy/offline-bundle/scripts/verify-file-production-readonly-adapter-edge.sh` verifies:

- Production directory presence and required files
- Forbidden write/watch/shell/network APIs absent; exposed write API patterns rejected
- Path redaction, regular-file checks, Foundation integration, JSONL record validator invocation
- Runtime index, connector-manager, and connector-registry free of production adapter references
- Package manifests unchanged vs HEAD
- Connector matrix and freeze gates unchanged
- `.runtime` remains untracked

Success tokens include:

- `FILE_PRODUCTION_READONLY_ADAPTER_VERIFIED`
- `FILE_ERROR_PATH_REDACTION_VERIFIED`
- `FILE_JSONL_RECORD_FOUNDATION_VALIDATION_INTEGRATED`
- `FILE_PRODUCTION_ADAPTER_NOT_REGISTERED_IN_RUNTIME`
- `PACKAGE_DEPENDENCY_UNCHANGED_VERIFIED`
- `FILE_REGULAR_FILE_CHECK_VERIFIED`
- `NO_EXPOSED_FILE_WRITE_API`

### Verifier negative matrix (post C6-01A)

- **30/30 REJECTED, 0 LEAKED**
- Token: `VERIFIER_NEGATIVE_TESTS_30_OF_30_REJECTED`

## Dry-run

- Script: `scripts/validation/edge-c6-file-production-adapter-dry-run.sh`
- **166 cases** (minimum 145): real adapter invocation + 30 canonical verifier negatives + supplemental negatives
- Success: `edge-c6-file-production-adapter-dry-run: PASS`
- Readiness: `UFMS_EDGE_C6_01_FILE_PRODUCTION_ADAPTER_PASS`
- Closure: `UFMS_EDGE_C6_01A_VERIFICATION_CLOSURE_PASS`

## Smoke

- Script: `scripts/validation/edge-c6-file-production-adapter-smoke.sh`
- Checks required files, fixtures, allowlist, limits, dangerous keys, formula rejection, verifier, blocked gate, no runtime registration, `.runtime` hygiene

## Validation results (C6-01A closure)

| Check | Result |
|-------|--------|
| `npm run typecheck:edge` | PASS |
| `edge-c6-file-production-adapter-dry-run.sh` | PASS (166/166) |
| `edge-c6-file-production-adapter-smoke.sh` | PASS |
| `verify-file-production-readonly-adapter-edge.sh` | PASS |
| `validate-edge-package.sh` | PASS |
| `edge-boundary-scan.sh` | PASS |
| `validate-ufms-ibms-isolation.sh` | PASS (`hard_fail_count=0`, cited) |

## Gate state (unchanged)

- `readOnlyFoundationEnforcementGate=PASS`
- `controlledPilotGate=DEFERRED`
- `readOnlyEnforcementGate=DEFERRED`
- `decision=BLOCKED_NOT_PRODUCTION_READY`
- `realConnectivityEnabled=false`
- `supportsWriteback=false`

## Runtime and dependency posture

- **No runtime registration** — production adapter not wired in runtime index, connector-manager, or registry
- **No package changes** — `package.json` / `package-lock.json` unchanged vs HEAD
- **No npm install / no new dependencies**

## Isolation and boundary

- Only `AN_VANTARIS_EDGE/**` modified
- `.runtime` untracked
- No git commit / no push

## Remaining limitations

- File Production Adapter Code Complete ≠ Pilot Approval
- File Production Adapter Code Complete ≠ Production Approval
- `realConnectivityEnabled` remains `false`
- No directory watch, no writeback, no LINK/DB direct access
- Verifier uses static heuristics; dry-run adapter/verifier negatives provide supplemental assurance
- CSV multiline quoted fields explicitly unsupported (fail closed)

## Readiness keys

- `UFMS_EDGE_C6_01_FILE_PRODUCTION_ADAPTER_PASS`
- `UFMS_EDGE_C6_01A_VERIFICATION_CLOSURE_PASS`
- `FILE_PRODUCTION_READONLY_ADAPTER_VERIFIED`
- `FILE_ERROR_PATH_REDACTION_VERIFIED`
- `FILE_JSONL_RECORD_FOUNDATION_VALIDATION_INTEGRATED`
- `FILE_PRODUCTION_ADAPTER_NOT_REGISTERED_IN_RUNTIME`
- `PACKAGE_DEPENDENCY_UNCHANGED_VERIFIED`
- `FILE_REGULAR_FILE_CHECK_VERIFIED`
- `NO_EXPOSED_FILE_WRITE_API`
- `VERIFIER_NEGATIVE_TESTS_30_OF_30_REJECTED`
- `NO_RUNTIME_REGISTRATION`
- `CONNECTOR_STILL_BLOCKED`
- `CONTROLLED_PILOT_GATE_DEFERRED`
- `PRODUCTION_READ_ONLY_GATE_DEFERRED`
