# Production GA Offline Foundation Package Scaffold

This directory contains the ONE-PROD-GA-R4 offline install / verify / rollback scaffold for the VANTARIS ONE foundation packages:

- EDGE: `AN_VANTARIS_ONE/packages/AN_VANTARIS_EDGE`
- LINK: `AN_VANTARIS_ONE/packages/AN_VANTARIS_LINK`
- DB: `AN_VANTARIS_ONE/packages/AN_VANTARIS_DB`
- Contracts: `AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts`

The package is reference-only. It does not duplicate package contents and does not copy `.env`, credentials, `node_modules`, `dist`, `build`, or `.runtime` files.

## Scripts

- `scripts/install-prod-ga-foundation.sh`: dry-run install plan only by default.
- `scripts/verify-prod-ga-foundation.sh`: read-only manifest/package/forbidden-file verification.
- `scripts/rollback-prod-ga-foundation.sh`: dry-run rollback plan only by default.

## Safety posture

- Installation execution: false by default
- EDGE start: false
- LINK start: false
- DB migration execution: false
- DB write: false
- Runtime activation: false
- UFMS source workspace modification: false
- Push/tag: false

R4 is an operator handoff scaffold only, not a deployment execution.

