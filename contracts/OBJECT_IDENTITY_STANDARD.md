# VANTARIS ONE Object Identity Standard

## Standard Object Identity Fields

- globalId: UUID string
- tenantId: string
- projectId: string
- siteId: string
- sourceSystemId: string
- gatewayId: string
- connectorId: string
- assetCode / assetUid
- deviceCode / deviceUid
- pointCode / pointUid
- messageId: UUID
- traceId: UUID
- correlationId: UUID optional
- idempotencyKey: deterministic string

## Time Standard

- ISO-8601 UTC
- sampledAt
- receivedAt
- createdAt
- updatedAt

## Prohibited Identity Practices

- relying only on auto-increment DB id across modules
- using display name as identity
- using raw vendor tag as canonical point identity without mapping
