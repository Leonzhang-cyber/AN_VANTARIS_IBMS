# Contract Governance

## Authority ownership

- `AN_VANTARIS_Contracts` is the single contract authority.
- Authority ownership is maintained in UFMS workspace governance flow.
- Runtime packages and generated outputs are consumers, not authority.

## Allowed contract changes

- Additive optional fields.
- New non-breaking enum values where consumers tolerate unknown values.
- New endpoints and schemas that do not alter existing required fields.
- Clarifying docs/examples that preserve protocol semantics.

## Backward-compatible changes

- Optional field additions are backward-compatible.
- New error/status codes are allowed when existing behavior is preserved.
- Deprecated fields can be annotated but must remain readable.

## Breaking changes

- Removing existing fields after release.
- Changing field type/meaning for existing contract fields.
- Changing required field sets in released contracts.
- Renaming or reusing previously published error codes.

Breaking changes require major version increment and explicit compatibility documentation.

## Deprecation policy

- Mark deprecations in schema description/docs/changelog.
- Keep deprecated fields readable for at least one major compatibility window.
- Provide migration guidance before removal in a later major.

## Review requirements

- Changes to required fields require explicit contract review approval.
- Changes affecting security, identity, signature, or trace rules require security review.
- Changes affecting cross-package boundaries require architecture review.

## JSON Schema and OpenAPI relationship

- JSON Schema defines payload structure and validation shape.
- OpenAPI defines transport boundary and operation semantics.
- OpenAPI payload schemas must reference authority JSON Schemas where possible.

## DTO example requirement

- Integration-facing contracts must include realistic examples in `dto-examples/`.
- Examples must align with released schema/OpenAPI versions.
- Examples must not contain real credentials, secrets, or customer data.

## Generated consumer rule

- Generated consumers are downstream artifacts derived from authority contracts.
- Generated files must include generated banner and must not be edited manually.
- Authority changes must occur in this package first, then regenerate consumers.

## No runtime imports rule

- Authority contract files/docs must not import runtime package code.
- Contract definitions must remain implementation-agnostic.

## No secrets and implementation leakage

- No real secret values in examples or docs.
- No DB implementation leakage into canonical contracts.
- DB-level indexing/engine specifics belong to DB mapping docs, not core canonical schemas.

## IEC 62443 aligned governance

- Security baseline governance is IEC 62443 aligned and evidence-driven.
- Security-relevant contract changes must update security baseline evidence artifacts.
- Security baseline changes require explicit security review before merge.
- Certification claims are prohibited without third-party certification evidence.
- Use wording such as "IEC 62443 aligned" and "certification-ready evidence baseline".
