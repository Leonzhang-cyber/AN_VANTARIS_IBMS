# LINK Reliability Engineer Guide v1

## 1. What reliability contracts cover

These contracts define delivery attempt tracking, retry policy, DLQ representation, replay request/result semantics, and partition-level reliability state.

## 2. Delivery attempt lifecycle

- Create delivery attempt for envelope and target endpoint.
- Evaluate downstream outcome and retryability.
- Reschedule or finalize to DLQ according to policy and attempt budget.

## 3. Retry policy usage

`link-retry-policy-v1` defines attempt budget, backoff strategy, jitter behavior, and retryable/non-retryable classification sets.

## 4. DLQ item structure

`link-dlq-item-v1` stores failure context, references to original envelope/event, payload snapshot, trace context, idempotency key, and retention metadata.

## 5. Replay request/result usage

- `link-replay-request-v1` supports replay by DLQ item IDs or envelope IDs, including `dryRun` and mode selection.
- `link-replay-result-v1` reports totals and per-item replay/skip/failure outcomes.

## 6. Partition state monitoring

`link-partition-state-v1` provides queue depth, in-flight count, DLQ count, last delivery/ack/error times, and health status by partition.

## 7. Test scenarios

- Retryable failure path schedules retry.
- Non-retryable or exhausted attempts move to DLQ.
- Dry-run replay produces no redelivery side effects.
- Duplicate replay requests preserve idempotent behavior.
- Partition counters reflect movement between queue/in-flight/DLQ.

## 8. DB boundary note

Code owns DB access and persistence orchestration. LINK runtime owns queue/log/DLQ execution state. EDGE/LINK must not direct-write UFMS DB.
