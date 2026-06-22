# Machine Identity Standard v1

## Scope

Defines machine identity contract requirements for EDGE/LINK integration.

## Required machine identity fields

- `machineId`
- `gatewayId`
- `linkId`
- `tenantId`
- `siteId`
- `trustDomain`
- `keyId`
- `credentialType`
- `issuedAt`
- `expiresAt`

## Rules

- Machine identity must not rely on human user JWT semantics.
- EDGE/LINK integrations must use machine identity contracts.
- `keyId` and `trustDomain` must be stable and verifiable across handoff boundaries.
- Timestamps follow UTC ISO-8601 standard.

## Security posture

- Identity examples must use fake values only.
- Private keys/secrets must never be embedded in contracts/examples.
