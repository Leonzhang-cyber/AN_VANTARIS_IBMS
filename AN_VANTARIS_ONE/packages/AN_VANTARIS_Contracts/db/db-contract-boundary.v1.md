# DB Contract Boundary v1

## Core rule

`AN_VANTARIS_DB` is implementation mapping, not contract authority.

## Canonical ownership

- Canonical objects and field meanings are defined by `AN_VANTARIS_Contracts`.
- DB implementation may optimize storage but must preserve canonical semantics at boundaries.

## Allowed DB implementation extensions

- indexes
- foreign keys
- technical/internal columns
- partitioning and retention implementation details

## Forbidden boundary drift

- DB must not rename canonical identifiers in published API contracts.
- DB-internal fields must not leak into canonical public contract definitions without authority review.
- EDGE/LINK must not directly access DB.
- Code owns DB access boundary for runtime integration.

## Version and migration relationship

- DB migration metadata must map to contract version milestones.
- Contract version changes requiring DB changes must include migration notes and rollback guidance.
