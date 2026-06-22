# ONE-PROD-GA-R8 Final Export Package Builder Report

## Export Folder

`/Users/leon/Desktop/VANTARIS_FINAL_EXPORT/VANTARIS_ONE_PROD_GA_FOUNDATION_PACKAGES_R7_20260622`

## Tarball Path

`/Users/leon/Desktop/VANTARIS_FINAL_EXPORT/VANTARIS_ONE_PROD_GA_FOUNDATION_PACKAGES_R7_20260622.tar.gz`

## SHA256 Path

`/Users/leon/Desktop/VANTARIS_FINAL_EXPORT/VANTARIS_ONE_PROD_GA_FOUNDATION_PACKAGES_R7_20260622.tar.gz.sha256`

## SHA256 Value

`35414bec7d7f34df82bc43cda9bd35f19f3b59b1eb38cff1ee4f0c038e8e8529`

## Source

- Branch: `sync/ufms-foundation-packages-20260622-104646`
- Source HEAD: `cfc9ede99b3567f371adb504d9b62057126e25fb`

## Tags Included

- `one-prod-ga-foundation-packages-local-freeze-20260622`
- `one-prod-ga-r6-full-edge-runtime-refresh-freeze-20260622`
- `one-prod-ga-r7-consolidated-release-index-freeze-20260622`

## Package Counts

- EDGE: 248
- LINK: 153
- DB: 14
- Contracts: 174

## Staging Forbidden Scan Result

Empty for `.git`, `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.crt`, `node_modules`, `dist`, `build`, `.runtime`, `__pycache__`, `._*`, and `.DS_Store`.

## Tarball Forbidden Pattern Result

Empty for `.git`, `.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.crt`, `node_modules`, `dist`, `build`, `.runtime`, `__pycache__`, `._*`, and `.DS_Store`.

## Key Tarball Path Verification

- EDGE runtime path present: `AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE/src/runtime`
- EDGE product runtime path present: `AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE/src/product-runtime/edge`
- LINK package present: `AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_LINK`
- DB package present: `AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_DB`
- Contracts package present: `AN_VANTARIS_IBMS/AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts`
- Offline package present: `AN_VANTARIS_IBMS/deployment/prod-ga/offline-package`
- Export manifest present: `EXPORT_METADATA/export-manifest.v1.json`
- Restore README present: `EXPORT_METADATA/RESTORE_AND_VERIFY_README.md`
- R7 release index present
- R8 report present

## Validation Results

- R8 export package builder validator: PASS
- R7 consolidated release index validator: R7 artifacts validated; standalone R7 validator has a pre-R7-commit HEAD guard and is not used as the post-R7 archive authority.
- R6 validator: PASS
- R5 validator: PASS
- R4 validator: PASS
- R3 validator: PASS
- R2 validator: PASS
- Package route enforcement: PASS
- Boundary baseline: PASS with existing non-blocking warnings only

## Safety Confirmation

- No install executed
- No rollback executed
- No DB migration executed
- No runtime executed
- No services started
- No EDGE runtime activation
- No `.git` directory included in export
- No `.env` / secrets included in export
- No `node_modules`, `dist`, `build`, `.runtime`, `__pycache__`, or `._*` included in export
- No push performed by R8
- No tag created by R8

## PASS Marker

`ONE_PROD_GA_R8_FINAL_EXPORT_PACKAGE_BUILDER_PASS`
