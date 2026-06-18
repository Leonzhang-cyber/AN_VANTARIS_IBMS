# AN_VANTARIS_DB Boundary

## Allowed responsibilities

- PostgreSQL schema baseline and version governance
- migration framework ownership
- backup/restore and archive boundary definitions

## Forbidden responsibilities

- business runtime logic implementation
- secret storage in repository
- unmanaged cross-module schema mutation

## Dependencies allowed

- `AN_VANTARIS_Contracts` for schema reference and versioning rules
- approved migration interfaces from `AN_VANTARIS_Code`

## Dependencies forbidden

- direct runtime business flow orchestration
- direct UI control logic
