/**
 * LINK-C3-03 — Partition metadata and priority lane contract.
 *
 * LINK-owned partition and priority model aligned with EDGE handoff intake and
 * queue item contracts.
 *
 * This contract does not enable production delivery.
 */

import type { EdgeHandoffIntakeContract, EdgeHandoffRecordType } from './edge-handoff-intake-contract.js';
import type { LinkQueueItemContract, LinkQueuePriority } from './queue-item-contract.js';

export type LinkPartitionLane = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';

export interface LinkPartitionMetadata {
  readonly partitionId: number;
  readonly partitionKey: string;
  readonly lane: LinkPartitionLane;
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly gatewayId: string;
  readonly sourceSystem?: string;
  readonly recordType: EdgeHandoffRecordType;
  readonly priority: LinkQueuePriority;
}

export interface LinkPartitionAssignment {
  readonly partitionId: number;
  readonly partitionKey: string;
  readonly lane: LinkPartitionLane;
  readonly reason: 'TENANT_SITE_GATEWAY_RECORD' | 'QUEUE_ITEM' | 'DEFAULT';
}

export interface LinkPriorityLanePolicy {
  readonly lane: LinkPartitionLane;
  readonly maxQueueDepth: number;
  readonly deliveryWeight: number;
  readonly backpressureDropAllowed: boolean;
}

export const DEFAULT_LINK_PRIORITY_LANE_POLICIES: Readonly<Record<LinkPartitionLane, LinkPriorityLanePolicy>> = {
  LOW: {
    lane: 'LOW',
    maxQueueDepth: 500,
    deliveryWeight: 1,
    backpressureDropAllowed: true,
  },
  NORMAL: {
    lane: 'NORMAL',
    maxQueueDepth: 1000,
    deliveryWeight: 2,
    backpressureDropAllowed: false,
  },
  HIGH: {
    lane: 'HIGH',
    maxQueueDepth: 2000,
    deliveryWeight: 4,
    backpressureDropAllowed: false,
  },
  CRITICAL: {
    lane: 'CRITICAL',
    maxQueueDepth: 5000,
    deliveryWeight: 8,
    backpressureDropAllowed: false,
  },
};

export function mapQueuePriorityToPartitionLane(priority: LinkQueuePriority): LinkPartitionLane {
  switch (priority) {
    case 'LOW':
      return 'LOW';
    case 'NORMAL':
      return 'NORMAL';
    case 'HIGH':
      return 'HIGH';
    case 'CRITICAL':
      return 'CRITICAL';
  }
}

export function createPartitionKeyFromParts(input: {
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly gatewayId: string;
  readonly recordType: EdgeHandoffRecordType;
}): string {
  return [
    input.tenantId ?? 'tenant-unknown',
    input.siteId ?? 'site-unknown',
    input.gatewayId,
    input.recordType,
  ].join(':');
}

export function assignPartitionId(partitionKey: string, partitionCount: number): number {
  if (!Number.isInteger(partitionCount) || partitionCount < 1) {
    throw new Error('partitionCount must be greater than zero');
  }

  let hash = 0;
  for (let index = 0; index < partitionKey.length; index += 1) {
    hash = (hash * 31 + partitionKey.charCodeAt(index)) >>> 0;
  }

  return hash % partitionCount;
}

export function createPartitionMetadataFromIntake(
  intake: EdgeHandoffIntakeContract,
  priority: LinkQueuePriority,
  partitionCount: number,
): LinkPartitionMetadata {
  const partitionKey = createPartitionKeyFromParts({
    tenantId: intake.source.tenantId,
    siteId: intake.source.siteId,
    gatewayId: intake.source.gatewayId,
    recordType: intake.recordType,
  });
  const partitionId = assignPartitionId(partitionKey, partitionCount);

  return {
    partitionId,
    partitionKey,
    lane: mapQueuePriorityToPartitionLane(priority),
    ...(intake.source.tenantId !== undefined ? { tenantId: intake.source.tenantId } : {}),
    ...(intake.source.siteId !== undefined ? { siteId: intake.source.siteId } : {}),
    gatewayId: intake.source.gatewayId,
    ...(intake.source.sourceSystem !== undefined ? { sourceSystem: intake.source.sourceSystem } : {}),
    recordType: intake.recordType,
    priority,
  };
}

export function createPartitionAssignmentFromQueueItem(
  item: LinkQueueItemContract,
): LinkPartitionAssignment {
  return {
    partitionId: item.partitionId,
    partitionKey: item.partitionKey,
    lane: mapQueuePriorityToPartitionLane(item.priority),
    reason: 'QUEUE_ITEM',
  };
}

export function validatePartitionMetadata(metadata: LinkPartitionMetadata): readonly string[] {
  const reasons: string[] = [];

  if (!Number.isInteger(metadata.partitionId) || metadata.partitionId < 0) {
    reasons.push('partitionId must be a non-negative integer');
  }

  if (!metadata.partitionKey.trim()) {
    reasons.push('partitionKey is required');
  }

  if (!metadata.gatewayId.trim()) {
    reasons.push('gatewayId is required');
  }

  const policy = DEFAULT_LINK_PRIORITY_LANE_POLICIES[metadata.lane];
  if (policy.lane !== metadata.lane) {
    reasons.push('lane policy mismatch');
  }

  return reasons;
}
