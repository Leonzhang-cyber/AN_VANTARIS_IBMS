# AN_VANTARIS_Code Boundary

## Allowed responsibilities

- platform-core runtime
- `ibms-core`, module registry, license gate, patch manager
- API host and orchestration for business modules

## Forbidden responsibilities

- embedding protocol-driver runtime internals directly
- bypassing contracts for cross-module schemas
- unmanaged direct schema mutation across module boundaries

## Dependencies allowed

- `AN_VANTARIS_Contracts`
- `AN_VANTARIS_DB` through approved data access layer

## Dependencies forbidden

- direct dependency on Edge private internals
- direct dependency on Console private internals for business state writes
