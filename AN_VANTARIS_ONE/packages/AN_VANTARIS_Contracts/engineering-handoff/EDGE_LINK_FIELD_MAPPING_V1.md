# EDGE LINK Field Mapping v1

## A) Wire Event mapping

| Field | Required | Producer | Consumer | Validation rule | Notes |
|-------|----------|----------|----------|-----------------|-------|
| `schemaVersion` | Yes | EDGE | LINK | const `v1` | Authority schema marker |
| `protocolVersion` | Yes | EDGE | LINK | const `v1` | Transport compatibility key |
| `eventId` | Yes | EDGE | LINK, Code | UUID format | Immutable event identity |
| `eventType` | Yes | EDGE | LINK, Code | non-empty string | Routing and policy |
| `eventCategory` | No | EDGE | LINK, Code | string | Optional category grouping |
| `sourceTimestamp` | Yes | EDGE/source | LINK, Code | ISO-8601 UTC date-time | Source-origin time |
| `observedTimestamp` | Yes | EDGE | LINK, Code | ISO-8601 UTC date-time | Edge observation time |
| `tenantId` | No | EDGE | LINK, Code | non-empty string | Tenant scope |
| `siteId` | No | EDGE | LINK, Code | non-empty string | Site scope |
| `gatewayId` | Yes | EDGE | LINK, Code | non-empty string | Edge gateway identity |
| `connectorId` | Yes | EDGE | LINK, Code | non-empty string | Connector identity |
| `sourceSystemId` | Yes | EDGE | LINK, Code | non-empty string | Upstream source identity |
| `assetId` | No | EDGE | LINK, Code | non-empty string | Domain object reference |
| `deviceId` | No | EDGE | LINK, Code | non-empty string | Device reference |
| `pointId` | No | EDGE | LINK, Code | non-empty string | Point/channel reference |
| `severity` | No | EDGE | LINK, Code | enum critical/high/medium/low/info | Event priority |
| `status` | No | EDGE | LINK, Code | string | Lifecycle/status marker |
| `payload` | Yes | EDGE | LINK, Code | object | Domain data body |
| `traceContext` | Yes | EDGE | LINK, Code | object, `traceId` required | Distributed trace context |
| `correlationId` | No | EDGE | LINK, Code | UUID format | End-to-end correlation |
| `idempotencyKey` | Yes | EDGE | LINK | non-empty string | Dedupe-safe processing |

## B) Signed Handoff Envelope mapping

| Field | Required | Producer | Consumer | Validation rule | Notes |
|-------|----------|----------|----------|-----------------|-------|
| `envelopeId` | Yes | EDGE | LINK | UUID format | Transport envelope identity |
| `schemaVersion` | Yes | EDGE | LINK | const `v1` | Envelope schema marker |
| `protocolVersion` | Yes | EDGE | LINK | const `v1` | Protocol compatibility marker |
| `createdAt` | Yes | EDGE | LINK | ISO-8601 UTC date-time | Envelope creation time |
| `producer` | No | EDGE | LINK | enum `AN_VANTARIS_EDGE` | Producer package marker |
| `machineIdentity` | Yes | EDGE | LINK | schema ref validation | Machine trust identity |
| `traceContext` | No | EDGE | LINK | object | Correlated trace state |
| `headers` | Yes | EDGE | LINK | schema ref validation | Required transport headers |
| `signature` | No | EDGE | LINK | non-empty string | Header/body parity checks may apply |
| `wireEvent` | Yes | EDGE | LINK | schema ref validation | Embedded event body |
| `idempotencyKey` | Yes | EDGE | LINK | non-empty string | Dedupe key at envelope level |

## C) Required headers mapping

| Field | Required | Producer | Consumer | Validation rule | Notes |
|-------|----------|----------|----------|-----------------|-------|
| `x-vantaris-machine-id` | Yes | EDGE | LINK | non-empty string | Machine identity routing |
| `x-vantaris-signature` | Yes | EDGE | LINK | non-empty string | Signature value |
| `x-vantaris-signature-algorithm` | Yes | EDGE | LINK | non-empty string | Algorithm identifier |
| `x-vantaris-signed-at` | Yes | EDGE | LINK | ISO-8601 UTC date-time | Replay-window check |
| `x-vantaris-trace-id` | Yes | EDGE | LINK | non-empty string | Trace continuity |
| `x-vantaris-idempotency-key` | Yes | EDGE | LINK | non-empty string | Duplicate protection |
| `x-vantaris-protocol-version` | Yes | EDGE | LINK | non-empty string | Version compatibility gate |
