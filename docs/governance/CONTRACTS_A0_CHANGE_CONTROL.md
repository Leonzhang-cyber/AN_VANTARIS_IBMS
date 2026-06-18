# CONTRACTS A0 Change Control

## Contract change request process

1. Open contract change request with scope, rationale, impact, and target artifacts.
2. Map impacted modules/domains and required compatibility strategy.
3. Record required evidence and validation checks before merge.

## Owner review

- Contract owner review is required for all schema/API/envelope/error/status changes.

## Backward compatibility review

- Public API/event/schema changes require explicit backward compatibility assessment.
- Breaking changes require version bump and migration path.

## Security review

- Security review is required for auth, trust, replay/idempotency, and payload integrity changes.

## DB migration review

- Any DB-related contract update requires AN_VANTARIS_DB migration review alignment.

## Generated artifact review

- Generated artifacts must be traceable to source contracts and include contract version reference.

## Release note requirement

- Every approved contract change must include release-note entries with compatibility notes.

## Evidence requirement

- Validation evidence (schema checks, compatibility checks, review sign-offs) must be attached.

## No private runtime schema rule

- Runtime modules must not invent private cross-module schemas outside contracts governance.
