# Engineer Handoff Baseline

## Read this first

1. `AN_VANTARIS_Contracts/README.md`
2. `AN_VANTARIS_Contracts/GOVERNANCE.md`
3. `AN_VANTARIS_Contracts/contract-manifest.json`
4. `AN_VANTARIS_Contracts/standards/`
5. `AN_VANTARIS_Contracts/openapi/` and `schemas/`

## What is stable now

- Contract authority ownership model
- Governance and compatibility baseline
- Existing LINK/Code/Console/NexusAI contract artifacts
- Standards/canonical/db/security baseline guidance

## What is pending (A1B)

- P0 EDGE/LINK protocol schemas
- EDGE-to-LINK OpenAPI/handoff spec
- expanded DTO examples for integration execution

## How to use examples

- Use examples only if they match authority schemas/OpenAPI version.
- Treat examples as guidance, not replacement for schema validation.
- Never use real secrets in examples.

## Critical rule

Do not rely on runtime source files as contract authority. Runtime implementations must consume `AN_VANTARIS_Contracts`.

## Integration checklist placeholder

- [ ] Confirm contract package version
- [ ] Confirm schema/OpenAPI compatibility
- [ ] Confirm required identity/signature/trace headers
- [ ] Confirm retry/idempotency behavior
- [ ] Confirm validation/error handling expectations
