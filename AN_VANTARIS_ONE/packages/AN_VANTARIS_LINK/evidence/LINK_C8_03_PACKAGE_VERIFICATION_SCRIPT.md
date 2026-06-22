# LINK-C8-03 — Package Verification Script

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records the LINK offline package verification script.

The verification script validates the offline package manifest, bundle files, executable script
permissions, contracts manifest reference, validation command references, and production delivery
blocking flags.

This task does not enable runtime deployment or production delivery.

## 2. Script Added

Added script:

- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh

## 3. Validation Coverage

The script validates:

- package manifest exists
- manifestVersion is link-offline-package-manifest.v1
- packageName is AN_VANTARIS_LINK_OFFLINE_BUNDLE
- packageStatus remains STRUCTURE_ONLY
- scope remains AN_VANTARIS_LINK
- contracts manifest reference exists
- bundleFiles is present
- required bundle files exist
- executable bundle scripts have executable permission
- validation commands include LINK typecheck
- validation commands include LINK boundary scan
- linkRuntimeEnabled=false
- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- consumerImplementationIncluded=false
- realUfmsApiDeliveryEnabled=false

## 4. Validation Command

Command executed:

- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh

Validation markers:

- LINK_C8_03_PACKAGE_VERIFICATION_SCRIPT_VALIDATE_PASS
- LINK_OFFLINE_PACKAGE_STRUCTURE_ONLY_CONFIRMED
- LINK_PRODUCTION_DELIVERY_BLOCK_CONFIRMED

## 5. Boundary

This task does not modify EDGE runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 6. Result

LINK_C8_03_PACKAGE_VERIFICATION_SCRIPT_PASS

LINK offline package verification script is created and validated.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
