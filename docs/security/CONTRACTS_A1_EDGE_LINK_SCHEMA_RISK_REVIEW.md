# CONTRACTS A1 Edge Link Schema Risk Review

## 1) Schema mistaken as runtime

- description: Teams may treat schema publication as runtime implementation completion.
- impact: Premature runtime migration and unsupported deployment assumptions.
- control: Docs explicitly mark baseline contracts as non-runtime and non-GA.
- current status: Controlled.

## 2) Edge implementation diverges from schema

- description: Future EDGE runtime may emit payloads not aligned to normalized object schema.
- impact: Downstream parsing failures and data inconsistency.
- control: Contract-first enforcement and schema validation gates in EDGE tasks.
- current status: Open until EDGE runtime task.

## 3) Link implementation diverges from schema

- description: Future LINK runtime may alter envelope/ack/retry semantics ad hoc.
- impact: Delivery behavior drift and integration instability.
- control: LINK must use these A1 schema baselines; breaking changes require version bump.
- current status: Open until LINK runtime task.

## 4) Missing idempotency causes duplicate processing

- description: Runtime implementations may ignore idempotency key usage.
- impact: Duplicate message processing and side effects.
- control: Envelope schema requires `idempotencyKey`; governance requires duplicate handling.
- current status: Partially controlled by contracts.

## 5) ACK semantics misunderstood

- description: Consumers may mis-handle ACK types and statuses.
- impact: Message loss, false delivery success, or reprocessing loops.
- control: `link-ack` schema defines explicit ack types and detail fields.
- current status: Controlled at contract layer.

## 6) Retry/DLQ policy ignored

- description: Retry rules may be bypassed by runtime-specific behavior.
- impact: Unbounded retries or dropped failed messages.
- control: Retry policy and DLQ schemas are baseline-required artifacts.
- current status: Controlled at contract layer; runtime enforcement pending.

## 7) Route policy leaks endpoint secrets

- description: Route policy examples/configs could accidentally include secrets.
- impact: Credential exposure and security risk.
- control: Route policy uses endpoint references only; no secret material in contracts.
- current status: Controlled.

## 8) Examples contain real customer data

- description: Example payloads may leak real tenant/site/device data.
- impact: Data privacy and compliance risk.
- control: Use demo tenant/project/site and synthetic identifiers only.
- current status: Controlled.

## 9) Payload hash/signature fields underused

- description: Security fields may be present but ignored in runtime validation.
- impact: Integrity and authenticity checks become ineffective.
- control: Envelope schema includes hash/signature metadata; runtime tasks must enforce verification policy.
- current status: Partially controlled by schema.

## 10) UFMS boundary bypassed

- description: Edge/Link contracts may accidentally introduce UFMS runtime coupling.
- impact: Boundary guard violation and cross-system contamination.
- control: UFMS references restricted to adapter/boundary contract context only.
- current status: Controlled.

## 11) Contract version drift

- description: Schema changes may happen without consistent manifest/version policy updates.
- impact: Consumer incompatibility and audit trace break.
- control: Versioning policy + manifest updates required for schema changes.
- current status: Controlled at governance level.
