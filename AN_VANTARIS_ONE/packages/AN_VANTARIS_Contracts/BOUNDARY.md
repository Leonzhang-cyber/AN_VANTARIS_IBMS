# AN_VANTARIS_Contracts Boundary

## Allowed responsibilities

- object/API/event/schema/envelope/security/versioning contract definitions
- manifest definitions for module/patch/license/trust contracts

## Forbidden responsibilities

- runtime logic execution
- DB connection
- external service call
- UFMS runtime import

## Dependencies allowed

- documentation and governance inputs
- contract validation tooling

## Dependencies forbidden

- direct coupling to runtime module internals
- direct runtime database operations
