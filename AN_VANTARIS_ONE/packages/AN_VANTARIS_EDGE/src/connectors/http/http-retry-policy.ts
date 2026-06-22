import type { HttpPollingReadOnlyPolicy, HttpRetryBackoff, HttpRetryDecision } from './http-readonly-types.js';

export function calculateHttpRetryBackoff(
  attempt: number,
  policy: HttpPollingReadOnlyPolicy,
): HttpRetryBackoff {
  const raw = policy.backoffBaseMs * policy.backoffMultiplier ** Math.max(0, attempt - 1);
  const delayMs = Math.min(raw, policy.backoffMaxMs);
  return {
    attempt,
    delayMs,
    clamped: raw > policy.backoffMaxMs,
  };
}

export function evaluateHttpRetryDecision(
  input: {
    attempt: number;
    statusCode?: number;
    errorClass?: string;
    retryAfterSeconds?: number;
  },
  policy: HttpPollingReadOnlyPolicy,
): HttpRetryDecision {
  const attempt = input.attempt;
  const maxAttempts = policy.maxRetryAttempts;

  if (attempt >= maxAttempts) {
    return {
      shouldRetry: false,
      attempt,
      maxAttempts,
      exhausted: true,
      reason: 'RETRY_EXHAUSTED',
    };
  }

  const statusRetryable =
    typeof input.statusCode === 'number' && policy.retryableStatusCodes.includes(input.statusCode);
  const errorRetryable =
    typeof input.errorClass === 'string' && policy.retryableErrorClasses.includes(input.errorClass);

  if (statusRetryable || errorRetryable) {
    return {
      shouldRetry: true,
      attempt,
      maxAttempts,
      exhausted: false,
      reason: statusRetryable ? `RETRYABLE_STATUS_${input.statusCode}` : `RETRYABLE_ERROR_${input.errorClass}`,
    };
  }

  return {
    shouldRetry: false,
    attempt,
    maxAttempts,
    exhausted: false,
    reason: typeof input.statusCode === 'number' ? `NON_RETRYABLE_STATUS_${input.statusCode}` : 'NON_RETRYABLE',
  };
}
