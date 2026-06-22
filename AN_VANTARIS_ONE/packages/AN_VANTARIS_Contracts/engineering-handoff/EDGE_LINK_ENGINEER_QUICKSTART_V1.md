# EDGE LINK Engineer Quickstart v1

## 1) What to read first

1. `AN_VANTARIS_Contracts/README.md`
2. `AN_VANTARIS_Contracts/GOVERNANCE.md`
3. `AN_VANTARIS_Contracts/openapi/edge-to-link-handoff.openapi.yaml`
4. `AN_VANTARIS_Contracts/schemas/*` (wire event, identity, signature, handoff envelope/event, delivery ack)
5. `AN_VANTARIS_Contracts/versions/edge-link-protocol-profile-v1.md`
6. `AN_VANTARIS_Contracts/versions/edge-link-compatibility-matrix-v1.md`

## 2) EDGE to LINK handoff flow

1. EDGE builds `wire-event-v1`.
2. EDGE wraps event inside `signed-handoff-envelope-v1`.
3. EDGE submits `edge-handoff-event-v1` to `POST /edge/v1/handoff`.
4. LINK validates headers/signature/version/idempotency.
5. LINK returns `delivery-ack.v1` or `error-response.v1`.

## 3) Required headers

- `x-vantaris-machine-id`
- `x-vantaris-signature`
- `x-vantaris-signature-algorithm`
- `x-vantaris-signed-at`
- `x-vantaris-trace-id`
- `x-vantaris-idempotency-key`
- `x-vantaris-protocol-version`

## 4) Example request body

Use `AN_VANTARIS_Contracts/dto-examples/edge-handoff-event.example.json` as baseline fixture.

## 5) Signature verification summary

- Verify required signature headers are present.
- Recompute signature over canonical signed payload.
- Validate algorithm and signed-at freshness window.
- Reject mismatches with `INVALID_SIGNATURE`.

## 6) Idempotency and duplicate handling

- Use `idempotencyKey` to avoid duplicate side effects.
- Duplicate handoffs should return deterministic ack behavior.
- Preserve original trace and correlation metadata across retries.

## 7) Retry and DLQ expectations

- Retryable failures should signal `retryable=true` and `retryAfterSeconds`.
- Repeated transport failures escalate to DLQ behavior in LINK runtime.
- Non-retryable validation/signature failures should fail fast.

## 8) Version compatibility

- EDGE protocol v1 <-> LINK protocol v1 is supported baseline.
- Version mismatches return `UNSUPPORTED_VERSION`.
- See compatibility matrix for supported/deprecated/unsupported behavior.

## 9) Test checklist

- [ ] Validate required headers and schema payloads
- [ ] Verify signature pass/fail behavior
- [ ] Verify idempotency duplicate handling
- [ ] Verify retryable vs non-retryable errors
- [ ] Verify protocol version mismatch handling
- [ ] Verify ack payload compatibility with Code/LINK consumers

## 10) Files included in this contract pack

- `schemas/wire-event-v1.schema.json`
- `schemas/machine-identity-ref-v1.schema.json`
- `schemas/signature-headers-v1.schema.json`
- `schemas/signed-handoff-envelope-v1.schema.json`
- `schemas/edge-handoff-event-v1.schema.json`
- `schemas/delivery-ack.v1.schema.json` (compatible extension)
- `openapi/edge-to-link-handoff.openapi.yaml`
- `dto-examples/*edge*`, `dto-examples/*wire*`, `dto-examples/*ack*`
