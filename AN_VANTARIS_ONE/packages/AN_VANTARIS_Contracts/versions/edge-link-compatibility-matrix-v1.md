# EDGE-LINK Compatibility Matrix v1

## Compatibility matrix

| Producer | Consumer | Contract | Status |
|----------|----------|----------|--------|
| EDGE protocol v1 | LINK protocol v1 | `wire-event-v1`, `signed-handoff-envelope-v1`, `edge-handoff-event-v1` | supported |
| LINK delivery v1 | Code API v1 | `link-to-code-delivery.v1.yaml` + `link-message-envelope.v1` | supported |
| Code ack v1 | LINK ack v1 | `code-to-link-ack.v1.yaml` + `delivery-ack.v1` | supported |

## Behavior levels

- **supported**: validated and recommended for active integration.
- **deprecated**: temporarily accepted, migration required.
- **unsupported**: rejected with version mismatch/error response.

## Version mismatch handling

- Reject unsupported protocol/schema versions with `UNSUPPORTED_VERSION`.
- Include actionable message indicating expected version family.
- Do not silently downgrade signed payload semantics.

## Backward compatibility rules

- Additive optional fields are allowed.
- Required field changes require major contract version.
- Field removal after release is forbidden.
- Deprecated fields remain readable through compatibility window.
