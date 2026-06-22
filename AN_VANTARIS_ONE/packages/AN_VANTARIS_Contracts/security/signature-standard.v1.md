# Signature Standard v1

## Signed payload rule

- Signature must be computed over canonical signed payload fields only.
- Unsiged metadata must not alter signature verification result.

## Required headers

Minimum required transport headers:

- signature header
- protocol version header
- trace id header
- idempotency key header
- signedAt timestamp header

Header names can be profile-specific but must be documented in authority schemas/OpenAPI.

## Signature algorithm naming

- Algorithm identifiers must be explicit and stable (example pattern: `HMAC-SHA256`).
- Avoid implicit algorithm defaults.

## Time and correlation requirements

- `signedAt` required for replay control.
- `traceId` required for observability and incident tracing.
- `idempotencyKey` required for retry-safe processing semantics.

## Replay protection

- Consumers should enforce signature age and replay window checks.
- Signature verification must include payload integrity and transport parity checks when defined.

## Example safety rule

- Examples must use fake signatures and fake keys only.
- Never include real secret material in contract docs/examples.
