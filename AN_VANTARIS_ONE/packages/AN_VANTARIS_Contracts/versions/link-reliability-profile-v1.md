# LINK Reliability Profile v1

## 1. Purpose

Standardize LINK reliability contracts for retry scheduling, DLQ handling, and replay operations across EDGE/LINK/Code/DB/QA workflows.

## 2. Delivery attempt lifecycle

1. Delivery is scheduled with `attemptNo=1`.
2. Delivery enters `in_progress` and targets Code delivery endpoint.
3. Delivery transitions to `succeeded` or `failed`.
4. Failed retryable attempts are rescheduled with incremented `attemptNo`.
5. Max-attempt or non-retryable outcomes transition to DLQ movement.

## 3. Retry policy rules

- Retry policy defines attempt budget, backoff behavior, retryable classification, and DLQ movement after exhaustion.
- Policy updates must preserve backward-compatible defaults for in-flight deliveries.

## 4. Retryable vs non-retryable failure classification

- Retryable examples: timeout, transient transport failures, 5xx and rate limits.
- Non-retryable examples: signature invalid, unsupported version, structural validation failures.
- Classification uses status codes and domain error codes together.

## 5. Backoff and jitter recommendations

- Prefer exponential-with-cap for unstable downstream conditions.
- Enable jitter for high-concurrency retry storms.
- Keep upper cap bounded to operational SLO windows.

## 6. DLQ movement rules

- Move to DLQ immediately for non-retryable failures.
- Move to DLQ after `maxAttempts` when `dlqAfterMaxAttempts=true`.
- Preserve original envelope/event references and idempotency key in DLQ item.

## 7. DLQ retention rules

- DLQ item includes explicit `retentionUntil` timestamp.
- Compliance holds may override default retention windows.
- Expiry state transitions should be auditable.

## 8. Replay request modes

- `by_dlq_item_ids`: replay explicitly selected DLQ items.
- `by_envelope_ids`: replay by original envelope IDs.
- `dryRun`: evaluate candidate replay set without redelivery side effects.
- `forceReplay`: allow replay despite previous replay markers when policy permits.

## 9. Idempotency expectations

- Replay and retry must preserve `idempotencyKey` semantics.
- Duplicate replay requests must not create duplicate downstream side effects.

## 10. Trace/correlation behavior

- Trace context is required for delivery attempt, replay request, replay result, and DLQ item contracts.
- Correlation linkage is expected across attempt history, DLQ movement, and replay outcomes.

## 11. Code ack relationship

- LINK delivery attempt outcomes align with Code acknowledgment semantics in `delivery-ack.v1`.
- Retry and DLQ rules interpret `retryable` and rejection details from ack/error responses.

## 12. DB persistence boundary

- Code owns DB access and persistence orchestration.
- LINK runtime owns queue/log/DLQ state transitions and reliability control flow.
- EDGE/LINK must not direct-write UFMS DB.

## 13. Version compatibility

- This profile targets `schemaVersion=v1` reliability contracts.
- Additive optional fields are allowed.
- Breaking behavior requires major contract progression and compatibility documentation.
