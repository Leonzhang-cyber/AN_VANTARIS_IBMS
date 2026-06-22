/**
 * S02 LINK — transport retry/backoff only.
 */

export interface LinkRetryDecision {
  readonly shouldRetry: boolean;
  readonly backoffMs: number;
}

export function evaluateLinkRetry(
  attempts: number,
  maxAttempts: number,
  backoffMs: readonly number[],
  deliverySucceeded: boolean,
): LinkRetryDecision {
  if (deliverySucceeded) {
    return { shouldRetry: false, backoffMs: 0 };
  }

  const shouldRetry = attempts < maxAttempts;
  const index = Math.min(Math.max(attempts - 1, 0), backoffMs.length - 1);
  return {
    shouldRetry,
    backoffMs: shouldRetry ? (backoffMs[index] ?? 0) : 0,
  };
}
