/**
 * LINK-C5-02 — Retry decision / backoff / jitter contract.
 *
 * LINK-owned retry decision contract for delivery retry and replay-aware retry.
 *
 * This contract does not enable production delivery.
 */

import type {
  LinkNonRetryableReasonCode,
  LinkRetryPolicyContract,
  LinkRetryReasonCode,
} from './retry-policy-contract.js';
import {
  calculateRetryBackoffMs,
  hasRetryBudget,
  isNonRetryableReason,
  isRetryableReason,
} from './retry-policy-contract.js';

export interface LinkRetryBudgetUsage {
  readonly globalUsed: number;
  readonly targetUsed: number;
  readonly gatewayUsed: number;
  readonly streamUsed: number;
  readonly replayUsed: number;
}

export interface LinkRetryDecisionInput {
  readonly policy: LinkRetryPolicyContract;
  readonly reasonCode: LinkRetryReasonCode | LinkNonRetryableReasonCode;
  readonly attemptNumber: number;
  readonly nowMs: number;
  readonly deterministicJitterSeed?: number;
  readonly replay: boolean;
  readonly budgetUsage: LinkRetryBudgetUsage;
}

export interface LinkRetryDecisionContract {
  readonly shouldRetry: boolean;
  readonly retryable: boolean;
  readonly attemptNumber: number;
  readonly maxAttempts: number;
  readonly nextRetryAt: string | null;
  readonly backoffMs: number;
  readonly jitterMs: number;
  readonly reasonCode: LinkRetryReasonCode | LinkNonRetryableReasonCode;
  readonly retryBudgetRemaining: number;
  readonly stormProtected: boolean;
  readonly dlqRequired: boolean;
  readonly productionDeliveryAllowed: false;
}

export function calculateRetryBudgetRemaining(input: {
  readonly policy: LinkRetryPolicyContract;
  readonly usage: LinkRetryBudgetUsage;
  readonly replay: boolean;
}): number {
  const remaining = [
    input.policy.budget.globalRetryBudget - input.usage.globalUsed,
    input.policy.budget.targetRetryBudget - input.usage.targetUsed,
    input.policy.budget.gatewayRetryBudget - input.usage.gatewayUsed,
    input.policy.budget.streamRetryBudget - input.usage.streamUsed,
    input.replay
      ? input.policy.budget.replayRetryBudget - input.usage.replayUsed
      : Number.MAX_SAFE_INTEGER,
  ];

  return Math.max(0, Math.min(...remaining));
}

export function createLinkRetryDecision(
  input: LinkRetryDecisionInput,
): LinkRetryDecisionContract {
  const retryable = isRetryableReason(input.policy, input.reasonCode);
  const nonRetryable = isNonRetryableReason(input.policy, input.reasonCode);
  const maxAttemptsExceeded = input.attemptNumber >= input.policy.maxAttempts;
  const budgetAllowed = hasRetryBudget({
    policy: input.policy,
    globalUsed: input.budgetUsage.globalUsed,
    targetUsed: input.budgetUsage.targetUsed,
    gatewayUsed: input.budgetUsage.gatewayUsed,
    streamUsed: input.budgetUsage.streamUsed,
    replayUsed: input.budgetUsage.replayUsed,
    replay: input.replay,
  });

  const backoffMs = retryable
    ? calculateRetryBackoffMs({
        policy: input.policy,
        attemptNumber: input.attemptNumber,
        deterministicJitterSeed: input.deterministicJitterSeed,
      })
    : 0;

  const shouldRetry =
    retryable === true &&
    nonRetryable === false &&
    maxAttemptsExceeded === false &&
    budgetAllowed === true;

  const retryBudgetRemaining = calculateRetryBudgetRemaining({
    policy: input.policy,
    usage: input.budgetUsage,
    replay: input.replay,
  });

  const nextRetryAt =
    shouldRetry === true ? new Date(input.nowMs + backoffMs).toISOString() : null;

  const stormProtected =
    input.policy.stormProtectionEnabled === true &&
    (budgetAllowed === false || retryBudgetRemaining === 0);

  return {
    shouldRetry,
    retryable,
    attemptNumber: input.attemptNumber,
    maxAttempts: input.policy.maxAttempts,
    nextRetryAt,
    backoffMs,
    jitterMs: input.policy.backoff.jitterMs,
    reasonCode: input.reasonCode,
    retryBudgetRemaining,
    stormProtected,
    dlqRequired: shouldRetry === false && retryable === true,
    productionDeliveryAllowed: false,
  };
}

export function validateLinkRetryDecisionContract(
  decision: LinkRetryDecisionContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!Number.isInteger(decision.attemptNumber) || decision.attemptNumber < 1) {
    reasons.push('attemptNumber must be greater than zero');
  }

  if (!Number.isInteger(decision.maxAttempts) || decision.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }

  if (!Number.isInteger(decision.backoffMs) || decision.backoffMs < 0) {
    reasons.push('backoffMs must not be negative');
  }

  if (!Number.isInteger(decision.jitterMs) || decision.jitterMs < 0) {
    reasons.push('jitterMs must not be negative');
  }

  if (!Number.isInteger(decision.retryBudgetRemaining) || decision.retryBudgetRemaining < 0) {
    reasons.push('retryBudgetRemaining must not be negative');
  }

  if (decision.shouldRetry === true && decision.nextRetryAt === null) {
    reasons.push('nextRetryAt is required when shouldRetry is true');
  }

  if (decision.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }

  return reasons;
}
