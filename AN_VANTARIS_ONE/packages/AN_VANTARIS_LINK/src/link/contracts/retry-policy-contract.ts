/**
 * LINK-C5-01 — Retry policy contract.
 *
 * LINK-owned retry policy model for delivery retry, replay-aware retry,
 * backoff, jitter, and retry storm protection.
 *
 * This contract does not enable production delivery.
 */

export type LinkRetryReasonCode =
  | 'LINK_DELIVERY_TIMEOUT'
  | 'LINK_DELIVERY_TARGET_RETRYABLE'
  | 'LINK_DELIVERY_429_RATE_LIMIT'
  | 'LINK_DELIVERY_5XX_RETRYABLE'
  | 'LINK_NETWORK_ERROR'
  | 'LINK_REPLAY_REQUESTED'
  | 'LINK_EDGE_RECONNECT_REPLAY'
  | 'LINK_RETRY_BUDGET_EXHAUSTED'
  | 'LINK_RETRY_NON_RETRYABLE'
  | 'LINK_RETRY_MAX_ATTEMPTS_EXCEEDED';

export type LinkNonRetryableReasonCode =
  | 'LINK_SECURITY_SIGNATURE_INVALID'
  | 'LINK_SCHEMA_INVALID'
  | 'LINK_POLICY_BLOCKED'
  | 'LINK_DELIVERY_TARGET_REJECTED'
  | 'LINK_DELIVERY_TARGET_UNAPPROVED'
  | 'LINK_DELIVERY_PRODUCTION_BLOCKED'
  | 'LINK_WRITEBACK_PROHIBITED'
  | 'LINK_DIRECT_DB_PROHIBITED'
  | 'LINK_QUEUE_EXPIRED'
  | 'LINK_DUPLICATE_FINAL';

export interface LinkRetryBudgetPolicy {
  readonly globalRetryBudget: number;
  readonly targetRetryBudget: number;
  readonly gatewayRetryBudget: number;
  readonly streamRetryBudget: number;
  readonly replayRetryBudget: number;
  readonly retryWindowMs: number;
}

export interface LinkRetryBackoffPolicy {
  readonly initialDelayMs: number;
  readonly maxDelayMs: number;
  readonly jitterMs: number;
  readonly multiplier: number;
}

export interface LinkRetryPolicyContract {
  readonly policyId: string;
  readonly maxAttempts: number;
  readonly backoff: LinkRetryBackoffPolicy;
  readonly budget: LinkRetryBudgetPolicy;
  readonly retryableReasonCodes: readonly LinkRetryReasonCode[];
  readonly nonRetryableReasonCodes: readonly LinkNonRetryableReasonCode[];
  readonly stormProtectionEnabled: boolean;
  readonly productionDeliveryAllowed: false;
}

export interface LinkRetryPolicyValidationResult {
  readonly valid: boolean;
  readonly reasons: readonly string[];
}

export function createDefaultLinkRetryPolicy(
  policyId = 'link-default-retry-policy',
): LinkRetryPolicyContract {
  return {
    policyId,
    maxAttempts: 3,
    backoff: {
      initialDelayMs: 500,
      maxDelayMs: 30000,
      jitterMs: 250,
      multiplier: 2,
    },
    budget: {
      globalRetryBudget: 10000,
      targetRetryBudget: 2000,
      gatewayRetryBudget: 1000,
      streamRetryBudget: 500,
      replayRetryBudget: 500,
      retryWindowMs: 60000,
    },
    retryableReasonCodes: [
      'LINK_DELIVERY_TIMEOUT',
      'LINK_DELIVERY_TARGET_RETRYABLE',
      'LINK_DELIVERY_429_RATE_LIMIT',
      'LINK_DELIVERY_5XX_RETRYABLE',
      'LINK_NETWORK_ERROR',
      'LINK_REPLAY_REQUESTED',
      'LINK_EDGE_RECONNECT_REPLAY',
    ],
    nonRetryableReasonCodes: [
      'LINK_SECURITY_SIGNATURE_INVALID',
      'LINK_SCHEMA_INVALID',
      'LINK_POLICY_BLOCKED',
      'LINK_DELIVERY_TARGET_REJECTED',
      'LINK_DELIVERY_TARGET_UNAPPROVED',
      'LINK_DELIVERY_PRODUCTION_BLOCKED',
      'LINK_WRITEBACK_PROHIBITED',
      'LINK_DIRECT_DB_PROHIBITED',
      'LINK_QUEUE_EXPIRED',
      'LINK_DUPLICATE_FINAL',
    ],
    stormProtectionEnabled: true,
    productionDeliveryAllowed: false,
  };
}

export function isRetryableReason(
  policy: LinkRetryPolicyContract,
  reasonCode: LinkRetryReasonCode | LinkNonRetryableReasonCode,
): boolean {
  return policy.retryableReasonCodes.includes(reasonCode as LinkRetryReasonCode);
}

export function isNonRetryableReason(
  policy: LinkRetryPolicyContract,
  reasonCode: LinkRetryReasonCode | LinkNonRetryableReasonCode,
): boolean {
  return policy.nonRetryableReasonCodes.includes(reasonCode as LinkNonRetryableReasonCode);
}

export function calculateRetryBackoffMs(input: {
  readonly policy: LinkRetryPolicyContract;
  readonly attemptNumber: number;
  readonly deterministicJitterSeed?: number;
}): number {
  const attemptIndex = Math.max(input.attemptNumber - 1, 0);
  const exponential = input.policy.backoff.initialDelayMs * input.policy.backoff.multiplier ** attemptIndex;
  const capped = Math.min(exponential, input.policy.backoff.maxDelayMs);
  const jitterSeed = input.deterministicJitterSeed ?? 0;
  const jitter =
    input.policy.backoff.jitterMs > 0
      ? jitterSeed % (input.policy.backoff.jitterMs + 1)
      : 0;

  return capped + jitter;
}

export function hasRetryBudget(input: {
  readonly policy: LinkRetryPolicyContract;
  readonly globalUsed: number;
  readonly targetUsed: number;
  readonly gatewayUsed: number;
  readonly streamUsed: number;
  readonly replayUsed: number;
  readonly replay: boolean;
}): boolean {
  if (input.globalUsed >= input.policy.budget.globalRetryBudget) return false;
  if (input.targetUsed >= input.policy.budget.targetRetryBudget) return false;
  if (input.gatewayUsed >= input.policy.budget.gatewayRetryBudget) return false;
  if (input.streamUsed >= input.policy.budget.streamRetryBudget) return false;
  if (input.replay && input.replayUsed >= input.policy.budget.replayRetryBudget) return false;

  return true;
}

export function validateLinkRetryPolicyContract(
  policy: LinkRetryPolicyContract,
): LinkRetryPolicyValidationResult {
  const reasons: string[] = [];

  if (!policy.policyId.trim()) {
    reasons.push('policyId is required');
  }

  if (!Number.isInteger(policy.maxAttempts) || policy.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }

  if (!Number.isInteger(policy.backoff.initialDelayMs) || policy.backoff.initialDelayMs < 0) {
    reasons.push('initialDelayMs must not be negative');
  }

  if (!Number.isInteger(policy.backoff.maxDelayMs) || policy.backoff.maxDelayMs < 1) {
    reasons.push('maxDelayMs must be greater than zero');
  }

  if (policy.backoff.maxDelayMs < policy.backoff.initialDelayMs) {
    reasons.push('maxDelayMs must be greater than or equal to initialDelayMs');
  }

  if (!Number.isInteger(policy.backoff.jitterMs) || policy.backoff.jitterMs < 0) {
    reasons.push('jitterMs must not be negative');
  }

  if (policy.backoff.multiplier < 1) {
    reasons.push('multiplier must be greater than or equal to one');
  }

  if (policy.budget.globalRetryBudget < 1) reasons.push('globalRetryBudget must be greater than zero');
  if (policy.budget.targetRetryBudget < 1) reasons.push('targetRetryBudget must be greater than zero');
  if (policy.budget.gatewayRetryBudget < 1) reasons.push('gatewayRetryBudget must be greater than zero');
  if (policy.budget.streamRetryBudget < 1) reasons.push('streamRetryBudget must be greater than zero');
  if (policy.budget.replayRetryBudget < 1) reasons.push('replayRetryBudget must be greater than zero');
  if (policy.budget.retryWindowMs < 1) reasons.push('retryWindowMs must be greater than zero');

  if (policy.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }

  return {
    valid: reasons.length === 0,
    reasons,
  };
}
