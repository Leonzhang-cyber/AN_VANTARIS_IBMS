/**
 * EDGE-C8-08 — EDGE heartbeat and LINK liveness contract.
 *
 * EDGE-owned contract for system heartbeat, gateway liveness, LINK
 * connectivity, outbox health, adapter/connector summary, resource status,
 * heartbeat ACK, and missed heartbeat tracking.
 *
 * This contract does not enable runtime, pilot, production, writeback, or direct
 * UFMS DB access.
 */

export type EdgeHeartbeatRuntimeStatus =
  | 'LOCKED'
  | 'DIAGNOSTIC'
  | 'MAINTENANCE'
  | 'DRY_RUN'
  | 'READY'
  | 'DEGRADED'
  | 'OFFLINE';

export type EdgeLinkConnectivityStatus =
  | 'UNKNOWN'
  | 'DISCONNECTED'
  | 'CONNECTING'
  | 'CONNECTED'
  | 'DEGRADED'
  | 'ACK_TIMEOUT'
  | 'REPLAY_REQUIRED'
  | 'BLOCKED';

export type EdgeGatewayLivenessStatus =
  | 'ONLINE'
  | 'DEGRADED'
  | 'OFFLINE'
  | 'LOCKED'
  | 'MAINTENANCE';

export type EdgeHeartbeatAckStatus =
  | 'NONE'
  | 'RECEIVED'
  | 'VALIDATED'
  | 'ACKED'
  | 'REJECTED'
  | 'BLOCKED'
  | 'DUPLICATE'
  | 'TIMEOUT';

export interface EdgeHeartbeatIdentity {
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly heartbeatId: string;
  readonly streamId: 'health';
  readonly sequenceNumber: number;
}

export interface EdgeHeartbeatProductionState {
  readonly runtimeEnabled: boolean;
  readonly pilotApproved: boolean;
  readonly productionApproved: boolean;
  readonly writebackProhibited: boolean;
  readonly productionDeliveryAllowed: boolean;
}

export interface EdgeHeartbeatOutboxSummary {
  readonly outboxDepth: number;
  readonly outboxOldestAgeMs: number;
  readonly retryPendingCount: number;
  readonly replayRequestedCount: number;
  readonly ackPendingCount: number;
  readonly localDlqCount: number;
}

export interface EdgeHeartbeatAdapterSummary {
  readonly totalAdapters: number;
  readonly healthyAdapters: number;
  readonly degradedAdapters: number;
  readonly offlineAdapters: number;
  readonly lastAdapterErrorAt?: string;
}

export interface EdgeHeartbeatConnectorSummary {
  readonly totalConnectors: number;
  readonly healthyConnectors: number;
  readonly degradedConnectors: number;
  readonly offlineConnectors: number;
  readonly lastConnectorErrorAt?: string;
}

export interface EdgeHeartbeatResourceSummary {
  readonly diskFreeBytes?: number;
  readonly diskTotalBytes?: number;
  readonly memoryUsedBytes?: number;
  readonly memoryTotalBytes?: number;
  readonly cpuLoadPercent?: number;
}

export interface EdgeHeartbeatTimingSummary {
  readonly heartbeatIntervalMs: number;
  readonly generatedAt: string;
  readonly lastSuccessfulAckAt?: string;
  readonly missedAckCount: number;
  readonly consecutiveMissedHeartbeatCount: number;
}

export interface EdgeHeartbeatContract {
  readonly identity: EdgeHeartbeatIdentity;
  readonly runtimeStatus: EdgeHeartbeatRuntimeStatus;
  readonly linkConnectivityStatus: EdgeLinkConnectivityStatus;
  readonly livenessStatus: EdgeGatewayLivenessStatus;
  readonly productionState: EdgeHeartbeatProductionState;
  readonly outbox: EdgeHeartbeatOutboxSummary;
  readonly adapters: EdgeHeartbeatAdapterSummary;
  readonly connectors: EdgeHeartbeatConnectorSummary;
  readonly resources: EdgeHeartbeatResourceSummary;
  readonly timing: EdgeHeartbeatTimingSummary;
  readonly evidenceRefs: readonly string[];
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export interface EdgeHeartbeatAckContract {
  readonly ackId: string;
  readonly heartbeatId: string;
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly streamId: 'health';
  readonly sequenceNumber: number;
  readonly status: EdgeHeartbeatAckStatus;
  readonly acknowledgedAt: string;
  readonly reason?: string;
  readonly missedHeartbeatCountAfterAck: number;
}

export interface EdgeHeartbeatLivenessDecision {
  readonly livenessStatus: EdgeGatewayLivenessStatus;
  readonly linkConnectivityStatus: EdgeLinkConnectivityStatus;
  readonly reason: string;
  readonly missedAckCount: number;
  readonly consecutiveMissedHeartbeatCount: number;
  readonly offlineThresholdReached: boolean;
}

export function createDefaultEdgeHeartbeatProductionState(): EdgeHeartbeatProductionState {
  return {
    runtimeEnabled: false,
    pilotApproved: false,
    productionApproved: false,
    writebackProhibited: true,
    productionDeliveryAllowed: false,
  };
}

export function createEdgeHeartbeatId(input: {
  readonly gatewayId: string;
  readonly sequenceNumber: number;
}): string {
  return `edge-heartbeat-${input.gatewayId}-${input.sequenceNumber}`;
}

export function createEdgeHeartbeatAckId(input: {
  readonly gatewayId: string;
  readonly sequenceNumber: number;
}): string {
  return `edge-heartbeat-ack-${input.gatewayId}-${input.sequenceNumber}`;
}

export function createDefaultEdgeHeartbeatContract(input: {
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly sequenceNumber: number;
  readonly generatedAt: string;
  readonly heartbeatIntervalMs?: number;
}): EdgeHeartbeatContract {
  const heartbeatId = createEdgeHeartbeatId({
    gatewayId: input.gatewayId,
    sequenceNumber: input.sequenceNumber,
  });

  return {
    identity: {
      gatewayId: input.gatewayId,
      ...(input.edgeId !== undefined ? { edgeId: input.edgeId } : {}),
      ...(input.tenantId !== undefined ? { tenantId: input.tenantId } : {}),
      ...(input.siteId !== undefined ? { siteId: input.siteId } : {}),
      heartbeatId,
      streamId: 'health',
      sequenceNumber: input.sequenceNumber,
    },
    runtimeStatus: 'LOCKED',
    linkConnectivityStatus: 'UNKNOWN',
    livenessStatus: 'LOCKED',
    productionState: createDefaultEdgeHeartbeatProductionState(),
    outbox: {
      outboxDepth: 0,
      outboxOldestAgeMs: 0,
      retryPendingCount: 0,
      replayRequestedCount: 0,
      ackPendingCount: 0,
      localDlqCount: 0,
    },
    adapters: {
      totalAdapters: 0,
      healthyAdapters: 0,
      degradedAdapters: 0,
      offlineAdapters: 0,
    },
    connectors: {
      totalConnectors: 0,
      healthyConnectors: 0,
      degradedConnectors: 0,
      offlineConnectors: 0,
    },
    resources: {},
    timing: {
      heartbeatIntervalMs: input.heartbeatIntervalMs ?? 30000,
      generatedAt: input.generatedAt,
      missedAckCount: 0,
      consecutiveMissedHeartbeatCount: 0,
    },
    evidenceRefs: [],
    runtimeEnabled: false,
    productionDeliveryAllowed: false,
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };
}

export function createEdgeHeartbeatAck(input: {
  readonly heartbeat: EdgeHeartbeatContract;
  readonly status: EdgeHeartbeatAckStatus;
  readonly acknowledgedAt: string;
  readonly reason?: string;
  readonly missedHeartbeatCountAfterAck?: number;
}): EdgeHeartbeatAckContract {
  return {
    ackId: createEdgeHeartbeatAckId({
      gatewayId: input.heartbeat.identity.gatewayId,
      sequenceNumber: input.heartbeat.identity.sequenceNumber,
    }),
    heartbeatId: input.heartbeat.identity.heartbeatId,
    gatewayId: input.heartbeat.identity.gatewayId,
    ...(input.heartbeat.identity.edgeId !== undefined ? { edgeId: input.heartbeat.identity.edgeId } : {}),
    streamId: 'health',
    sequenceNumber: input.heartbeat.identity.sequenceNumber,
    status: input.status,
    acknowledgedAt: input.acknowledgedAt,
    ...(input.reason !== undefined ? { reason: input.reason } : {}),
    missedHeartbeatCountAfterAck: input.missedHeartbeatCountAfterAck ?? 0,
  };
}

export function evaluateHeartbeatLiveness(input: {
  readonly missedAckCount: number;
  readonly consecutiveMissedHeartbeatCount: number;
  readonly degradedThreshold?: number;
  readonly offlineThreshold?: number;
}): EdgeHeartbeatLivenessDecision {
  const degradedThreshold = input.degradedThreshold ?? 2;
  const offlineThreshold = input.offlineThreshold ?? 5;

  if (input.consecutiveMissedHeartbeatCount >= offlineThreshold) {
    return {
      livenessStatus: 'OFFLINE',
      linkConnectivityStatus: 'ACK_TIMEOUT',
      reason: 'heartbeat offline threshold reached',
      missedAckCount: input.missedAckCount,
      consecutiveMissedHeartbeatCount: input.consecutiveMissedHeartbeatCount,
      offlineThresholdReached: true,
    };
  }

  if (input.consecutiveMissedHeartbeatCount >= degradedThreshold) {
    return {
      livenessStatus: 'DEGRADED',
      linkConnectivityStatus: 'DEGRADED',
      reason: 'heartbeat degraded threshold reached',
      missedAckCount: input.missedAckCount,
      consecutiveMissedHeartbeatCount: input.consecutiveMissedHeartbeatCount,
      offlineThresholdReached: false,
    };
  }

  return {
    livenessStatus: 'ONLINE',
    linkConnectivityStatus: 'CONNECTED',
    reason: 'heartbeat within threshold',
    missedAckCount: input.missedAckCount,
    consecutiveMissedHeartbeatCount: input.consecutiveMissedHeartbeatCount,
    offlineThresholdReached: false,
  };
}

export function validateEdgeHeartbeatContract(
  heartbeat: EdgeHeartbeatContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!heartbeat.identity.gatewayId.trim()) reasons.push('identity.gatewayId is required');
  if (!heartbeat.identity.heartbeatId.trim()) reasons.push('identity.heartbeatId is required');
  if (heartbeat.identity.streamId !== 'health') reasons.push('identity.streamId must be health');

  if (!Number.isInteger(heartbeat.identity.sequenceNumber) || heartbeat.identity.sequenceNumber < 0) {
    reasons.push('identity.sequenceNumber must be a non-negative integer');
  }

  if (heartbeat.productionState.writebackProhibited !== true) {
    reasons.push('writeback must remain prohibited');
  }

  if (heartbeat.productionState.productionDeliveryAllowed !== false) {
    reasons.push('production delivery must remain false');
  }

  if (heartbeat.runtimeEnabled !== false) reasons.push('runtimeEnabled must remain false');
  if (heartbeat.productionDeliveryAllowed !== false) reasons.push('productionDeliveryAllowed must remain false');
  if (heartbeat.writebackAllowed !== false) reasons.push('writebackAllowed must remain false');
  if (heartbeat.directDbAccessAllowed !== false) reasons.push('directDbAccessAllowed must remain false');

  if (heartbeat.outbox.outboxDepth < 0) reasons.push('outboxDepth must not be negative');
  if (heartbeat.outbox.retryPendingCount < 0) reasons.push('retryPendingCount must not be negative');
  if (heartbeat.outbox.localDlqCount < 0) reasons.push('localDlqCount must not be negative');

  if (!Number.isInteger(heartbeat.timing.heartbeatIntervalMs) || heartbeat.timing.heartbeatIntervalMs < 1) {
    reasons.push('heartbeatIntervalMs must be greater than zero');
  }

  if (!heartbeat.timing.generatedAt.trim()) reasons.push('timing.generatedAt is required');

  return reasons;
}

export function validateEdgeHeartbeatAckContract(
  ack: EdgeHeartbeatAckContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!ack.ackId.trim()) reasons.push('ackId is required');
  if (!ack.heartbeatId.trim()) reasons.push('heartbeatId is required');
  if (!ack.gatewayId.trim()) reasons.push('gatewayId is required');
  if (ack.streamId !== 'health') reasons.push('streamId must be health');

  if (!Number.isInteger(ack.sequenceNumber) || ack.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }

  if (!ack.acknowledgedAt.trim()) reasons.push('acknowledgedAt is required');

  if (!Number.isInteger(ack.missedHeartbeatCountAfterAck) || ack.missedHeartbeatCountAfterAck < 0) {
    reasons.push('missedHeartbeatCountAfterAck must be a non-negative integer');
  }

  return reasons;
}
