# LINK-C8-01 — Offline Bundle Structure

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records the LINK offline bundle structure.

This task creates deployment package directories and structure-only scripts for future
offline install, uninstall, rollback, local verification, and package integrity checks.

This task does not enable production delivery.

## 2. Files Added

Offline bundle structure:

- AN_VANTARIS_LINK/deploy/offline-bundle/README.md
- AN_VANTARIS_LINK/deploy/offline-bundle/config/link.env.example
- AN_VANTARIS_LINK/deploy/offline-bundle/systemd/an-vantaris-link.service.template
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/install-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/uninstall-link.sh
- AN_VANTARIS_LINK/deploy/offline-bundle/scripts/rollback-link.sh

Directories added:

- AN_VANTARIS_LINK/deploy/offline-bundle/scripts
- AN_VANTARIS_LINK/deploy/offline-bundle/config
- AN_VANTARIS_LINK/deploy/offline-bundle/systemd
- AN_VANTARIS_LINK/deploy/offline-bundle/manifests
- AN_VANTARIS_LINK/deploy/offline-bundle/evidence
- AN_VANTARIS_LINK/deploy/offline-bundle/docs

## 3. Boundary

This task does not modify EDGE runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 4. Result

LINK_C8_01_OFFLINE_BUNDLE_STRUCTURE_PASS

LINK offline bundle structure is created.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
