/**
 * LINK-C7-01 — Runtime health snapshot contract.
 *
 * LINK-owned runtime operations health model for ingress, queue, DLQ, delivery,
 * retry, replay, gateway liveness, evidence, and production-blocked state.
 *
 * This contract does not enable production delivery.
 */

export type LinkRuntimeHealthStatus =
  | 'HEALTHY'
  | 'DEGRADED'
  | 'UNHEALTHY'
  | 'BLOCKED'
  | 'UNKNOWN';

export type LinkRuntimeReadyStatus =
  | 'READY'
  | 'NOT_READY'
  | 'DEGRADED'
  | 'BLOCKED';

export type LinkRuntimeComponentStatus =
  | 'OK'
  | 'WARN'
  | 'ERROR'
  | 'BLOCKED'
  | 'UNKNOWN';

export interface LinkRuntimeIngressStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly acceptedCount: number;
  readonly rejectedCount: number;
  readonly blockedCount: number;
  readonly duplicateCount: number;
  readonly lastIngressAt?: string;
}

export interface LinkRuntimeQueueStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly queueDepth: number;
  readonly oldestQueueAgeMs: number;
  readonly partitionCount: number;
  readonly criticalLaneDepth: number;
  readonly highLaneDepth: number;
  readonly normalLaneDepth: number;
  readonly lowLaneDepth: number;
}

export interface LinkRuntimeDlqStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly dlqCount: number;
  readonly replayEligibleCount: number;
  readonly operatorActionRequiredCount: number;
  readonly lastDlqAt?: string;
}

export interface LinkRuntimeDeliveryStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly dryRunAcceptedCount: number;
  readonly blockedCount: number;
  readonly retryableCount: number;
  readonly rejectedCount: number;
  readonly lastDeliveryAt?: string;
  readonly productionDeliveryAllowed: false;
}

export interface LinkRuntimeRetryReplayStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly retryPendingCount: number;
  readonly retryBudgetRemaining: number;
  readonly replayRequestedCount: number;
  readonly replayBudgetRemaining: number;
  readonly stormProtectedCount: number;
}

export interface LinkRuntimeGatewayLivenessStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly onlineGatewayCount: number;
  readonly degradedGatewayCount: number;
  readonly offlineGatewayCount: number;
  readonly missedHeartbeatCount: number;
  readonly lastHeartbeatAt?: string;
}

export interface LinkRuntimeEvidenceStatus {
  readonly status: LinkRuntimeComponentStatus;
  readonly evidenceChainCount: number;
  readonly incompleteChainCount: number;
  readonly tamperMismatchCount: number;
  readonly lastEvidenceAt?: string;
}

export interface LinkRuntimeHealthSnapshotContract {
  readonly snapshotId: string;
  readonly linkNodeId: string;
  readonly generatedAt: string;
  readonly healthStatus: LinkRuntimeHealthStatus;
  readonly readyStatus: LinkRuntimeReadyStatus;
  readonly ingress: LinkRuntimeIngressStatus;
  readonly queue: LinkRuntimeQueueStatus;
  readonly dlq: LinkRuntimeDlqStatus;
  readonly delivery: LinkRuntimeDeliveryStatus;
  readonly retryReplay: LinkRuntimeRetryReplayStatus;
  readonly gatewayLiveness: LinkRuntimeGatewayLivenessStatus;
  readonly evidence: LinkRuntimeEvidenceStatus;
  readonly warnings: readonly string[];
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export function createLinkRuntimeHealthSnapshotId(input: {
  readonly linkNodeId: string;
  readonly generatedAt: string;
}): string {
  return `link-health-${input.linkNodeId}-${input.generatedAt}`;
}

export function deriveLinkRuntimeHealthStatus(input: {
  readonly ingress: LinkRuntimeIngressStatus;
  readonly queue: LinkRuntimeQueueStatus;
  readonly dlq: LinkRuntimeDlqStatus;
  readonly delivery: LinkRuntimeDeliveryStatus;
  readonly retryReplay: LinkRuntimeRetryReplayStatus;
  readonly gatewayLiveness: LinkRuntimeGatewayLivenessStatus;
  readonly evidence: LinkRuntimeEvidenceStatus;
}): LinkRuntimeHealthStatus {
  const statuses = [
    input.ingress.status,
    input.queue.status,
    input.dlq.status,
    input.delivery.status,
    input.retryReplay.status,
    input.gatewayLiveness.status,
    input.evidence.status,
  ];

  if (statuses.includes('ERROR')) {
    return 'UNHEALTHY';
  }

  if (statuses.includes('BLOCKED')) {
    return 'BLOCKED';
  }

  if (statuses.includes('WARN')) {
    return 'DEGRADED';
  }

  if (statuses.every((status) => status === 'OK')) {
    return 'HEALTHY';
  }

  return 'UNKNOWN';
}

export function deriveLinkRuntimeReadyStatus(
  healthStatus: LinkRuntimeHealthStatus,
): LinkRuntimeReadyStatus {
  switch (healthStatus) {
    case 'HEALTHY':
      return 'READY';
    case 'DEGRADED':
      return 'DEGRADED';
    case 'BLOCKED':
      return 'BLOCKED';
    case 'UNHEALTHY':
    case 'UNKNOWN':
      return 'NOT_READY';
  }
}

export function createDefaultLinkRuntimeHealthSnapshot(input: {
  readonly linkNodeId: string;
  readonly generatedAt: string;
}): LinkRuntimeHealthSnapshotContract {
  const ingress: LinkRuntimeIngressStatus = {
    status: 'OK',
    acceptedCount: 0,
    rejectedCount: 0,
    blockedCount: 0,
    duplicateCount: 0,
  };

  const queue: LinkRuntimeQueueStatus = {
    status: 'OK',
    queueDepth: 0,
    oldestQueueAgeMs: 0,
    partitionCount: 0,
    criticalLaneDepth: 0,
    highLaneDepth: 0,
    normalLaneDepth: 0,
    lowLaneDepth: 0,
  };

  const dlq: LinkRuntimeDlqStatus = {
    status: 'OK',
    dlqCount: 0,
    replayEligibleCount: 0,
    operatorActionRequiredCount: 0,
  };

  const delivery: LinkRuntimeDeliveryStatus = {
    status: 'BLOCKED',
    dryRunAcceptedCount: 0,
    blockedCount: 0,
    retryableCount: 0,
    rejectedCount: 0,
    productionDeliveryAllowed: false,
  };

  const retryReplay: LinkRuntimeRetryReplayStatus = {
    status: 'OK',
    retryPendingCount: 0,
    retryBudgetRemaining: 0,
    replayRequestedCount: 0,
    replayBudgetRemaining: 0,
    stormProtectedCount: 0,
  };

  const gatewayLiveness: LinkRuntimeGatewayLivenessStatus = {
    status: 'OK',
    onlineGatewayCount: 0,
    degradedGatewayCount: 0,
    offlineGatewayCount: 0,
    missedHeartbeatCount: 0,
  };

  const evidence: LinkRuntimeEvidenceStatus = {
    status: 'OK',
    evidenceChainCount: 0,
    incompleteChainCount: 0,
    tamperMismatchCount: 0,
  };

  const healthStatus = deriveLinkRuntimeHealthStatus({
    ingress,
    queue,
    dlq,
    delivery,
    retryReplay,
    gatewayLiveness,
    evidence,
  });

  return {
    snapshotId: createLinkRuntimeHealthSnapshotId(input),
    linkNodeId: input.linkNodeId,
    generatedAt: input.generatedAt,
    healthStatus,
    readyStatus: deriveLinkRuntimeReadyStatus(healthStatus),
    ingress,
    queue,
    dlq,
    delivery,
    retryReplay,
    gatewayLiveness,
    evidence,
    warnings: ['production delivery remains blocked'],
    runtimeEnabled: false,
    productionDeliveryAllowed: false,
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };
}

export function validateLinkRuntimeHealthSnapshotContract(
  snapshot: LinkRuntimeHealthSnapshotContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!snapshot.snapshotId.trim()) reasons.push('snapshotId is required');
  if (!snapshot.linkNodeId.trim()) reasons.push('linkNodeId is required');
  if (!snapshot.generatedAt.trim()) reasons.push('generatedAt is required');

  if (snapshot.ingress.acceptedCount < 0) reasons.push('ingress.acceptedCount must not be negative');
  if (snapshot.ingress.rejectedCount < 0) reasons.push('ingress.rejectedCount must not be negative');
  if (snapshot.ingress.blockedCount < 0) reasons.push('ingress.blockedCount must not be negative');
  if (snapshot.ingress.duplicateCount < 0) reasons.push('ingress.duplicateCount must not be negative');

  if (snapshot.queue.queueDepth < 0) reasons.push('queue.queueDepth must not be negative');
  if (snapshot.queue.oldestQueueAgeMs < 0) reasons.push('queue.oldestQueueAgeMs must not be negative');
  if (snapshot.queue.partitionCount < 0) reasons.push('queue.partitionCount must not be negative');

  if (snapshot.dlq.dlqCount < 0) reasons.push('dlq.dlqCount must not be negative');
  if (snapshot.dlq.replayEligibleCount < 0) reasons.push('dlq.replayEligibleCount must not be negative');
  if (snapshot.dlq.operatorActionRequiredCount < 0) {
    reasons.push('dlq.operatorActionRequiredCount must not be negative');
  }

  if (snapshot.delivery.productionDeliveryAllowed !== false) {
    reasons.push('delivery.productionDeliveryAllowed must remain false');
  }

  if (snapshot.retryReplay.retryPendingCount < 0) {
    reasons.push('retryReplay.retryPendingCount must not be negative');
  }

  if (snapshot.gatewayLiveness.onlineGatewayCount < 0) {
    reasons.push('gatewayLiveness.onlineGatewayCount must not be negative');
  }

  if (snapshot.evidence.evidenceChainCount < 0) {
    reasons.push('evidence.evidenceChainCount must not be negative');
  }

  if (snapshot.runtimeEnabled !== false) reasons.push('runtimeEnabled must remain false');
  if (snapshot.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }
  if (snapshot.writebackAllowed !== false) reasons.push('writebackAllowed must remain false');
  if (snapshot.directDbAccessAllowed !== false) reasons.push('directDbAccessAllowed must remain false');

  return reasons;
}
