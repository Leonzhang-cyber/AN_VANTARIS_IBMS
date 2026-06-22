# PKG-LINK-03 — Package Integrity Manifest and Checksum Foundation

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence records LINK independent install package integrity manifest and checksum foundation.

This task adds a release manifest, checksum foundation, and release integrity policy.

This task does not assemble a real artifact, execute real install, start services,
approve endpoints, enable production delivery, connect to UFMS API, access UFMS DB,
or enable writeback.

## 2. Files Added

Added files:

- AN_VANTARIS_LINK/deploy/offline-bundle/integrity/RELEASE_MANIFEST.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/integrity/CHECKSUMS.link.json
- AN_VANTARIS_LINK/deploy/offline-bundle/integrity/RELEASE_INTEGRITY_POLICY.link.md

## 3. Release Manifest Coverage

Release manifest covers:

- package manifest reference
- lifecycle manifest reference
- release layout reference
- rollback plan reference
- contracts manifest reference
- required release file list
- blocked runtime boundary flags

## 4. Checksum Foundation Coverage

Checksum foundation covers:

- checksum manifest version
- sha256 algorithm declaration
- checksum generation deferred state
- real artifact assembly blocked state
- production delivery blocked state

## 5. Integrity Policy Coverage

Release integrity policy covers:

- required integrity inputs
- required validation rules
- release file existence checks
- contracts manifest reference check
- package verification check
- healthcheck check
- typecheck check
- boundary scan check
- runtime blocked state

## 6. Validation Commands

Commands executed:

- Python release integrity validation
- node AN_VANTARIS_Contracts/scripts/validate-all-contract-schemas.mjs
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/verify-link-offline-package.sh
- bash AN_VANTARIS_LINK/deploy/offline-bundle/scripts/healthcheck-link-offline.sh
- npm --prefix AN_VANTARIS_LINK run typecheck
- bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh

## 7. Boundary

This task does not modify EDGE runtime.

This task does not modify UFMS backend/frontend.

This task does not change DB/schema/migration/auth/login/credentials.

This task does not implement VANTARIS ONE, UMMS, MMS, or UCDE runtime.

This task does not enable LINK production delivery.

This task does not approve endpoints.

This task does not start services.

This task does not execute real install.

This task does not assemble real production artifact.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

## 8. Result

PKG_LINK_03_PACKAGE_INTEGRITY_MANIFEST_CHECKSUM_FOUNDATION_PASS

LINK package integrity manifest and checksum foundation are defined.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
