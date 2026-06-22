# DB Engineer Contract Note v1

## 1) Authority boundary

DB is implementation mapping, not contract authority.

## 2) Access ownership

Code owns DB access.

## 3) EDGE/LINK database rule

EDGE/LINK must not direct-write UFMS DB.

## 4) Canonical identifier integrity

Canonical identifiers (`tenantId`, `siteId`, `gatewayId`, `connectorId`, `assetId`, `deviceId`, and related IDs) must be preserved across API and DB mapping.

## 5) Allowed DB implementation extensions

DB can add indexes, foreign keys, and technical fields for performance and operability.

## 6) Version linkage

DB migration metadata should reference contract version milestones.

## 7) Layer relationship

- Event layer: normalized events/alarms and processing state.
- Config layer: configuration and versioned profile state.
- Raw layer: source payload snapshots and transport metadata.
- Insight layer: downstream triage/recommendation outcomes.

## 8) Pending P1

P1 DB mapping YAML is available:

- `AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml`
- `AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml`
- `AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml`

## 9) How DB engineers should use P1B files

- Start with `canonical-to-db-map.v1.yaml` to align canonical objects with DB layers, suggested tables, ownership, and retention class.
- Use `field-type-mapping.v1.yaml` for type/index/nullability guidance when implementing storage structures.
- Attach `migration-metadata-contract.v1.yaml` metadata to migration planning/review artifacts for contract-version traceability.

## 10) Important scope guard

DB mapping YAML is contract guidance, not Prisma schema or migration execution content.
