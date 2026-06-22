# PKG-LINK-02 — Install / Uninstall / Upgrade / Rollback Plans

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records LINK independent install package lifecycle plans for install,
uninstall, upgrade, and rollback.

This task defines dry-run-only lifecycle planning. It does not execute real install,
uninstall, upgrade, rollback, service start, service stop, endpoint approval, production
delivery, UFMS API delivery, UFMS DB access, or writeback.

## 2. Files Added

Added lifecycle plans:

- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/INSTALL_PLAN.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/UNINSTALL_PLAN.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/UPGRADE_PLAN.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/lifecycle/ROLLBACK_PLAN.link.json

## 3. Install Plan Coverage

Install plan covers:

- package verification
- planned runtime user creation
- planned package file staging
- planned config example staging
- planned systemd template staging
- local healthcheck
- realInstallExecuted=false
- serviceStartExecuted=false
- production delivery blocked

## 4. Uninstall Plan Coverage

Uninstall plan covers:

- operator approval requirement
- evidence retention requirement
- planned service stop
- planned service template removal
- planned package file removal
- mandatory evidence preservation
- realUninstallExecuted=false
- dataDeletionExecuted=false

## 5. Upgrade Plan Coverage

Upgrade plan covers:

- current package state recording
- target package state recording
- rollback plan requirement
- package verification
- local healthcheck
- realUpgradeExecuted=false
- serviceRestartExecuted=false

## 6. Rollback Plan Coverage

Rollback plan covers:

- rollback target verification
- previous package restore planning
- previous config reference restore planning
- package verification
- healthcheck
- rollback evidence
- realRollbackExecuted=false
- dataDeletionExecuted=false

## 7. Validation Commands

Commands executed:

- Python lifecycle plan validation
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

This task does not start services.

This task does not execute real install, uninstall, upgrade, or rollback.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 9. Result

PKG_LINK_02_INSTALL_UNINSTALL_UPGRADE_ROLLBACK_PLANS_PASS

LINK install / uninstall / upgrade / rollback plans are defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
