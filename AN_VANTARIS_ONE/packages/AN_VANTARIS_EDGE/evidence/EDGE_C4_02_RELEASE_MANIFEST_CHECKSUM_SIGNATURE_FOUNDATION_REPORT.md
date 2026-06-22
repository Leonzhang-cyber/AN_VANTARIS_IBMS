# EDGE C4-02 Release Integrity Foundation Report

## Scope

C4-02 establishes local release integrity foundation artifacts under `AN_VANTARIS_EDGE/**` only.

## Baseline commit

- `233e7d4 feat(edge): add offline lifecycle scaffold`

## Release identity

- `releaseId`: `vantaris-edge-foundation-c4-02`
- `product`: `AN_VANTARIS_EDGE`
- `releaseClassification`: `FOUNDATION_ONLY`
- `productionRelease`: `false`

## File inventory

- Deterministic inventory generated from allowed roots only:
  - `AN_VANTARIS_EDGE/src/**`
  - `AN_VANTARIS_EDGE/config/**`
  - `AN_VANTARIS_EDGE/deploy/**`
  - `AN_VANTARIS_EDGE/scripts/**`
  - `AN_VANTARIS_EDGE/docs/**`
  - Allowed static release evidence under `AN_VANTARIS_EDGE/evidence/**`
- Inventory excludes `.runtime`, `node_modules`, `dist`, `build`, `coverage`, `logs`, temp files, and sensitive/private-material patterns.

## SHA-256 checksum model

- Per-file checksum algorithm is fixed to `SHA-256`.
- `CHECKSUMS.edge.json` includes file-level `path`, `sizeBytes`, and `sha256`.

## Aggregate digest model

- Aggregate digest is calculated from stable sorted lines:
  - `path + ":" + sha256`
- Hash algorithm for aggregate digest is `SHA-256`.

## Determinism

- Repeated generation over unchanged input yields:
  - same inventory order,
  - same per-file SHA-256 values,
  - same aggregate digest.

## Tamper detection

- Integrity verification fails when a manifest-inventory file is modified after generation.

## Missing/extra file behavior

- Missing file in inventory fails verification.
- Extra unmanifested file can be detected and blocked with strict extra-file mode.

## Path traversal protection

- Verifier rejects traversal paths and out-of-bound manifest/checksum/signature paths.

## External symlink protection

- Verifier rejects symlinked inventory entries that resolve outside EDGE root.

## Signature metadata scaffold

- Signature metadata is synthetic scaffold only:
  - `signatureStatus=NOT_PRODUCTION_SIGNED`
  - `signatureMode=SYNTHETIC_METADATA_ONLY`
  - `detachedSignaturePresent=false`
  - `hsmBacked=false`
  - `pkcs11Backed=false`
  - `productionCertification=false`

## Production signature limitations

- C4-02 does not perform cryptographic production signature verification.
- C4-02 rejects unsigned production release configuration.

## HSM/PKCS#11 deferral

- HSM/PKCS#11 integration is explicitly deferred to later security phases.

## Release acceptance result

- C4-02 accepted state: `FOUNDATION_ACCEPTED_NOT_PRODUCTION`.

## Lifecycle integration boundary

- C4-02 provides release integrity decision only.
- C4-01 lifecycle scaffold behavior remains unchanged.
- No automatic wiring to real install/upgrade/rollback execution in this phase.

## Dry-run result

- `edge-c4-release-integrity-dry-run: PASS`

## Lightweight smoke result

- `edge-c4-release-integrity-smoke: PASS`

## Explicit safety statements

- Explicit no-real-key statement: no real private keys are generated, loaded, or stored.
- Explicit no-production-signature statement: production signature remains absent.
- Explicit no-network statement: no network access in C4-02 scaffold flow.

## Readiness key

`UFMS_EDGE_C4_02_RELEASE_MANIFEST_CHECKSUM_SIGNATURE_FOUNDATION_PASS`
