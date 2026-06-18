# AN_VANTARIS_LINK Boundary

## Allowed responsibilities

- secure delivery and envelope validation
- ACK/retry/DLQ/replay orchestration
- route policy execution and delivery audit

## Forbidden responsibilities

- business logic implementation
- direct business DB write
- Edge driver logic implementation

## Dependencies allowed

- `AN_VANTARIS_Contracts`
- controlled interactions with `AN_VANTARIS_Code` / adapters by route policy

## Dependencies forbidden

- direct dependency on business module runtime internals
- direct dependency on UI module internals
