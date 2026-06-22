# EDGE-LINK Protocol Profile v1

## Baseline

- `protocolVersion`: `v1`
- `schemaVersion`: `v1`
- Timestamp format: UTC ISO-8601 (`date-time`)

## Identity and tracing

- `traceId` required in `traceContext` and transport headers.
- `correlationId` required for cross-package tracking.
- `idempotencyKey` required for dedupe-safe handoff.
- Machine identity required through `machine-identity-ref-v1`.

## Signature header rules

Required headers:

- `x-vantaris-machine-id`
- `x-vantaris-signature`
- `x-vantaris-signature-algorithm`
- `x-vantaris-signed-at`
- `x-vantaris-trace-id`
- `x-vantaris-idempotency-key`
- `x-vantaris-protocol-version`

## Accepted clock skew recommendation

- Recommended verification tolerance: +/- 300 seconds.

## Retry semantics

- Retry behavior must preserve original `idempotencyKey`.
- Retryable outcomes should signal `retryable=true` and `retryAfterSeconds`.
- Duplicate submissions should resolve deterministically with duplicate-safe acknowledgment.

## Duplicate handling

- LINK should treat duplicate `idempotencyKey` as safe repeat and avoid duplicate side effects.
- ACK payload should expose duplicate or partial success semantics where applicable.

## Unknown field tolerance

- Producers may add optional fields.
- Consumers should ignore unknown fields unless explicitly forbidden by boundary policy.
