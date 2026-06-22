import type { OpcUaReadOnlyPolicy, OpcUaRetryBackoff, OpcUaRetryDecision } from './opcua-readonly-types.js';

export function calculateOpcUaRetryBackoff(attempt: number, policy: OpcUaReadOnlyPolicy): OpcUaRetryBackoff {
  const raw = policy.backoffBaseMs * policy.backoffMultiplier ** Math.max(0, attempt - 1);
  const delayMs = Math.min(raw, policy.backoffMaxMs);
  return { attempt, delayMs, clamped: raw > policy.backoffMaxMs };
}

export function evaluateOpcUaRetryDecision(
  input: { attempt: number; errorClass?: string },
  policy: OpcUaReadOnlyPolicy,
): OpcUaRetryDecision {
  const attempt = input.attempt;
  const maxAttempts = policy.maxRetryAttempts;

  if (attempt >= maxAttempts) {
    return { shouldRetry: false, attempt, maxAttempts, exhausted: true, reason: 'RETRY_EXHAUSTED' };
  }

  if (typeof input.errorClass === 'string' && policy.nonRetryableErrors.includes(input.errorClass)) {
    return { shouldRetry: false, attempt, maxAttempts, exhausted: false, reason: `NON_RETRYABLE_${input.errorClass}` };
  }

  if (typeof input.errorClass === 'string' && policy.retryableErrors.includes(input.errorClass)) {
    return { shouldRetry: true, attempt, maxAttempts, exhausted: false, reason: `RETRYABLE_${input.errorClass}` };
  }

  return { shouldRetry: false, attempt, maxAttempts, exhausted: false, reason: 'NON_RETRYABLE' };
}
