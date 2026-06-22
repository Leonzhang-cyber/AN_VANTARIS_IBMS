# LINK-C8-05 — Rollback / Uninstall Plan

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records the LINK offline rollback and uninstall plan.

This task adds structure-only rollback and uninstall planning documentation. It does not execute
rollback, uninstall, runtime deployment, service start, endpoint approval, or production delivery.

## 2. File Added

Added document:

- AN_VANTARIS_LINK/deploy/offline-bundle/docs/ROLLBACK_AND_UNINSTALL_PLAN.md

## 3. Plan Coverage

The plan covers:

- rollback purpose
- rollback scope
- uninstall scope
- required checks before rollback
- required checks after rollback
- required checks before uninstall
- evidence retention rules
- production delivery blocked state
- UFMS DB access blocked state
- writeback blocked state

## 4. Existing Scripts Referenced

Existing structure-only scripts:

- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/install-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/uninstall-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/rollback-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh

## 5. Boundary

This task does not modify EDGE runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not start services.

This task does not delete data.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 6. Result

LINK_C8_05_ROLLBACK_UNINSTALL_PLAN_PASS

LINK offline rollback and uninstall plan is documented.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
