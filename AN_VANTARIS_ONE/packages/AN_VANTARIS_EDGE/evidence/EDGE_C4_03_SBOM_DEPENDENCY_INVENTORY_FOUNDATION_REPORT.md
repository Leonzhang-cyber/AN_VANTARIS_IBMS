# EDGE C4-03 SBOM and Dependency Inventory Foundation Report

## Scope

This report captures `UFMS-EDGE-C4-03` delivery for offline SBOM and dependency inventory foundation in `AN_VANTARIS_EDGE/**` only.

## Baseline commit

- `5f8d580 feat(edge): add release integrity foundation`

## Foundation classification

- `SBOM_FOUNDATION_ONLY`
- `productionSbom=false`
- `sbomStandard=INTERNAL_FOUNDATION`

## First-party inventory

- Includes first-party source and deployment script components.
- Inventory is local and deterministic.

## Node dependency inventory

- Based on local `package.json` and `package-lock.json` only.
- Includes built-in modules and lockfile-declared dependencies.
- Distinguishes direct/transitive and production/development/optional scopes.

## OS dependency inventory

- Cross-references:
  - `APT_DEPENDENCIES.edge.txt`
  - `APT_OPTIONAL_SECURITY.edge.txt`
  - `NODE_RUNTIME.edge.txt`
- `installPerformed=false` for all entries.

## Connector dependency inventory

- Covers six connectors: `file`, `http`, `snmp`, `modbus`, `bacnet`, `opcua`.
- Keeps freeze conditions:
  - `syntheticFixtureOnly=true`
  - `realConnectivityEnabled=false`
  - `productionDependencyIncluded=false`
  - `enablementGate=C5-00`

## Security/HSM dependency inventory

- Covers OpenSSL, PKCS#11, OpenSC, pcscd, HSM vendor module, trust store, signing provider, key provisioning.
- `installedByC4_03=false`
- `configured=false`
- `productionEnabled=false`

## License metadata limitations

- Local declaration metadata only.
- Not legal advice.
- No online license verification.
- No formal distribution legal review completion in C4-03.

## Vulnerability assessment limitations

- `assessmentMode=OFFLINE_METADATA_ONLY`
- `assessmentStatus=NOT_SCANNED`
- No network/registry/NVD/OSV/npm audit scans.
- Empty vulnerability list does not imply absence of vulnerabilities.

## Determinism

- Stable component ordering by `componentId`.
- Stable aggregate digest computation from deterministic component fields.
- Repeated generation over same input yields same aggregate digest.

## Aggregate digest

- Computed over sorted:
  - `componentId:version:type:provenanceStatus`

## Release-integrity boundary

- C4-03 provides dependency/SBOM inventory foundation only.
- C4-02 release manifest remains with `sbomPresent=false`.
- No C4-02 checksum/signature behavior changes.

## Dry-run result

- `edge-c4-sbom-inventory-dry-run: PASS`

## Lightweight smoke result

- `edge-c4-sbom-inventory-smoke: PASS`

## Explicit safety statements

- Explicit no-network statement: no external lookups or network scanners were used.
- Explicit no-install statement: no package installation command was executed.
- Explicit no-vulnerability-scan statement: online/offline vulnerability scanners were not run.
- Explicit no-legal-approval statement: legal approval is not completed in C4-03.
- Explicit not-production-SBOM statement: output is foundation-only and not production SBOM.

## Readiness key

`UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS`
