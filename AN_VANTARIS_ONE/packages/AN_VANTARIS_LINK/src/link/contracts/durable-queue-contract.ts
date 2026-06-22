/**
 * LINK-C3-04 — Local durable queue / recovery path contract.
 *
 * LINK-owned durable queue model for append-only local recovery planning.
 *
 * This contract does not write runtime files by itself and does not enable
 * production delivery.
 */

import type { LinkQueueItemContract } from './queue-item-contract.js';
import type {
  LinkGaQueueState,
  LinkQueueTransitionReason,
} from './queue-state-contract.js';

export type LinkDurableQueueRecordKind =
  | 'QUEUE_APPEND'
  | 'QUEUE_STATE_TRANSITION'
  | 'QUEUE_RECOVERY_SNAPSHOT'
  | 'QUEUE_REPLAY_MARKER';

export interface LinkDurableQueueRecord {
  readonly recordId: string;
  readonly kind: LinkDurableQueueRecordKind;
  readonly queueId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly partitionId: number;
  readonly partitionKey: string;
  readonly state: LinkGaQueueState;
  readonly reason: LinkQueueTransitionReason;
  readonly payloadHash: string;
  readonly recordedAt: string;
  readonly item?: LinkQueueItemContract;
}

export interface LinkDurableQueueRecoveryPlan {
  readonly recoveryId: string;
  readonly partitionId: number;
  readonly startedAt: string;
  readonly source: 'LOCAL_APPEND_ONLY_LOG' | 'SNAPSHOT' | 'DRY_RUN';
  readonly recoveredRecords: number;
  readonly skippedRecords: number;
  readonly warnings: readonly string[];
}

export interface LinkDurableQueueReplayCandidate {
  readonly queueId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly partitionId: number;
  readonly eligible: boolean;
  readonly reason: string;
}

export function createDurableQueueAppendRecord(
  item: LinkQueueItemContract,
  recordedAt = new Date().toISOString(),
): LinkDurableQueueRecord {
  return {
    recordId: `link-durable-${item.queueId}-${item.state}`,
    kind: 'QUEUE_APPEND',
    queueId: item.queueId,
    eventId: item.eventId,
    traceId: item.traceId,
    gatewayId: item.gatewayId,
    partitionId: item.partitionId,
    partitionKey: item.partitionKey,
    state: item.state,
    reason: item.stateSnapshot.reason,
    payloadHash: item.payloadHash,
    recordedAt,
    item,
  };
}

export function createDurableQueueStateTransitionRecord(input: {
  readonly item: LinkQueueItemContract;
  readonly to: LinkGaQueueState;
  readonly reason: LinkQueueTransitionReason;
  readonly recordedAt?: string;
}): LinkDurableQueueRecord {
  const recordedAt = input.recordedAt ?? new Date().toISOString();

  return {
    recordId: `link-durable-${input.item.queueId}-${input.to}-${recordedAt}`,
    kind: 'QUEUE_STATE_TRANSITION',
    queueId: input.item.queueId,
    eventId: input.item.eventId,
    traceId: input.item.traceId,
    gatewayId: input.item.gatewayId,
    partitionId: input.item.partitionId,
    partitionKey: input.item.partitionKey,
    state: input.to,
    reason: input.reason,
    payloadHash: input.item.payloadHash,
    recordedAt,
  };
}

export function createDryRunRecoveryPlan(input: {
  readonly partitionId: number;
  readonly recoveredRecords: number;
  readonly skippedRecords?: number;
  readonly warnings?: readonly string[];
  readonly startedAt?: string;
}): LinkDurableQueueRecoveryPlan {
  const startedAt = input.startedAt ?? new Date().toISOString();

  return {
    recoveryId: `link-recovery-${input.partitionId}-${startedAt}`,
    partitionId: input.partitionId,
    startedAt,
    source: 'DRY_RUN',
    recoveredRecords: input.recoveredRecords,
    skippedRecords: input.skippedRecords ?? 0,
    warnings: input.warnings ?? [],
  };
}

export function createReplayCandidateFromRecord(
  record: LinkDurableQueueRecord,
): LinkDurableQueueReplayCandidate {
  const terminalBlocked = record.state === 'ACKED' || record.state === 'REJECTED' || record.state === 'EXPIRED';

  return {
    queueId: record.queueId,
    eventId: record.eventId,
    traceId: record.traceId,
    partitionId: record.partitionId,
    eligible: !terminalBlocked,
    reason: terminalBlocked
      ? `state ${record.state} is terminal and not replay eligible`
      : `state ${record.state} is replay eligible`,
  };
}

export function validateDurableQueueRecord(
  record: LinkDurableQueueRecord,
): readonly string[] {
  const reasons: string[] = [];

  if (!record.recordId.trim()) {
    reasons.push('recordId is required');
  }

  if (!record.queueId.trim()) {
    reasons.push('queueId is required');
  }

  if (!record.eventId.trim()) {
    reasons.push('eventId is required');
  }

  if (!record.traceId.trim()) {
    reasons.push('traceId is required');
  }

  if (!record.gatewayId.trim()) {
    reasons.push('gatewayId is required');
  }

  if (!Number.isInteger(record.partitionId) || record.partitionId < 0) {
    reasons.push('partitionId must be a non-negative integer');
  }

  if (!record.partitionKey.trim()) {
    reasons.push('partitionKey is required');
  }

  if (!record.payloadHash.trim()) {
    reasons.push('payloadHash is required');
  }

  return reasons;
}
