# EDGE LINK Handoff Pack Index v1

## 1. Purpose

Provide a single engineer-facing index for EDGE/LINK/Code/DB integration using the released P0 contract authority artifacts.

## 2. Who should use this pack

- EDGE engineer
- LINK engineer
- Code/API engineer
- DB engineer
- QA/test engineer

## 3. Reading order

1. `AN_VANTARIS_Contracts/engineering-handoff/ENGINEER_README.md`
2. `AN_VANTARIS_Contracts/engineering-handoff/EDGE_LINK_ENGINEER_QUICKSTART_V1.md`
3. `AN_VANTARIS_Contracts/versions/edge-link-protocol-profile-v1.md`
4. `AN_VANTARIS_Contracts/versions/edge-link-compatibility-matrix-v1.md`
5. `AN_VANTARIS_Contracts/openapi/edge-to-link-handoff.openapi.yaml`
6. `AN_VANTARIS_Contracts/schemas/`
7. `AN_VANTARIS_Contracts/dto-examples/`

## 4. Contract authority rule

- `AN_VANTARIS_Contracts` is the authority.
- Runtime source is not contract authority.

## 5. File map

| Contract area | File path | Owner | Consumer | Status |
|---------------|-----------|-------|----------|--------|
| Wire event | `AN_VANTARIS_Contracts/schemas/wire-event-v1.schema.json` | Contracts authority | EDGE, LINK, Code | Stable (P0) |
| Machine identity | `AN_VANTARIS_Contracts/schemas/machine-identity-ref-v1.schema.json` | Contracts authority | EDGE, LINK | Stable (P0) |
| Signature headers | `AN_VANTARIS_Contracts/schemas/signature-headers-v1.schema.json` | Contracts authority | EDGE, LINK | Stable (P0) |
| Signed envelope | `AN_VANTARIS_Contracts/schemas/signed-handoff-envelope-v1.schema.json` | Contracts authority | EDGE, LINK | Stable (P0) |
| EDGE handoff event | `AN_VANTARIS_Contracts/schemas/edge-handoff-event-v1.schema.json` | Contracts authority | EDGE, LINK | Stable (P0) |
| Delivery ack | `AN_VANTARIS_Contracts/schemas/delivery-ack.v1.schema.json` | Contracts authority | LINK, Code | Stable (P0 extension) |
| EDGE->LINK API | `AN_VANTARIS_Contracts/openapi/edge-to-link-handoff.openapi.yaml` | Contracts authority | EDGE, LINK, QA | Stable (P0) |
| Protocol profile | `AN_VANTARIS_Contracts/versions/edge-link-protocol-profile-v1.md` | Contracts authority | EDGE, LINK, QA | Stable (P0) |
| Compatibility matrix | `AN_VANTARIS_Contracts/versions/edge-link-compatibility-matrix-v1.md` | Contracts authority | EDGE, LINK, Code | Stable (P0) |
| DTO examples | `AN_VANTARIS_Contracts/dto-examples/*.example.json` | Contracts authority | Engineers, QA | Stable (P0) |

## 6. What is stable now

- P0 EDGE/LINK handoff
- signature headers
- machine identity
- wire event
- signed envelope
- delivery ack extension
- compatibility matrix

## 7. What is pending

- P1B DB mapping YAML
- P1C retry/DLQ/replay detailed schemas

## 8. P1 canonical schema baseline

- Canonical schemas are now available under `AN_VANTARIS_Contracts/schemas/` (`*-v1.schema.json` canonical objects plus `common-*` shared definitions).
- Canonical examples are available under `AN_VANTARIS_Contracts/dto-examples/canonical/`.
- Canonical schemas define object identity and field meaning used by wire-event payload mapping and downstream DB mapping.
- DB mapping details are still extended in P1B YAML deliverables.

## 10. P1C reliability contracts

- Schemas: `AN_VANTARIS_Contracts/schemas/link-*-v1.schema.json`
- Examples: `AN_VANTARIS_Contracts/dto-examples/reliability/*.example.json`
- OpenAPI: `AN_VANTARIS_Contracts/openapi/link-reliability.openapi.yaml`
- Reliability profile: `AN_VANTARIS_Contracts/versions/link-reliability-profile-v1.md`

## 11. Engineer checklist

- [ ] Confirm contract version and protocol profile
- [ ] Validate requests against authority schemas
- [ ] Include required signature/idempotency headers
- [ ] Verify version compatibility matrix before rollout
- [ ] Use DTO examples with fake values only
- [ ] Do not treat runtime source as contract authority
