# LINK-C8-04 — Local Healthcheck Script

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records the LINK offline bundle local healthcheck script.

The healthcheck validates that the offline package manifest exists, contracts manifest reference
exists, C7 diagnostics aggregate evidence exists, and production delivery blocking flags remain
enforced.

This task does not start LINK runtime and does not enable production delivery.

## 2. Script Added

Added script:

- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh

## 3. Healthcheck Coverage

The script checks:

- offline package manifest exists
- contracts manifest exists
- LINK-C7 diagnostics aggregate evidence exists
- packageStatus remains STRUCTURE_ONLY
- linkRuntimeEnabled=false
- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- consumerImplementationIncluded=false
- realUfmsApiDeliveryEnabled=false

## 4. Validation Command

Command executed:

- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh

Validation markers:

- LINK_C8_04_LOCAL_HEALTHCHECK_PASS
- LINK_OFFLINE_BUNDLE_HEALTHY
- LINK_C7_DIAGNOSTICS_EVIDENCE_PRESENT
- LINK_CONTRACTS_MANIFEST_REFERENCE_PRESENT
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

LINK_C8_04_LOCAL_HEALTHCHECK_SCRIPT_PASS

LINK offline bundle local healthcheck script is created and validated.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
