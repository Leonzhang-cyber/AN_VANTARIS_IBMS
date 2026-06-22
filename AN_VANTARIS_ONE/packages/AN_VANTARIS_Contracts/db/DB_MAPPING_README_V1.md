# DB Mapping README v1

## 1. Purpose

Define P1B DB mapping guidance that connects canonical contracts to DB implementation layers without changing contract authority ownership.

## 2. Reading order

1. `AN_VANTARIS_Contracts/db/db-contract-boundary.v1.md`
2. `AN_VANTARIS_Contracts/db/canonical-to-db-mapping-baseline.v1.md`
3. `AN_VANTARIS_Contracts/db/canonical-to-db-map.v1.yaml`
4. `AN_VANTARIS_Contracts/db/field-type-mapping.v1.yaml`
5. `AN_VANTARIS_Contracts/db/migration-metadata-contract.v1.yaml`

## 3. DB boundary rule

`AN_VANTARIS_DB` is implementation mapping, not contract authority. Canonical meaning and identifier semantics remain owned by `AN_VANTARIS_Contracts`.

## 4. Canonical-to-DB mapping usage

Use `canonical-to-db-map.v1.yaml` to map each canonical object to:

- DB layer
- suggested table
- required canonical fields
- technical fields and index hints
- write/read ownership expectations

## 5. Field type mapping usage

Use `field-type-mapping.v1.yaml` as DB type guidance for IDs, status fields, timestamps, numeric telemetry, booleans, JSON payloads, arrays, trace context, idempotency keys, and hash fields.

## 6. Migration metadata usage

Use `migration-metadata-contract.v1.yaml` as migration governance metadata contract. It records migration-to-contract linkage, compatibility mode, rollout/rollback expectations, and approval checkpoints.

## 7. EDGE/LINK no-direct-DB rule

EDGE/LINK must not direct-write UFMS DB. Runtime integration with persistence flows through Code-owned boundaries.

## 8. Code owns DB persistence

Code orchestrates canonical write paths into DB layers and enforces identifier/trace/idempotency semantics at the persistence boundary.

## 9. P1B current scope

- Canonical-to-DB mapping guidance
- Field-type mapping guidance
- Migration metadata contract template
- Validator baseline checks for required DB mapping artifacts

## 10. Future work

- YAML semantic validation (structure/ruleset checks)
- DB migration drift validation against canonical contract milestones
- Extended retention and compliance policy profiles per object family
