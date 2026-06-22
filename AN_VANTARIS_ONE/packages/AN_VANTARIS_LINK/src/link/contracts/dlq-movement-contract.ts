/**
 * LINK-C5-04 — DLQ movement contract.
 *
 * LINK-owned DLQ movement record for retry-exhausted, rejected, expired,
 * security, schema, policy, replay, and queue failures.
 *
 * This contract does not enable production delivery.
 */

import type {
  LinkDlqCategory,
  LinkDlqReasonCode,
} from './dlq-reason-taxonomy.js';
import {
  getLinkDlqReasonDefinition,
  isLinkDlqReasonOperatorActionRequired,
  isLinkDlqReasonReplayEligible,
  isLinkDlqReasonRetryable,
} from './dlq-reason-taxonomy.js';
import type { LinkDeliveryAttemptContract } from './delivery-attempt-receipt-contract.js';
import type { LinkQueueItemContract } from './queue-item-contract.js';

export interface LinkDlqEvidenceRef {
  readonly evidenceId: string;
  readonly evidenceType:
    | 'queue'
    | 'delivery'
    | 'retry'
    | 'replay'
    | 'security'
    | 'schema'
    | 'policy'
    | 'operator'
    | 'unknown';
  readonly sourcePath?: string;
  readonly hash?: string;
}

export interface LinkDlqMovementContract {
  readonly dlqId: string;
  readonly queueId: string;
  readonly deliveryId?: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly targetId?: string;
  readonly reasonCode: LinkDlqReasonCode;
  readonly category: LinkDlqCategory;
  readonly retryable: boolean;
  readonly replayEligible: boolean;
  readonly operatorActionRequired: boolean;
  readonly movedAt: string;
  readonly attempts: number;
  readonly maxAttempts: number;
  readonly reliabilityKey?: string;
  readonly duplicateRiskKey?: string;
  readonly evidenceRefs: readonly LinkDlqEvidenceRef[];
  readonly productionDeliveryAllowed: false;
}

export interface LinkDlqMovementValidationResult {
  readonly valid: boolean;
  readonly reasons: readonly string[];
}

export function createLinkDlqId(input: {
  readonly queueId: string;
  readonly reasonCode: LinkDlqReasonCode;
}): string {
  return `link-dlq-${input.queueId}-${input.reasonCode}`;
}

export function createLinkDlqMovementFromQueue(input: {
  readonly item: LinkQueueItemContract;
  readonly reasonCode: LinkDlqReasonCode;
  readonly movedAt?: string;
  readonly evidenceRefs?: readonly LinkDlqEvidenceRef[];
}): LinkDlqMovementContract {
  const reason = getLinkDlqReasonDefinition(input.reasonCode);

  return {
    dlqId: createLinkDlqId({
      queueId: input.item.queueId,
      reasonCode: input.reasonCode,
    }),
    queueId: input.item.queueId,
    eventId: input.item.eventId,
    traceId: input.item.traceId,
    gatewayId: input.item.gatewayId,
    streamId: input.item.partitionIdentity.recordType,
    sequenceNumber: 0,
    reasonCode: input.reasonCode,
    category: reason.category,
    retryable: isLinkDlqReasonRetryable(input.reasonCode),
    replayEligible: isLinkDlqReasonReplayEligible(input.reasonCode),
    operatorActionRequired: isLinkDlqReasonOperatorActionRequired(input.reasonCode),
    movedAt: input.movedAt ?? new Date().toISOString(),
    attempts: input.item.attempts,
    maxAttempts: input.item.maxAttempts,
    evidenceRefs: input.evidenceRefs ?? [],
    productionDeliveryAllowed: false,
  };
}

export function createLinkDlqMovementFromDelivery(input: {
  readonly attempt: LinkDeliveryAttemptContract;
  readonly reasonCode: LinkDlqReasonCode;
  readonly movedAt?: string;
  readonly evidenceRefs?: readonly LinkDlqEvidenceRef[];
}): LinkDlqMovementContract {
  const reason = getLinkDlqReasonDefinition(input.reasonCode);

  return {
    dlqId: createLinkDlqId({
      queueId: input.attempt.queueId,
      reasonCode: input.reasonCode,
    }),
    queueId: input.attempt.queueId,
    deliveryId: input.attempt.deliveryId,
    eventId: input.attempt.eventId,
    traceId: input.attempt.traceId,
    gatewayId: input.attempt.gatewayId,
    streamId: input.attempt.streamId,
    sequenceNumber: input.attempt.sequenceNumber,
    targetId: input.attempt.targetId,
    reasonCode: input.reasonCode,
    category: reason.category,
    retryable: isLinkDlqReasonRetryable(input.reasonCode),
    replayEligible: isLinkDlqReasonReplayEligible(input.reasonCode),
    operatorActionRequired: isLinkDlqReasonOperatorActionRequired(input.reasonCode),
    movedAt: input.movedAt ?? new Date().toISOString(),
    attempts: input.attempt.attemptNumber,
    maxAttempts: input.attempt.maxAttempts,
    reliabilityKey: input.attempt.reliabilityKey,
    duplicateRiskKey: input.attempt.duplicateRiskKey,
    evidenceRefs: input.evidenceRefs ?? [],
    productionDeliveryAllowed: false,
  };
}

export function validateLinkDlqMovementContract(
  movement: LinkDlqMovementContract,
): LinkDlqMovementValidationResult {
  const reasons: string[] = [];

  if (!movement.dlqId.trim()) reasons.push('dlqId is required');
  if (!movement.queueId.trim()) reasons.push('queueId is required');
  if (!movement.eventId.trim()) reasons.push('eventId is required');
  if (!movement.traceId.trim()) reasons.push('traceId is required');
  if (!movement.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!movement.streamId.trim()) reasons.push('streamId is required');
  if (!Number.isInteger(movement.sequenceNumber) || movement.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }
  if (!movement.movedAt.trim()) reasons.push('movedAt is required');
  if (!Number.isInteger(movement.attempts) || movement.attempts < 0) {
    reasons.push('attempts must not be negative');
  }
  if (!Number.isInteger(movement.maxAttempts) || movement.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }
  if (movement.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }

  return {
    valid: reasons.length === 0,
    reasons,
  };
}
