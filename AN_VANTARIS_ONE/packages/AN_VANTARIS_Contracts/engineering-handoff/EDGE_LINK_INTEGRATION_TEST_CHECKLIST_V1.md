# EDGE LINK Integration Test Checklist v1

## Contract and protocol checks

- [ ] JSON schema validation checks for wire event, signed envelope, handoff event, and delivery ack.
- [ ] Required header checks for all `x-vantaris-*` mandatory headers.
- [ ] Missing signature checks (`x-vantaris-signature` absent should fail).
- [ ] Invalid signature checks (tampered body/signature mismatch should fail).
- [ ] Expired `x-vantaris-signed-at` / clock skew checks (outside allowed skew should fail).
- [ ] Duplicate `idempotencyKey` checks (must be deterministic and duplicate-safe).
- [ ] Retryable failure checks (`retryable=true`, `retryAfterSeconds` behavior).
- [ ] Partial success ack checks (`partialSuccess`, accepted/rejected counts).
- [ ] Version mismatch checks (`UNSUPPORTED_VERSION` path).
- [ ] Unknown optional field tolerance checks (consumer should tolerate allowed unknown optionals).

## Hygiene and governance checks

- [ ] No real secrets in examples.
- [ ] EDGE must not import LINK runtime.
- [ ] LINK must not import EDGE acquisition runtime.
- [ ] LINK must not direct-write DB.
- [ ] Code owns DB persistence.

## P1C reliability checks

- [ ] retryable failure moves to retry schedule
- [ ] non-retryable failure moves to DLQ
- [ ] max attempts moves to DLQ
- [ ] replay dry-run does not redeliver
- [ ] replay by `dlqItemIds`
- [ ] replay by `envelopeIds`
- [ ] duplicate replay respects idempotency
- [ ] partition state `queueDepth`/`dlqCount` changes are observable

## P2A0 security and audit checks

- [ ] machine identity required
- [ ] missing signature rejected
- [ ] stale signedAt rejected
- [ ] replay idempotency duplicate handled
- [ ] no DB direct write from EDGE/LINK
- [ ] audit event emitted or captured as evidence placeholder
- [ ] no secrets in examples/config
- [ ] zone/conduit boundary respected
- [ ] deployment profile validated
