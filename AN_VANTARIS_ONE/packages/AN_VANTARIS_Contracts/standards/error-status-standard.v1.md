# Error and Status Standard v1

## Global error response shape

- Use shared `error-response` schema as baseline shape.
- Required baseline fields: `schemaVersion`, `code`, `message`.
- Recommended contextual fields: `correlationId`, structured `details`.

## Error prefix recommendation

- Use module-friendly code prefixes for discoverability (example: `LINK_*`, `EDGE_*`, `CONTRACT_*`).
- Preserve existing published codes; do not repurpose old codes.

## Retryable vs non-retryable

- Retryable failures should be explicitly indicated via code taxonomy and/or detail field.
- Non-retryable validation/contract failures should be deterministic and stable.

## Validation error

- Must identify schema/field violations in machine-readable details.
- Must include correlation metadata when available.

## Auth/signature error

- Must distinguish identity/auth failures from signature integrity failures.
- Must avoid leaking sensitive verification internals.

## Version mismatch error

- Must indicate supported version range and received version.
- Must include recommended upgrade/downgrade action.

## Processing status lifecycle

- Define state machine for transport and processing states.
- Ensure status transitions are deterministic and auditable.
- Avoid ambiguous terminal statuses.
