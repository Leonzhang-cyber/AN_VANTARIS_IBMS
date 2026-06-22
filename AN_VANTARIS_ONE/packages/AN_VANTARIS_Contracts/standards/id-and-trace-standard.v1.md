# ID and Trace Standard v1

## Scope

Defines required identifier and trace fields used across contracts.

## Core identifiers

- `eventId`: immutable identifier for a domain event.
- `envelopeId`: transport envelope identifier for delivery unit.
- `correlationId`: end-to-end request/message correlation key.
- `traceId`: distributed trace root identifier.
- `idempotencyKey`: dedupe-safe operation identifier.

## Domain identifiers

- `tenantId`: tenant boundary identifier.
- `siteId`: site/facility identifier.
- `gatewayId`: edge gateway identifier.
- `connectorId`: connector/integration source identifier.
- `assetId`: canonical asset identifier.
- `deviceId`: device identifier.
- `pointId`: telemetry point identifier.

## Naming recommendation

- Use lowerCamelCase field names ending with `Id`.
- Identifier values should be opaque and stable.
- Prefer UUID/ULID or deterministic namespaced IDs where applicable.

## Trace requirements

- `correlationId` required for cross-package flows.
- `traceId` required for observability-capable flows.
- `idempotencyKey` required for retry-prone write/delivery operations.

## Privacy and security

- IDs must not embed PII.
- IDs must not embed secret values or credentials.
- Avoid exposing internal DB implementation IDs as canonical public contract IDs.
