# AN_VANTARIS_Console Boundary

## Allowed responsibilities

- control plane UI
- user/role/permission administration
- license center and patch center
- Edge/Link/DB/AI admin entry points

## Forbidden responsibilities

- direct business DB bypass writes
- private runtime coupling to Code internals
- embedding backend runtime logic inside UI package

## Dependencies allowed

- `AN_VANTARIS_Contracts`
- admin APIs exposed by `AN_VANTARIS_Code`, `AN_VANTARIS_EDGE`, `AN_VANTARIS_LINK`, `AN_VANTARIS_NexusAI`, `AN_VANTARIS_DB`

## Dependencies forbidden

- direct mutation of business schemas
- direct execution of migration/seed logic
