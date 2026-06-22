/**
 * LINK-C3-02 — Queue item contract alignment.
 *
 * LINK-owned queue item contract aligned with C2 EDGE handoff intake and C3
 * GA-ready queue state model.
 *
 * This contract does not enable production delivery.
 */

import type {
  EdgeHandoffEvidenceRef,
  EdgeHandoffIntakeContract,
  EdgeHandoffRecordType,
} from './edge-handoff-intake-contract.js';
import type {
  LinkGaQueueState,
  LinkQueueStateSnapshot,
  LinkQueueTransitionReason,
} from './queue-state-contract.js';
import { createLinkQueueStateSnapshot } from './queue-state-contract.js';

export type LinkQueuePriority = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';

export interface LinkQueuePartitionIdentity {
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly gatewayId: string;
  readonly sourceSystem?: string;
  readonly recordType: EdgeHandoffRecordType;
}

export interface LinkQueueItemContract {
  readonly queueId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly correlationId?: string;
  readonly gatewayId: string;
  readonly partitionKey: string;
  readonly partitionId: number;
  readonly priority: LinkQueuePriority;
  readonly state: LinkGaQueueState;
  readonly attempts: number;
  readonly maxAttempts: number;
  readonly enqueuedAt: string;
  readonly updatedAt: string;
  readonly availableAt: string;
  readonly expiresAt?: string;
  readonly payloadHash: string;
  readonly reasonCode?: string;
  readonly stateSnapshot: LinkQueueStateSnapshot;
  readonly partitionIdentity: LinkQueuePartitionIdentity;
  readonly evidenceRefs: readonly EdgeHandoffEvidenceRef[];
}

export interface CreateLinkQueueItemInput {
  readonly intake: EdgeHandoffIntakeContract;
  readonly queueId: string;
  readonly partitionId: number;
  readonly partitionKey?: string;
  readonly priority?: LinkQueuePriority;
  readonly maxAttempts?: number;
  readonly enqueuedAt?: string;
  readonly availableAt?: string;
  readonly expiresAt?: string;
  readonly reason?: LinkQueueTransitionReason;
}

export function createPartitionKeyFromIntake(intake: EdgeHandoffIntakeContract): string {
  const tenant = intake.source.tenantId ?? 'tenant-unknown';
  const site = intake.source.siteId ?? 'site-unknown';
  const gateway = intake.source.gatewayId;
  const recordType = intake.recordType;

  return [tenant, site, gateway, recordType].join(':');
}

export function inferQueuePriorityFromRecordType(
  recordType: EdgeHandoffRecordType,
): LinkQueuePriority {
  if (recordType === 'alarm') {
    return 'CRITICAL';
  }

  if (recordType === 'event' || recordType === 'health') {
    return 'HIGH';
  }

  if (recordType === 'audit' || recordType === 'evidence') {
    return 'NORMAL';
  }

  return 'NORMAL';
}

export function createLinkQueueItemContract(
  input: CreateLinkQueueItemInput,
): LinkQueueItemContract {
  const now = input.enqueuedAt ?? new Date().toISOString();
  const priority = input.priority ?? inferQueuePriorityFromRecordType(input.intake.recordType);
  const partitionKey = input.partitionKey ?? createPartitionKeyFromIntake(input.intake);
  const reason = input.reason ?? 'INGRESS_QUEUED';

  return {
    queueId: input.queueId,
    eventId: input.intake.eventId,
    traceId: input.intake.traceId,
    ...(input.intake.correlationId !== undefined
      ? { correlationId: input.intake.correlationId }
      : {}),
    gatewayId: input.intake.source.gatewayId,
    partitionKey,
    partitionId: input.partitionId,
    priority,
    state: 'QUEUED',
    attempts: 0,
    maxAttempts: input.maxAttempts ?? 3,
    enqueuedAt: now,
    updatedAt: now,
    availableAt: input.availableAt ?? now,
    ...(input.expiresAt !== undefined ? { expiresAt: input.expiresAt } : {}),
    payloadHash: input.intake.payloadHash,
    stateSnapshot: createLinkQueueStateSnapshot('QUEUED', reason, 0, now),
    partitionIdentity: {
      ...(input.intake.source.tenantId !== undefined
        ? { tenantId: input.intake.source.tenantId }
        : {}),
      ...(input.intake.source.siteId !== undefined
        ? { siteId: input.intake.source.siteId }
        : {}),
      gatewayId: input.intake.source.gatewayId,
      ...(input.intake.source.sourceSystem !== undefined
        ? { sourceSystem: input.intake.source.sourceSystem }
        : {}),
      recordType: input.intake.recordType,
    },
    evidenceRefs: input.intake.evidenceRefs,
  };
}

export function validateLinkQueueItemContract(
  item: LinkQueueItemContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!item.queueId.trim()) {
    reasons.push('queueId is required');
  }

  if (!item.eventId.trim()) {
    reasons.push('eventId is required');
  }

  if (!item.traceId.trim()) {
    reasons.push('traceId is required');
  }

  if (!item.gatewayId.trim()) {
    reasons.push('gatewayId is required');
  }

  if (!item.partitionKey.trim()) {
    reasons.push('partitionKey is required');
  }

  if (!Number.isInteger(item.partitionId) || item.partitionId < 0) {
    reasons.push('partitionId must be a non-negative integer');
  }

  if (!item.payloadHash.trim()) {
    reasons.push('payloadHash is required');
  }

  if (item.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }

  if (item.attempts < 0) {
    reasons.push('attempts must not be negative');
  }

  return reasons;
}
