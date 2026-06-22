# PKG-LINK-05 — Uninstall / Upgrade / Rollback Dry-run Validation

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records LINK independent package uninstall / upgrade / rollback dry-run validation.

This task validates that uninstall and rollback scripts remain structure-only and that upgrade / rollback plans remain dry-run-only.

This task does not perform real uninstall, upgrade, rollback, service stop, service restart, data deletion, endpoint approval, production delivery, UFMS API delivery, UFMS DB access, or writeback.

## 2. Scripts Validated

Validated scripts:

- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/uninstall-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/rollback-link.sh

## 3. Plans Validated

Validated lifecycle plans:

- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/UNINSTALL_PLAN.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/UPGRADE_PLAN.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/ROLLBACK_PLAN.link.json

## 4. Expected Uninstall Dry-run Behavior

Expected behavior:

- emits LINK_UNINSTALL_STRUCTURE_ONLY
- emits LINK_NO_RUNTIME_REMOVAL_EXECUTED
- emits LINK_NO_DATA_DELETION_EXECUTED

## 5. Expected Rollback Dry-run Behavior

Expected behavior:

- emits LINK_ROLLBACK_STRUCTURE_ONLY
- emits LINK_ROLLBACK_NOT_EXECUTED
- emits LINK_PRODUCTION_DELIVERY_REMAINS_BLOCKED

## 6. Upgrade Dry-run Boundary

Upgrade plan confirms:

- realUpgradeExecuted=false
- serviceRestartExecuted=false
- linkRuntimeEnabled=false
- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false

## 7. Validation Commands

Commands executed:

- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/uninstall-link.sh
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/rollback-link.sh
- node AN_VANTARIS_Contracts/scripts/validate-all-contract-schemas.mjs
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh
- npm --prefix AN_VANTARIS_LINK run typecheck
- bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh

## 8. Boundary

This task does not modify EDGE runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not stop services.

This task does not restart services.

This task does not execute real uninstall.

This task does not execute real upgrade.

This task does not execute real rollback.

This task does not delete data.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 9. Result

PKG_LINK_05_UNINSTALL_UPGRADE_ROLLBACK_DRY_RUN_VALIDATION_PASS

LINK uninstall / upgrade / rollback dry-run validation is complete.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
