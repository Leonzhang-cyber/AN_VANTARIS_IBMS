/**
 * LINK-C4-03 — Delivery attempt and receipt contract.
 *
 * LINK-owned delivery attempt, receipt, and ACK mapping contract.
 *
 * This contract does not enable production delivery.
 */

import type {
  LinkDeliveryIdempotencyContract,
  LinkDeliveryHeaders,
} from './delivery-idempotency-contract.js';
import type { LinkDeliveryTargetContract } from './delivery-target-contract.js';
import type { LinkQueueItemContract } from './queue-item-contract.js';

export type LinkDeliveryAttemptStatus =
  | 'DELIVERY_BLOCKED'
  | 'DELIVERY_DRY_RUN_ACCEPTED'
  | 'DELIVERY_ATTEMPTED'
  | 'DELIVERY_ACCEPTED'
  | 'DELIVERY_RETRYABLE'
  | 'DELIVERY_REJECTED'
  | 'DELIVERY_DLQ';

export type LinkDeliveryReceiptReason =
  | 'PRODUCTION_DELIVERY_BLOCKED'
  | 'DRY_RUN_ACCEPTED'
  | 'TARGET_ACCEPTED'
  | 'TARGET_RETRYABLE'
  | 'TARGET_REJECTED'
  | 'TARGET_TIMEOUT'
  | 'TARGET_UNAPPROVED'
  | 'IDEMPOTENCY_INVALID'
  | 'QUEUE_ITEM_INVALID'
  | 'DLQ_ROUTED';

export interface LinkDeliveryAttemptContract {
  readonly deliveryId: string;
  readonly queueId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly targetId: string;
  readonly attemptNumber: number;
  readonly maxAttempts: number;
  readonly startedAt: string;
  readonly completedAt?: string;
  readonly status: LinkDeliveryAttemptStatus;
  readonly httpStatus?: number;
  readonly retryable: boolean;
  readonly reasonCode: LinkDeliveryReceiptReason;
  readonly idempotencyKey: string;
  readonly reliabilityKey: string;
  readonly duplicateRiskKey: string;
  readonly headers: LinkDeliveryHeaders;
}

export interface LinkDeliveryReceiptContract {
  readonly receiptId: string;
  readonly deliveryId: string;
  readonly queueId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly targetId: string;
  readonly status: LinkDeliveryAttemptStatus;
  readonly reasonCode: LinkDeliveryReceiptReason;
  readonly accepted: boolean;
  readonly retryable: boolean;
  readonly dryRun: boolean;
  readonly productionDelivery: false;
  readonly receivedAt: string;
  readonly completedAt: string;
  readonly idempotencyKey: string;
  readonly reliabilityKey: string;
}

export function createLinkDeliveryId(input: {
  readonly queueId: string;
  readonly targetId: string;
  readonly attemptNumber: number;
}): string {
  return `link-delivery-${input.queueId}-${input.targetId}-${input.attemptNumber}`;
}

export function createBlockedDeliveryAttempt(input: {
  readonly item: LinkQueueItemContract;
  readonly target: LinkDeliveryTargetContract;
  readonly idempotency: LinkDeliveryIdempotencyContract;
  readonly headers: LinkDeliveryHeaders;
  readonly attemptNumber?: number;
  readonly startedAt?: string;
}): LinkDeliveryAttemptContract {
  const attemptNumber = input.attemptNumber ?? 1;
  const deliveryId = createLinkDeliveryId({
    queueId: input.item.queueId,
    targetId: input.target.targetId,
    attemptNumber,
  });

  return {
    deliveryId,
    queueId: input.item.queueId,
    eventId: input.item.eventId,
    traceId: input.item.traceId,
    gatewayId: input.item.gatewayId,
    streamId: input.idempotency.streamId,
    sequenceNumber: input.idempotency.sequenceNumber,
    targetId: input.target.targetId,
    attemptNumber,
    maxAttempts: input.item.maxAttempts,
    startedAt: input.startedAt ?? new Date().toISOString(),
    status: 'DELIVERY_BLOCKED',
    retryable: false,
    reasonCode: 'PRODUCTION_DELIVERY_BLOCKED',
    idempotencyKey: input.idempotency.idempotencyKey,
    reliabilityKey: input.idempotency.reliabilityKey,
    duplicateRiskKey: input.idempotency.duplicateRiskKey,
    headers: input.headers,
  };
}

export function createDryRunDeliveryAttempt(input: {
  readonly item: LinkQueueItemContract;
  readonly target: LinkDeliveryTargetContract;
  readonly idempotency: LinkDeliveryIdempotencyContract;
  readonly headers: LinkDeliveryHeaders;
  readonly attemptNumber?: number;
  readonly startedAt?: string;
}): LinkDeliveryAttemptContract {
  const attemptNumber = input.attemptNumber ?? 1;
  const deliveryId = createLinkDeliveryId({
    queueId: input.item.queueId,
    targetId: input.target.targetId,
    attemptNumber,
  });

  return {
    deliveryId,
    queueId: input.item.queueId,
    eventId: input.item.eventId,
    traceId: input.item.traceId,
    gatewayId: input.item.gatewayId,
    streamId: input.idempotency.streamId,
    sequenceNumber: input.idempotency.sequenceNumber,
    targetId: input.target.targetId,
    attemptNumber,
    maxAttempts: input.item.maxAttempts,
    startedAt: input.startedAt ?? new Date().toISOString(),
    status: 'DELIVERY_DRY_RUN_ACCEPTED',
    retryable: false,
    reasonCode: 'DRY_RUN_ACCEPTED',
    idempotencyKey: input.idempotency.idempotencyKey,
    reliabilityKey: input.idempotency.reliabilityKey,
    duplicateRiskKey: input.idempotency.duplicateRiskKey,
    headers: input.headers,
  };
}

export function createLinkDeliveryReceipt(input: {
  readonly attempt: LinkDeliveryAttemptContract;
  readonly completedAt?: string;
}): LinkDeliveryReceiptContract {
  const completedAt = input.completedAt ?? new Date().toISOString();

  return {
    receiptId: `link-delivery-receipt-${input.attempt.deliveryId}`,
    deliveryId: input.attempt.deliveryId,
    queueId: input.attempt.queueId,
    eventId: input.attempt.eventId,
    traceId: input.attempt.traceId,
    gatewayId: input.attempt.gatewayId,
    streamId: input.attempt.streamId,
    sequenceNumber: input.attempt.sequenceNumber,
    targetId: input.attempt.targetId,
    status: input.attempt.status,
    reasonCode: input.attempt.reasonCode,
    accepted:
      input.attempt.status === 'DELIVERY_DRY_RUN_ACCEPTED' ||
      input.attempt.status === 'DELIVERY_ACCEPTED',
    retryable: input.attempt.retryable,
    dryRun: input.attempt.status === 'DELIVERY_DRY_RUN_ACCEPTED',
    productionDelivery: false,
    receivedAt: input.attempt.startedAt,
    completedAt,
    idempotencyKey: input.attempt.idempotencyKey,
    reliabilityKey: input.attempt.reliabilityKey,
  };
}

export function validateLinkDeliveryAttemptContract(
  attempt: LinkDeliveryAttemptContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!attempt.deliveryId.trim()) reasons.push('deliveryId is required');
  if (!attempt.queueId.trim()) reasons.push('queueId is required');
  if (!attempt.eventId.trim()) reasons.push('eventId is required');
  if (!attempt.traceId.trim()) reasons.push('traceId is required');
  if (!attempt.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!attempt.streamId.trim()) reasons.push('streamId is required');
  if (!Number.isInteger(attempt.sequenceNumber) || attempt.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }
  if (!attempt.targetId.trim()) reasons.push('targetId is required');
  if (!Number.isInteger(attempt.attemptNumber) || attempt.attemptNumber < 1) {
    reasons.push('attemptNumber must be greater than zero');
  }
  if (!Number.isInteger(attempt.maxAttempts) || attempt.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }
  if (!attempt.startedAt.trim()) reasons.push('startedAt is required');
  if (!attempt.idempotencyKey.trim()) reasons.push('idempotencyKey is required');
  if (!attempt.reliabilityKey.trim()) reasons.push('reliabilityKey is required');
  if (!attempt.duplicateRiskKey.trim()) reasons.push('duplicateRiskKey is required');

  return reasons;
}

export function validateLinkDeliveryReceiptContract(
  receipt: LinkDeliveryReceiptContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!receipt.receiptId.trim()) reasons.push('receiptId is required');
  if (!receipt.deliveryId.trim()) reasons.push('deliveryId is required');
  if (!receipt.queueId.trim()) reasons.push('queueId is required');
  if (!receipt.eventId.trim()) reasons.push('eventId is required');
  if (!receipt.traceId.trim()) reasons.push('traceId is required');
  if (!receipt.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!receipt.streamId.trim()) reasons.push('streamId is required');
  if (!Number.isInteger(receipt.sequenceNumber) || receipt.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }
  if (!receipt.targetId.trim()) reasons.push('targetId is required');
  if (!receipt.receivedAt.trim()) reasons.push('receivedAt is required');
  if (!receipt.completedAt.trim()) reasons.push('completedAt is required');
  if (!receipt.idempotencyKey.trim()) reasons.push('idempotencyKey is required');
  if (!receipt.reliabilityKey.trim()) reasons.push('reliabilityKey is required');
  if (receipt.productionDelivery !== false) {
    reasons.push('productionDelivery must remain false');
  }

  return reasons;
}
