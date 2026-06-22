/**
 * EDGE-C8-11 — EDGE health snapshot contract.
 *
 * EDGE-owned health snapshot model for local diagnostics, LINK liveness,
 * outbox status, heartbeat status, adapter summary, connector summary,
 * resource status, and production-blocked state.
 *
 * This contract does not enable runtime, pilot, production, writeback, or direct
 * UFMS DB access.
 */

import type {
  EdgeGatewayLivenessStatus,
  EdgeHeartbeatContract,
  EdgeLinkConnectivityStatus,
} from './edge-heartbeat-liveness-contract.js';

import type {
  EdgeOutboxCapacityPolicy,
  EdgeOutboxRetryPolicy,
} from './edge-outbox-reliability-contract.js';

export type EdgeHealthOverallStatus =
  | 'HEALTHY'
  | 'DEGRADED'
  | 'UNHEALTHY'
  | 'LOCKED'
  | 'MAINTENANCE'
  | 'UNKNOWN';

export type EdgeHealthComponentStatus =
  | 'OK'
  | 'WARN'
  | 'ERROR'
  | 'OFFLINE'
  | 'LOCKED'
  | 'UNKNOWN';

export interface EdgeHealthComponentSummary {
  readonly componentId: string;
  readonly componentType:
    | 'runtime'
    | 'heartbeat'
    | 'link'
    | 'outbox'
    | 'adapter'
    | 'connector'
    | 'resource'
    | 'security'
    | 'policy'
    | 'evidence';
  readonly status: EdgeHealthComponentStatus;
  readonly message: string;
  readonly lastUpdatedAt: string;
}

export interface EdgeHealthOutboxStatus {
  readonly depth: number;
  readonly oldestAgeMs: number;
  readonly retryPendingCount: number;
  readonly replayRequestedCount: number;
  readonly ackPendingCount: number;
  readonly localDlqCount: number;
  readonly capacityPolicy: EdgeOutboxCapacityPolicy;
  readonly retryPolicy: EdgeOutboxRetryPolicy;
}

export interface EdgeHealthHeartbeatStatus {
  readonly heartbeatId: string;
  readonly sequenceNumber: number;
  readonly livenessStatus: EdgeGatewayLivenessStatus;
  readonly linkConnectivityStatus: EdgeLinkConnectivityStatus;
  readonly missedAckCount: number;
  readonly consecutiveMissedHeartbeatCount: number;
  readonly lastSuccessfulAckAt?: string;
  readonly generatedAt: string;
}

export interface EdgeHealthSecurityStatus {
  readonly machineIdentityConfigured: boolean;
  readonly credentialRefConfigured: boolean;
  readonly secretMaterialStored: false;
  readonly lockedMode: boolean;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export interface EdgeHealthPolicyStatus {
  readonly runtimeEnabled: false;
  readonly pilotApproved: false;
  readonly productionApproved: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackProhibited: true;
  readonly policyVersion?: string;
  readonly configVersion?: string;
}

export interface EdgeHealthResourceStatus {
  readonly diskFreeBytes?: number;
  readonly diskTotalBytes?: number;
  readonly memoryUsedBytes?: number;
  readonly memoryTotalBytes?: number;
  readonly cpuLoadPercent?: number;
}

export interface EdgeHealthSnapshotContract {
  readonly snapshotId: string;
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly generatedAt: string;
  readonly overallStatus: EdgeHealthOverallStatus;
  readonly heartbeat: EdgeHealthHeartbeatStatus;
  readonly outbox: EdgeHealthOutboxStatus;
  readonly resources: EdgeHealthResourceStatus;
  readonly security: EdgeHealthSecurityStatus;
  readonly policy: EdgeHealthPolicyStatus;
  readonly components: readonly EdgeHealthComponentSummary[];
  readonly evidenceRefs: readonly string[];
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export function createEdgeHealthSnapshotId(input: {
  readonly gatewayId: string;
  readonly generatedAt: string;
}): string {
  return `edge-health-${input.gatewayId}-${input.generatedAt}`;
}

export function deriveOverallHealthStatus(input: {
  readonly heartbeat: EdgeHealthHeartbeatStatus;
  readonly components: readonly EdgeHealthComponentSummary[];
  readonly lockedMode: boolean;
}): EdgeHealthOverallStatus {
  if (input.lockedMode) {
    return 'LOCKED';
  }

  if (input.heartbeat.livenessStatus === 'OFFLINE') {
    return 'UNHEALTHY';
  }

  if (
    input.heartbeat.livenessStatus === 'DEGRADED' ||
    input.components.some((component) => component.status === 'ERROR')
  ) {
    return 'DEGRADED';
  }

  if (input.components.some((component) => component.status === 'WARN')) {
    return 'DEGRADED';
  }

  return 'HEALTHY';
}

export function createEdgeHealthSnapshotFromHeartbeat(input: {
  readonly heartbeat: EdgeHeartbeatContract;
  readonly outboxCapacityPolicy: EdgeOutboxCapacityPolicy;
  readonly outboxRetryPolicy: EdgeOutboxRetryPolicy;
  readonly components?: readonly EdgeHealthComponentSummary[];
  readonly policyVersion?: string;
  readonly configVersion?: string;
  readonly evidenceRefs?: readonly string[];
}): EdgeHealthSnapshotContract {
  const components = input.components ?? [];
  const generatedAt = input.heartbeat.timing.generatedAt;

  const heartbeatStatus: EdgeHealthHeartbeatStatus = {
    heartbeatId: input.heartbeat.identity.heartbeatId,
    sequenceNumber: input.heartbeat.identity.sequenceNumber,
    livenessStatus: input.heartbeat.livenessStatus,
    linkConnectivityStatus: input.heartbeat.linkConnectivityStatus,
    missedAckCount: input.heartbeat.timing.missedAckCount,
    consecutiveMissedHeartbeatCount: input.heartbeat.timing.consecutiveMissedHeartbeatCount,
    ...(input.heartbeat.timing.lastSuccessfulAckAt !== undefined
      ? { lastSuccessfulAckAt: input.heartbeat.timing.lastSuccessfulAckAt }
      : {}),
    generatedAt,
  };

  const security: EdgeHealthSecurityStatus = {
    machineIdentityConfigured: false,
    credentialRefConfigured: false,
    secretMaterialStored: false,
    lockedMode: input.heartbeat.runtimeStatus === 'LOCKED',
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };

  const policy: EdgeHealthPolicyStatus = {
    runtimeEnabled: false,
    pilotApproved: false,
    productionApproved: false,
    productionDeliveryAllowed: false,
    writebackProhibited: true,
    ...(input.policyVersion !== undefined ? { policyVersion: input.policyVersion } : {}),
    ...(input.configVersion !== undefined ? { configVersion: input.configVersion } : {}),
  };

  return {
    snapshotId: createEdgeHealthSnapshotId({
      gatewayId: input.heartbeat.identity.gatewayId,
      generatedAt,
    }),
    gatewayId: input.heartbeat.identity.gatewayId,
    ...(input.heartbeat.identity.edgeId !== undefined ? { edgeId: input.heartbeat.identity.edgeId } : {}),
    ...(input.heartbeat.identity.tenantId !== undefined ? { tenantId: input.heartbeat.identity.tenantId } : {}),
    ...(input.heartbeat.identity.siteId !== undefined ? { siteId: input.heartbeat.identity.siteId } : {}),
    generatedAt,
    overallStatus: deriveOverallHealthStatus({
      heartbeat: heartbeatStatus,
      components,
      lockedMode: security.lockedMode,
    }),
    heartbeat: heartbeatStatus,
    outbox: {
      depth: input.heartbeat.outbox.outboxDepth,
      oldestAgeMs: input.heartbeat.outbox.outboxOldestAgeMs,
      retryPendingCount: input.heartbeat.outbox.retryPendingCount,
      replayRequestedCount: input.heartbeat.outbox.replayRequestedCount,
      ackPendingCount: input.heartbeat.outbox.ackPendingCount,
      localDlqCount: input.heartbeat.outbox.localDlqCount,
      capacityPolicy: input.outboxCapacityPolicy,
      retryPolicy: input.outboxRetryPolicy,
    },
    resources: input.heartbeat.resources,
    security,
    policy,
    components,
    evidenceRefs: input.evidenceRefs ?? [],
    runtimeEnabled: false,
    productionDeliveryAllowed: false,
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };
}

export function validateEdgeHealthSnapshotContract(
  snapshot: EdgeHealthSnapshotContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!snapshot.snapshotId.trim()) reasons.push('snapshotId is required');
  if (!snapshot.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!snapshot.generatedAt.trim()) reasons.push('generatedAt is required');

  if (!snapshot.heartbeat.heartbeatId.trim()) reasons.push('heartbeat.heartbeatId is required');

  if (!Number.isInteger(snapshot.heartbeat.sequenceNumber) || snapshot.heartbeat.sequenceNumber < 0) {
    reasons.push('heartbeat.sequenceNumber must be a non-negative integer');
  }

  if (snapshot.outbox.depth < 0) reasons.push('outbox.depth must not be negative');
  if (snapshot.outbox.oldestAgeMs < 0) reasons.push('outbox.oldestAgeMs must not be negative');
  if (snapshot.outbox.retryPendingCount < 0) reasons.push('outbox.retryPendingCount must not be negative');
  if (snapshot.outbox.replayRequestedCount < 0) reasons.push('outbox.replayRequestedCount must not be negative');
  if (snapshot.outbox.ackPendingCount < 0) reasons.push('outbox.ackPendingCount must not be negative');
  if (snapshot.outbox.localDlqCount < 0) reasons.push('outbox.localDlqCount must not be negative');

  if (snapshot.security.secretMaterialStored !== false) {
    reasons.push('secretMaterialStored must remain false');
  }

  if (snapshot.security.writebackAllowed !== false) {
    reasons.push('security.writebackAllowed must remain false');
  }

  if (snapshot.security.directDbAccessAllowed !== false) {
    reasons.push('security.directDbAccessAllowed must remain false');
  }

  if (snapshot.policy.runtimeEnabled !== false) reasons.push('policy.runtimeEnabled must remain false');
  if (snapshot.policy.productionDeliveryAllowed !== false) {
    reasons.push('policy.productionDeliveryAllowed must remain false');
  }
  if (snapshot.policy.writebackProhibited !== true) reasons.push('policy.writebackProhibited must remain true');

  if (snapshot.runtimeEnabled !== false) reasons.push('runtimeEnabled must remain false');
  if (snapshot.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }
  if (snapshot.writebackAllowed !== false) reasons.push('writebackAllowed must remain false');
  if (snapshot.directDbAccessAllowed !== false) reasons.push('directDbAccessAllowed must remain false');

  return reasons;
}
