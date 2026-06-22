# VANTARIS ONE Production GA Customer Delivery Edition

PASS marker: `ONE_PROD_GA_R9_FINAL_CUSTOMER_DELIVERY_EDITION_PASS`

## What this package is

This is the final customer delivery edition scaffold for the VANTARIS ONE Production GA foundation package chain. It provides a read-only, engineer-guided delivery plan for importing the offline export, checking package readiness, reviewing installation intent, verifying package integrity, and preparing acceptance evidence.

## What this package is not

This package is not a runtime activation, live installation, DB migration, service start, deployment execution, or customer production cutover. It does not bundle secrets, `.env` files, `node_modules`, `dist`, `build`, or `.runtime` content.

## Offline deployment folder layout

- `customer-delivery.manifest.v1.json` — customer delivery manifest and safety defaults.
- `scripts/precheck-customer-delivery.sh` — dry-run precheck for package counts, forbidden files, OS, disk, and optional R8 export checksum.
- `scripts/install-customer-delivery.sh` — dry-run installation plan; actual execution is intentionally not implemented in R9.
- `scripts/verify-customer-delivery.sh` — read-only verification of packages, reports, UI specs, checklists, and manifest.
- `scripts/rollback-customer-delivery.sh` — dry-run rollback plan; destructive rollback is intentionally not implemented in R9.
- `scripts/package-counts-customer-delivery.sh` — read-only package count summary.
- `ui/` — engineer installer console and customer UI flow specifications only.
- `checklists/` — activation and offline acceptance checklists.

## Engineer workflow

1. Import the R8 offline export package into the agreed staging location.
2. Run precheck in dry-run mode.
3. Review the install dry-run output and approval requirements.
4. Run verify to confirm package counts, forbidden scan status, and delivery artifacts.
5. Use rollback dry-run planning only if a rollback rehearsal is required.
6. Collect acceptance evidence from the generated outputs and checklist sign-offs.

## Customer workflow

1. Review GA readiness and package status.
2. Approve the deployment window.
3. Confirm activation prerequisites and rollback authority.
4. Approve production activation only in a future explicitly authorized phase.
5. Review acceptance evidence and complete handover.

## Safety boundaries

- No default DB migration.
- No default runtime activation.
- No default EDGE or LINK service start.
- No default rollback deletion.
- No production secrets or `.env` files.
- No install, rollback, DB, or runtime execution is performed by R9.

## Required future activation approvals

Production activation requires explicit future approval for installation execution, DB migration, runtime activation, EDGE/LINK startup, rollback authority, acceptance signer, and production support window.
