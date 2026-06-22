# AN_VANTARIS_Contracts

Unified Contract Source of Truth for VANTARIS ONE platform integration.

## Authority baseline

- `AN_VANTARIS_Contracts` is the contract authority for VANTARIS ONE, UFMS, EDGE, LINK, Code, DB, Console, and NexusAI.
- VANTARIS ONE naming is platform-level; UFMS naming is used only for UFMS product profile semantics.
- Runtime packages must consume contracts from this authority and must not redefine them independently.
- Contracts authority must not import runtime packages or depend on runtime implementation details.
- Generated consumer outputs are downstream artifacts only and are not authority.

## Scope

This package governs:

- JSON Schemas in `schemas/`
- OpenAPI boundary contracts in `openapi/`
- error/status registries in `errors/` and `status/`
- standards and canonical model guidance in `standards/` and `canonical/`
- DB boundary guidance in `db/`
- security boundary guidance in `security/`
- engineer-facing rollout docs in `engineering-handoff/`, `versions/`, and `dto-examples/`

## Consumers

Primary consumers:

- `AN_VANTARIS_EDGE`
- `AN_VANTARIS_LINK`
- `AN_VANTARIS_Code`
- `AN_VANTARIS_DB`
- `AN_VANTARIS_Console`
- `AN_VANTARIS_NexusAI`

## Ownership and lifecycle

- Authority edits happen in UFMS workspace only.
- Contract release/versioning is controlled by this package metadata (`VERSION`, `CHANGELOG.md`, `contract-manifest.json`).
- Any breaking contract change requires explicit major version progression and compatibility documentation.

## High-level rules

- Do not place secrets in schemas/examples/docs.
- Do not encode DB implementation leakage into canonical contracts.
- Do not couple contracts to package-private runtime code.
- Treat generated consumers as copies derived from authority, never the source.

## Immediate next phase

Governance baseline is established in A1A. Detailed P0 EDGE/LINK protocol schemas and OpenAPI artifacts follow in A1B.
