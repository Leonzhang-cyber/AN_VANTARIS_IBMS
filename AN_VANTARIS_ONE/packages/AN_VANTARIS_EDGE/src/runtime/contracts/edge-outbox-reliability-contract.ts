/**
 * EDGE-C8-05 — EDGE outbox reliability contract.
 *
 * EDGE-owned contract for reliable EDGE-to-LINK send, ACK tracking, retry,
 * replay, and disconnect recovery.
 *
 * This contract does not enable runtime, pilot, production, writeback, or direct
 * UFMS DB access.
 */

import type {
  EdgeStableSuppressionDecision,
  EdgeStableValueIdentity,
} from './stable-value-suppression-contract.js';

export type EdgeOutboxState =
  | 'PENDING_SEND'
  | 'SENT_WAITING_ACK'
  | 'ACKED'
  | 'RETRY_PENDING'
  | 'REPLAY_REQUESTED'
  | 'DROPPED_EXPIRED'
  | 'REJECTED_FINAL';

export type EdgeOutboxAckStatus =
  | 'NONE'
  | 'RECEIVED'
  | 'VALIDATED'
  | 'QUEUED'
  | 'REJECTED'
  | 'BLOCKED'
  | 'DUPLICATE'
  | 'GAP_DETECTED'
  | 'REPLAY_REQUESTED';

export type EdgeOutboxReplayReason =
  | 'SEQUENCE_GAP'
  | 'LINK_RECOVERY'
  | 'EDGE_RECONNECT'
  | 'ACK_LOST'
  | 'OPERATOR_REQUESTED'
  | 'UNKNOWN';

export type EdgeOutboxDropPolicy =
  | 'DROP_OLDEST_LOW_PRIORITY'
  | 'DROP_TELEMETRY_FIRST'
  | 'BLOCK_NEW_LOW_PRIORITY'
  | 'REJECT_NEW_WHEN_FULL'
  | 'PRESERVE_ALARM_EVENT_HEALTH';

export type EdgeOutboxRecordPriority = 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';

export interface EdgeOutboxStreamIdentity {
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly streamId: string;
  readonly tenantId?: string;
  readonly siteId?: string;
}

export interface EdgeOutboxSequenceRef {
  readonly stream: EdgeOutboxStreamIdentity;
  readonly sequenceNumber: number;
  readonly eventId: string;
  readonly traceId: string;
  readonly payloadHash: string;
  readonly recordType: string;
  readonly occurredAt: string;
}

export interface EdgeOutboxRetryPolicy {
  readonly maxAttempts: number;
  readonly initialDelayMs: number;
  readonly maxDelayMs: number;
  readonly jitterMs: number;
  readonly maxInFlight: number;
  readonly batchSize: number;
  readonly retryBudget: number;
  readonly replayBudget: number;
}

export interface EdgeOutboxCapacityPolicy {
  readonly maxOutboxRecords: number;
  readonly maxOutboxBytes: number;
  readonly recordTtlMs: number;
  readonly dropPolicy: EdgeOutboxDropPolicy;
  readonly preserveAlarmEventHealth: boolean;
  readonly allowTelemetryAggregation: boolean;
}

export interface EdgeOutboxReplayRequest {
  readonly requestId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly fromSequence: number;
  readonly toSequence: number;
  readonly maxRecords: number;
  readonly reason: EdgeOutboxReplayReason;
  readonly requestedAt: string;
}

export interface EdgeOutboxAckRecord {
  readonly ackId: string;
  readonly status: EdgeOutboxAckStatus;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly eventId: string;
  readonly traceId: string;
  readonly payloadHash: string;
  readonly acknowledgedAt: string;
  readonly duplicate: boolean;
  readonly replayRequest?: EdgeOutboxReplayRequest;
  readonly reason?: string;
}

export interface EdgeOutboxItem {
  readonly outboxId: string;
  readonly sequence: EdgeOutboxSequenceRef;
  readonly priority: EdgeOutboxRecordPriority;
  readonly state: EdgeOutboxState;
  readonly payload: unknown;
  readonly payloadBytes: number;
  readonly createdAt: string;
  readonly lastSendAt?: string;
  readonly ackReceivedAt?: string;
  readonly attempts: number;
  readonly maxAttempts: number;
  readonly nextRetryAt?: string;
  readonly expiresAt: string;
  readonly ack: EdgeOutboxAckRecord;
  readonly stableSuppression?: EdgeStableSuppressionDecision;
}

export interface EdgeOutboxStateTransition {
  readonly outboxId: string;
  readonly from: EdgeOutboxState;
  readonly to: EdgeOutboxState;
  readonly reason:
    | 'CREATED'
    | 'SEND_ATTEMPTED'
    | 'ACK_RECEIVED'
    | 'ACK_LOST_TIMEOUT'
    | 'RETRY_SCHEDULED'
    | 'REPLAY_REQUESTED'
    | 'EXPIRED'
    | 'REJECTED_FINAL';
  readonly transitionedAt: string;
}

export function createEdgeOutboxStreamKey(stream: EdgeOutboxStreamIdentity): string {
  return [
    stream.tenantId ?? 'tenant-unknown',
    stream.siteId ?? 'site-unknown',
    stream.gatewayId,
    stream.edgeId ?? 'edge-unknown',
    stream.streamId,
  ].join(':');
}

export function createEdgeOutboxReliabilityKey(ref: EdgeOutboxSequenceRef): string {
  return [
    ref.stream.gatewayId,
    ref.stream.streamId,
    String(ref.sequenceNumber),
    ref.eventId,
    ref.payloadHash,
  ].join(':');
}

export function inferEdgeOutboxPriority(recordType: string): EdgeOutboxRecordPriority {
  if (recordType === 'alarm') {
    return 'CRITICAL';
  }

  if (recordType === 'event' || recordType === 'health') {
    return 'HIGH';
  }

  if (recordType === 'audit' || recordType === 'evidence' || recordType === 'config_version') {
    return 'NORMAL';
  }

  return 'NORMAL';
}

export function createDefaultEdgeOutboxRetryPolicy(): EdgeOutboxRetryPolicy {
  return {
    maxAttempts: 5,
    initialDelayMs: 500,
    maxDelayMs: 30000,
    jitterMs: 250,
    maxInFlight: 100,
    batchSize: 100,
    retryBudget: 1000,
    replayBudget: 1000,
  };
}

export function createDefaultEdgeOutboxCapacityPolicy(): EdgeOutboxCapacityPolicy {
  return {
    maxOutboxRecords: 100000,
    maxOutboxBytes: 512 * 1024 * 1024,
    recordTtlMs: 7 * 24 * 60 * 60 * 1000,
    dropPolicy: 'PRESERVE_ALARM_EVENT_HEALTH',
    preserveAlarmEventHealth: true,
    allowTelemetryAggregation: true,
  };
}

export function createEmptyEdgeOutboxAckRecord(
  ref: EdgeOutboxSequenceRef,
  acknowledgedAt = '',
): EdgeOutboxAckRecord {
  return {
    ackId: `edge-outbox-ack-${ref.stream.gatewayId}-${ref.stream.streamId}-${ref.sequenceNumber}`,
    status: 'NONE',
    gatewayId: ref.stream.gatewayId,
    streamId: ref.stream.streamId,
    sequenceNumber: ref.sequenceNumber,
    eventId: ref.eventId,
    traceId: ref.traceId,
    payloadHash: ref.payloadHash,
    acknowledgedAt,
    duplicate: false,
  };
}

export function createEdgeOutboxItem(input: {
  readonly sequence: EdgeOutboxSequenceRef;
  readonly payload: unknown;
  readonly payloadBytes: number;
  readonly createdAt: string;
  readonly expiresAt: string;
  readonly maxAttempts?: number;
  readonly stableSuppression?: EdgeStableSuppressionDecision;
}): EdgeOutboxItem {
  return {
    outboxId: `edge-outbox-${input.sequence.stream.gatewayId}-${input.sequence.stream.streamId}-${input.sequence.sequenceNumber}`,
    sequence: input.sequence,
    priority: inferEdgeOutboxPriority(input.sequence.recordType),
    state: 'PENDING_SEND',
    payload: input.payload,
    payloadBytes: input.payloadBytes,
    createdAt: input.createdAt,
    attempts: 0,
    maxAttempts: input.maxAttempts ?? createDefaultEdgeOutboxRetryPolicy().maxAttempts,
    expiresAt: input.expiresAt,
    ack: createEmptyEdgeOutboxAckRecord(input.sequence),
    ...(input.stableSuppression !== undefined ? { stableSuppression: input.stableSuppression } : {}),
  };
}

export function createEdgeOutboxReplayRequest(input: {
  readonly requestId: string;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly fromSequence: number;
  readonly toSequence: number;
  readonly maxRecords?: number;
  readonly reason: EdgeOutboxReplayReason;
  readonly requestedAt: string;
}): EdgeOutboxReplayRequest {
  return {
    requestId: input.requestId,
    gatewayId: input.gatewayId,
    streamId: input.streamId,
    fromSequence: input.fromSequence,
    toSequence: input.toSequence,
    maxRecords: input.maxRecords ?? 1000,
    reason: input.reason,
    requestedAt: input.requestedAt,
  };
}

export function createEdgeOutboxTransition(
  outboxId: string,
  from: EdgeOutboxState,
  to: EdgeOutboxState,
  reason: EdgeOutboxStateTransition['reason'],
  transitionedAt = new Date().toISOString(),
): EdgeOutboxStateTransition {
  return {
    outboxId,
    from,
    to,
    reason,
    transitionedAt,
  };
}

export function shouldRetryEdgeOutboxItem(item: EdgeOutboxItem): boolean {
  return (
    item.state === 'RETRY_PENDING' &&
    item.attempts < item.maxAttempts &&
    item.ack.status !== 'QUEUED' &&
    item.ack.status !== 'DUPLICATE' &&
    item.ack.status !== 'REJECTED'
  );
}

export function validateEdgeOutboxSequenceRef(ref: EdgeOutboxSequenceRef): readonly string[] {
  const reasons: string[] = [];

  if (!ref.stream.gatewayId.trim()) {
    reasons.push('stream.gatewayId is required');
  }

  if (!ref.stream.streamId.trim()) {
    reasons.push('stream.streamId is required');
  }

  if (!Number.isInteger(ref.sequenceNumber) || ref.sequenceNumber < 0) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }

  if (!ref.eventId.trim()) {
    reasons.push('eventId is required');
  }

  if (!ref.traceId.trim()) {
    reasons.push('traceId is required');
  }

  if (!ref.payloadHash.trim()) {
    reasons.push('payloadHash is required');
  }

  if (!ref.recordType.trim()) {
    reasons.push('recordType is required');
  }

  if (!ref.occurredAt.trim()) {
    reasons.push('occurredAt is required');
  }

  return reasons;
}

export function validateEdgeOutboxItem(item: EdgeOutboxItem): readonly string[] {
  const reasons: string[] = [];

  if (!item.outboxId.trim()) {
    reasons.push('outboxId is required');
  }

  reasons.push(...validateEdgeOutboxSequenceRef(item.sequence));

  if (!Number.isInteger(item.payloadBytes) || item.payloadBytes < 0) {
    reasons.push('payloadBytes must be a non-negative integer');
  }

  if (!item.createdAt.trim()) {
    reasons.push('createdAt is required');
  }

  if (!item.expiresAt.trim()) {
    reasons.push('expiresAt is required');
  }

  if (item.attempts < 0) {
    reasons.push('attempts must not be negative');
  }

  if (item.maxAttempts < 1) {
    reasons.push('maxAttempts must be greater than zero');
  }

  return reasons;
}

export function shouldCreateOutboxRecordFromStableDecision(
  decision: EdgeStableSuppressionDecision,
): boolean {
  return (
    decision.emit === true ||
    decision.changeReason !== 'SUPPRESSED_NO_CHANGE' ||
    decision.fullSnapshot === true ||
    decision.reconnectFirstSample === true ||
    decision.heartbeatDue === true
  );
}

export function createSequenceRefFromStableIdentity(input: {
  readonly identity: EdgeStableValueIdentity;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly eventId: string;
  readonly traceId: string;
  readonly payloadHash: string;
  readonly occurredAt: string;
}): EdgeOutboxSequenceRef {
  return {
    stream: {
      gatewayId: input.identity.gatewayId,
      ...(input.identity.edgeId !== undefined ? { edgeId: input.identity.edgeId } : {}),
      streamId: input.streamId,
      ...(input.identity.tenantId !== undefined ? { tenantId: input.identity.tenantId } : {}),
      ...(input.identity.siteId !== undefined ? { siteId: input.identity.siteId } : {}),
    },
    sequenceNumber: input.sequenceNumber,
    eventId: input.eventId,
    traceId: input.traceId,
    payloadHash: input.payloadHash,
    recordType: input.identity.recordType,
    occurredAt: input.occurredAt,
  };
}
