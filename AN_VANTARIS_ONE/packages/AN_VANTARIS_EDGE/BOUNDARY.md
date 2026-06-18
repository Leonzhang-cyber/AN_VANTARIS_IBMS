# AN_VANTARIS_EDGE Boundary

## Allowed responsibilities

- protocol adapters and device connectors
- tag mapping and data normalization
- local buffering and edge health diagnostics

## Forbidden responsibilities

- direct DB write
- backend DAO coupling
- UI/SSE coupling without adapter
- UFMS runtime import

## Dependencies allowed

- `AN_VANTARIS_Contracts`
- delivery handoff to `AN_VANTARIS_LINK`

## Dependencies forbidden

- direct dependency on business DB runtime
- direct dependency on Console runtime internals
