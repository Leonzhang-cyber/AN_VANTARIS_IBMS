# EDGE C3-01 File Import Connector Foundation Report

## Scope

This phase introduces local file import connector foundation to validate real input file ingestion into the existing EDGE pipeline without introducing real device, network, LINK, DB, or API integration.

## File import objective

Enable controlled local synthetic file input via protocol `file`, prove end-to-end processing through C2 pipeline components, and keep strict read-only and boundary-safe behavior.

## Files changed

- `src/runtime/file-import-types.ts`
- `src/runtime/file-import-reader.ts`
- `src/runtime/plugins/file-import-protocol-plugin.ts`
- `src/runtime/protocol-plugin-registry.ts`
- `src/runtime/connector-manager.ts` (pipeline compatibility retained)
- `src/runtime/edge-diagnostics-cli.ts`
- `src/runtime/index.ts`
- `config/samples/file-import-sample.jsonl`
- `config/connectors.example.json`
- `scripts/validation/edge-c3-file-import-connector-dry-run.sh`
- `scripts/validation/edge-c3-file-import-connector-smoke.sh`
- `evidence/EDGE_C3_01_FILE_IMPORT_CONNECTOR_FOUNDATION_REPORT.md`

## File import plugin behavior

- Implements protocol plugin contract: `initialize`, `start`, `stop`, `pollOnce`, `diagnostics`.
- Uses protocol `file` and keeps `supportsWriteback: false`.
- Reads synthetic local file only after allowlist path validation.
- Supports JSON and JSONL parse path through reader.
- Returns parse/validation diagnostics without external calls.
- On parse/path errors returns failed/degraded diagnostics and does not call network/LINK/DB/API.

## Path allowlist policy

- Allowed roots:
  - `AN_VANTARIS_EDGE/config/samples/**`
  - `AN_VANTARIS_EDGE/.runtime/input/**`
- Denied examples:
  - user home/Desktop/Downloads/Documents
  - `/etc`, `/var`, `/tmp`
  - arbitrary external system paths
- Reader enforces resolved absolute-path containment checks.

## Format support

- Supported: `json`, `jsonl`
- Includes:
  - file size limit (default 1MB)
  - JSONL line limit (default 5000)
  - per-record validation with non-crashing malformed handling

## Pipeline integration

File import samples flow through existing chain:

Protocol Plugin Runtime
→ Normalization Pipeline
→ Edge Envelope
→ Local Buffer
→ Local Delivery Orchestrator
→ Delivery Audit Chain

No bypass added for connector manager, normalization pipeline, envelope builder, local buffer store, or delivery audit chain.

## Validation result

- Typecheck edge/link/edge-link pass.
- C3-01 dry-run pass.
- C3-01 smoke pass.
- C3-00 readiness gate smoke pass.
- C2 foundation freeze smoke pass.
- Edge package/boundary/isolation validators pass (isolation pass with warnings and `hard_fail_count=0`).

## Evidence paths

- `.runtime/evidence/edge-c3-file-import-connector-evidence.json`
- `.runtime/evidence/edge-c3-file-import-sample-parse.json`
- `.runtime/evidence/edge-c3-file-import-pipeline-summary.json`

## Runtime artifact hygiene

- `.runtime` remains untracked by git.
- Runtime evidence JSON files are not committed.

## Boundary confirmation

- Changes remain within `AN_VANTARIS_EDGE`.
- No prohibited package boundary changes.

## No LINK/DB/API/device integration confirmation

- No LINK delivery integration.
- No DB integration.
- No UFMS API integration.
- No real device connection.
- No real OT protocol library introduced.

## Known limitations

- File import accepts only local synthetic files under strict allowlist.
- No production credential path or customer dataset integration.
- No writeback functionality.

## Next recommended phase

C3-02 HTTP Polling Connector Foundation.

## Readiness key

`UFMS_EDGE_C3_01_FILE_IMPORT_CONNECTOR_FOUNDATION_PASS`
