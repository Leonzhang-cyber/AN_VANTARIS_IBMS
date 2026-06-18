# CONTRACTS A1 Edge Link Schema Rules

- Edge normalized object must not include DB-only id as canonical identity.
- Link envelope must include messageId, traceId, idempotencyKey.
- ACK before delete principle applies for Link delivery lifecycle.
- Retry and DLQ must be contract-defined.
- Route policy must not embed real secrets.
- Examples must not include real customer data.
- Runtime modules must not invent private envelope fields.
- Breaking schema change requires version bump.
- UFMS only through adapter/boundary contract.
