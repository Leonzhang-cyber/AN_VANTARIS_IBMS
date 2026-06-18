# CONTRACTS ONE ALIGNMENT

## VANTARIS ONE Contract Source Position

- `contracts/` is the current local contract governance base for VANTARIS ONE alignment in this repository.
- It should evolve toward `AN_VANTARIS_Contracts` target structure in staged tasks.
- Contracts are the single source of truth for cross-module API/Event/Schema/Envelope/Security rules.

## Required Future Structure

Target structure should include at least:

- contract manifest and version policy
- domain schemas (platform/asset/integration/telemetry/event-alarm/work-management/esg/cde/ai/trust/audit)
- openapi/event/protocol/edge-link/module/patch/db/security contracts
- examples and tooling for validation

## P0 Contract Backlog

- contract-manifest
- versioning policy
- object identity standard
- error/status code governance alignment
- edge normalized object schema
- link envelope/ack/retry/dlq contract
- module manifest
- patch manifest
- license VC contract
- CDE base schema
- API namespace policy

## No Runtime Role

- Contracts are not runtime modules.
- Contracts do not execute business logic.

## No DB Connection

- Contracts do not directly connect to DB.
- Contracts provide schema references and contract definitions only.

## No UFMS Runtime Import

- Contracts must not import or embed UFMS runtime/source/schema/auth/login/seed/migration logic.
- UFMS integration is allowed only through approved adapter contracts.

## Contract-first Change Rule

- Every cross-module change must start from contract definition and review.
- Runtime modules cannot invent private cross-module schemas.
- Breaking changes require explicit new contract version.
