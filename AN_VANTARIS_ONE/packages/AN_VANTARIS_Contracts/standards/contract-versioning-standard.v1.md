# Contract Versioning Standard v1

## Scope

Defines how contract package versioning, schema versioning, protocol versioning, OpenAPI versioning, and compatibility matrix alignment must work together.

## Semantic versioning

- Contract package uses SemVer-like governance labels in `VERSION`.
- Major: breaking contract changes.
- Minor: additive backward-compatible changes.
- Patch: documentation/clarification/non-structural corrections.

## schemaVersion

- Every released schema must expose `schemaVersion`.
- `schemaVersion` change without compatibility guarantees is treated as a breaking contract event.
- Required field additions/removals require major upgrade.

## protocolVersion

- Transport-level protocolVersion is separate from package version.
- protocolVersion must be explicitly documented in schema and protocol docs.
- Consumers must validate supported protocolVersion range.

## OpenAPI version

- OpenAPI `info.version` must align with the corresponding contract release track.
- Request/response payload references must resolve to authority schemas for the same version family.

## Compatibility matrix relationship

- `versions/` docs must capture producer/consumer compatibility per package version and protocolVersion.
- Matrix is required before promoting a contract baseline to production handoff.

## Minor version compatibility

- Minor upgrades must preserve compatibility with previous minor within same major.
- Consumers should tolerate unknown optional fields.
- Deprecated fields remain readable until major upgrade window closes.

## Breaking change rules

Breaking events include:

- field removal
- required field set changes
- type changes for existing fields
- semantic repurposing of existing values

Breaking changes require:

1. major version increment
2. changelog entry
3. migration guidance
4. compatibility matrix update
