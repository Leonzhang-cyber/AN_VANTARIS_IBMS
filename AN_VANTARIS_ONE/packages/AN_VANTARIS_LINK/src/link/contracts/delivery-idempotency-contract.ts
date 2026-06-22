/**
 * LINK-C4-02B — Delivery idempotency contract.
 *
 * LINK-owned idempotency key and outbound header contract.
 *
 * This version aligns delivery idempotency with EDGE-C8 outbox reliability by
 * carrying streamId and sequenceNumber.
 *
 * This contract does not enable production delivery.
 */

import type { EdgeHandoffIntakeContract } from './edge-handoff-intake-contract.js';
import type { EdgeLinkSequenceRef } from './edge-link-reliability-contract.js';
import { createEdgeLinkReliabilityKey } from './edge-link-reliability-contract.js';
import type { LinkQueueItemContract } from './queue-item-contract.js';

export interface LinkDeliveryIdempotencyInput {
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly payloadHash: string;
  readonly recordType: string;
  readonly occurredAt: string;
  readonly queueId: string;
  readonly dedupeKey?: string;
}

export interface LinkDeliveryIdempotencyContract {
  readonly idempotencyKey: string;
  readonly reliabilityKey: string;
  readonly duplicateRiskKey: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly payloadHash: string;
  readonly recordType: string;
  readonly occurredAt: string;
  readonly queueId: string;
  readonly dedupeKey?: string;
}

export interface LinkDeliveryHeaders {
  readonly 'X-VANTARIS-Idempotency-Key': string;
  readonly 'X-VANTARIS-Reliability-Key': string;
  readonly 'X-VANTARIS-Trace-Id': string;
  readonly 'X-VANTARIS-Gateway-Id': string;
  readonly 'X-VANTARIS-Stream-Id': string;
  readonly 'X-VANTARIS-Sequence-Number': string;
  readonly 'X-VANTARIS-Link-Queue-Id': string;
  readonly 'X-VANTARIS-Link-Delivery-Id': string;
}

export function createEdgeLinkSequenceRefFromIdempotencyInput(
  input: LinkDeliveryIdempotencyInput,
): EdgeLinkSequenceRef {
  return {
    stream: {
      gatewayId: input.gatewayId,
      streamId: input.streamId,
    },
    sequenceNumber: input.sequenceNumber,
    eventId: input.eventId,
    traceId: input.traceId,
    payloadHash: input.payloadHash,
    occurredAt: input.occurredAt,
  };
}

export function createDuplicateRiskKey(input: LinkDeliveryIdempotencyInput): string {
  return [
    input.gatewayId,
    input.streamId,
    String(input.sequenceNumber),
    input.eventId,
    input.payloadHash,
    input.dedupeKey ?? 'dedupe-none',
  ].join(':');
}

export function createLinkDeliveryIdempotencyKey(input: LinkDeliveryIdempotencyInput): string {
  return [
    'vantaris-link',
    input.gatewayId,
    input.streamId,
    String(input.sequenceNumber),
    input.recordType,
    input.eventId,
    input.payloadHash,
    input.queueId,
  ].join(':');
}

export function createLinkDeliveryIdempotencyContract(
  input: LinkDeliveryIdempotencyInput,
): LinkDeliveryIdempotencyContract {
  const sequenceRef = createEdgeLinkSequenceRefFromIdempotencyInput(input);

  return {
    idempotencyKey: createLinkDeliveryIdempotencyKey(input),
    reliabilityKey: createEdgeLinkReliabilityKey(sequenceRef),
    duplicateRiskKey: createDuplicateRiskKey(input),
    eventId: input.eventId,
    traceId: input.traceId,
    gatewayId: input.gatewayId,
    streamId: input.streamId,
    sequenceNumber: input.sequenceNumber,
    payloadHash: input.payloadHash,
    recordType: input.recordType,
    occurredAt: input.occurredAt,
    queueId: input.queueId,
    ...(input.dedupeKey !== undefined ? { dedupeKey: input.dedupeKey } : {}),
  };
}

export function createIdempotencyInputFromQueueItem(
  intake: EdgeHandoffIntakeContract,
  item: LinkQueueItemContract,
): LinkDeliveryIdempotencyInput {
  const normalized = intake.normalizedPayload as
    | {
        readonly dedupeKey?: unknown;
        readonly streamId?: unknown;
        readonly sequenceNumber?: unknown;
      }
    | null
    | undefined;

  const dedupeKey =
    typeof normalized?.dedupeKey === 'string' && normalized.dedupeKey.trim()
      ? normalized.dedupeKey
      : undefined;

  const streamId =
    typeof normalized?.streamId === 'string' && normalized.streamId.trim()
      ? normalized.streamId
      : item.partitionIdentity.recordType;

  const sequenceNumber =
    typeof normalized?.sequenceNumber === 'number' && Number.isInteger(normalized.sequenceNumber)
      ? normalized.sequenceNumber
      : 0;

  return {
    eventId: item.eventId,
    traceId: item.traceId,
    gatewayId: item.gatewayId,
    streamId,
    sequenceNumber,
    payloadHash: item.payloadHash,
    recordType: item.partitionIdentity.recordType,
    occurredAt: intake.occurredAt,
    queueId: item.queueId,
    ...(dedupeKey !== undefined ? { dedupeKey } : {}),
  };
}

export function createLinkDeliveryHeaders(input: {
  readonly idempotency: LinkDeliveryIdempotencyContract;
  readonly deliveryId: string;
}): LinkDeliveryHeaders {
  return {
    'X-VANTARIS-Idempotency-Key': input.idempotency.idempotencyKey,
    'X-VANTARIS-Reliability-Key': input.idempotency.reliabilityKey,
    'X-VANTARIS-Trace-Id': input.idempotency.traceId,
    'X-VANTARIS-Gateway-Id': input.idempotency.gatewayId,
    'X-VANTARIS-Stream-Id': input.idempotency.streamId,
    'X-VANTARIS-Sequence-Number': String(input.idempotency.sequenceNumber),
    'X-VANTARIS-Link-Queue-Id': input.idempotency.queueId,
    'X-VANTARIS-Link-Delivery-Id': input.deliveryId,
  };
}

export function validateLinkDeliveryIdempotencyContract(
  contract: LinkDeliveryIdempotencyContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!contract.idempotencyKey.trim()) {
    reasons.push('idempotencyKey is required');
  }

  if (!contract.reliabilityKey.trim()) {
    reasons.push('reliabilityKey is required');
  }

  if (!contract.duplicateRiskKey.trim()) {
    reasons.push('duplicateRiskKey is required');
  }

  if (!contract.eventId.trim()) {
    reasons.push('eventId is required');
  }

  if (!contract.traceId.trim()) {
    reasons.push('traceId is required');
  }

  if (!contract.gatewayId.trim()) {
    reasons.push('gatewayId is required');
  }

  if (!contract.streamId.trim()) {
    reasons.push('streamId is required');
  }

  if (!Number.isInteger(contract.sequenceNumber) || contract.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }

  if (!contract.payloadHash.trim()) {
    reasons.push('payloadHash is required');
  }

  if (!contract.recordType.trim()) {
    reasons.push('recordType is required');
  }

  if (!contract.occurredAt.trim()) {
    reasons.push('occurredAt is required');
  }

  if (!contract.queueId.trim()) {
    reasons.push('queueId is required');
  }

  return reasons;
}
