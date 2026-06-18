# VANTARIS ONE Contracts

`contracts/` is the current Contracts source directory for VANTARIS ONE transition.
`AN_VANTARIS_Contracts` target package will be created later.

Contracts are governance/source-of-truth assets, not runtime modules.
Contracts do not connect to DB.
Contracts do not call Edge/Link/Code/Console/NexusAI.
Runtime modules must align to Contracts.
IBMS is retained as ibms-core business module.
UFMS is only referenced through adapter/boundary contracts, not runtime import.

## A0 Baseline Files

- `contract-manifest.json`
- `VERSION`
- `GOVERNANCE.md`
- `VERSIONING_POLICY.md`
- `OBJECT_IDENTITY_STANDARD.md`
- `API_NAMESPACE_POLICY.md`
- `ERROR_CODES.md`
- `STATUS_CODES.md`
- `PORTS_AND_NETWORK_BOUNDARY.md`

## CONTRACTS-A1 Edge/Link Schemas

Schemas:

- `schemas/edge-link/edge-normalized-object.schema.json`
- `schemas/edge-link/link-envelope.schema.json`
- `schemas/edge-link/link-ack.schema.json`
- `schemas/edge-link/link-retry-policy.schema.json`
- `schemas/edge-link/link-dlq.schema.json`
- `schemas/edge-link/link-replay-request.schema.json`
- `schemas/edge-link/link-route-policy.schema.json`
- `schemas/edge-link/link-message-state.schema.json`
- `schemas/edge-link/link-delivery-audit.schema.json`

Examples:

- `examples/edge-link/edge-normalized-telemetry.example.json`
- `examples/edge-link/edge-normalized-event.example.json`
- `examples/edge-link/edge-normalized-alarm.example.json`
- `examples/edge-link/link-envelope-telemetry.example.json`
- `examples/edge-link/link-ack-accepted.example.json`
- `examples/edge-link/link-ack-rejected.example.json`
- `examples/edge-link/link-dlq.example.json`
- `examples/edge-link/link-replay-request.example.json`
- `examples/edge-link/link-route-policy.example.json`

These schemas are contract baseline only.
They do not create AN_VANTARIS_EDGE runtime.
They do not create AN_VANTARIS_LINK runtime.
Runtime implementation must follow future EDGE / LINK tasks.
