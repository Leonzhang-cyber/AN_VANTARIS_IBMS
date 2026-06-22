/**
 * LINK-C4-02B — EDGE-LINK reliability contract.
 *
 * LINK-owned contract for EDGE-to-LINK loss, duplicate, gap, disconnect,
 * reconnect, and replay semantics.
 *
 * This contract aligns with EDGE-C8 outbox reliability concepts.
 * It does not enable production delivery.
 */

export type EdgeLinkIngressAckReliabilityStatus =
  | 'RECEIVED'
  | 'VALIDATED'
  | 'QUEUED'
  | 'REJECTED'
  | 'BLOCKED'
  | 'DUPLICATE'
  | 'GAP_DETECTED'
  | 'REPLAY_REQUESTED';

export type EdgeLinkReplayReason =
  | 'SEQUENCE_GAP'
  | 'LINK_RECOVERY'
  | 'EDGE_RECONNECT'
  | 'ACK_LOST'
  | 'OPERATOR_REQUESTED'
  | 'UNKNOWN';

export interface EdgeLinkStreamIdentity {
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly streamId: string;
  readonly tenantId?: string;
  readonly siteId?: string;
}

export interface EdgeLinkSequenceRef {
  readonly stream: EdgeLinkStreamIdentity;
  readonly sequenceNumber: number;
  readonly eventId: string;
  readonly traceId: string;
  readonly payloadHash: string;
  readonly occurredAt: string;
}

export interface EdgeLinkReplayWindow {
  readonly gatewayId: string;
  readonly streamId: string;
  readonly fromSequence: number;
  readonly toSequence: number;
  readonly maxRecords: number;
  readonly reason: EdgeLinkReplayReason;
}

export interface EdgeLinkGapRange {
  readonly gatewayId: string;
  readonly streamId: string;
  readonly fromSequence: number;
  readonly toSequence: number;
  readonly detectedAt: string;
}

export interface EdgeLinkIngressLedgerSnapshot {
  readonly gatewayId: string;
  readonly streamId: string;
  readonly lastAcceptedSequence: number | null;
  readonly seenEventIds: readonly string[];
  readonly seenPayloadHashes: readonly string[];
  readonly duplicateCount: number;
  readonly gapRanges: readonly EdgeLinkGapRange[];
  readonly lastAckedAt?: string;
}

export interface EdgeLinkReliabilityAck {
  readonly ackId: string;
  readonly status: EdgeLinkIngressAckReliabilityStatus;
  readonly gatewayId: string;
  readonly streamId: string;
  readonly sequenceNumber: number;
  readonly eventId: string;
  readonly traceId: string;
  readonly payloadHash: string;
  readonly acknowledgedAt: string;
  readonly duplicate: boolean;
  readonly gapDetected: boolean;
  readonly replayWindow?: EdgeLinkReplayWindow;
  readonly reason?: string;
}

export function createEdgeLinkReliabilityKey(ref: EdgeLinkSequenceRef): string {
  return [
    ref.stream.gatewayId,
    ref.stream.streamId,
    String(ref.sequenceNumber),
    ref.eventId,
    ref.payloadHash,
  ].join(':');
}

export function isDuplicateSequence(
  ledger: EdgeLinkIngressLedgerSnapshot,
  ref: EdgeLinkSequenceRef,
): boolean {
  return (
    ledger.seenEventIds.includes(ref.eventId) ||
    ledger.seenPayloadHashes.includes(ref.payloadHash) ||
    (ledger.lastAcceptedSequence !== null && ref.sequenceNumber <= ledger.lastAcceptedSequence)
  );
}

export function detectSequenceGap(
  ledger: EdgeLinkIngressLedgerSnapshot,
  ref: EdgeLinkSequenceRef,
  detectedAt = new Date().toISOString(),
): EdgeLinkGapRange | null {
  if (ledger.lastAcceptedSequence === null) {
    return null;
  }

  const expectedNext = ledger.lastAcceptedSequence + 1;
  if (ref.sequenceNumber <= expectedNext) {
    return null;
  }

  return {
    gatewayId: ref.stream.gatewayId,
    streamId: ref.stream.streamId,
    fromSequence: expectedNext,
    toSequence: ref.sequenceNumber - 1,
    detectedAt,
  };
}

export function createReplayWindowFromGap(
  gap: EdgeLinkGapRange,
  maxRecords = 1000,
  reason: EdgeLinkReplayReason = 'SEQUENCE_GAP',
): EdgeLinkReplayWindow {
  return {
    gatewayId: gap.gatewayId,
    streamId: gap.streamId,
    fromSequence: gap.fromSequence,
    toSequence: gap.toSequence,
    maxRecords,
    reason,
  };
}

export function createEdgeLinkReliabilityAck(input: {
  readonly ref: EdgeLinkSequenceRef;
  readonly status: EdgeLinkIngressAckReliabilityStatus;
  readonly acknowledgedAt?: string;
  readonly duplicate?: boolean;
  readonly gapDetected?: boolean;
  readonly replayWindow?: EdgeLinkReplayWindow;
  readonly reason?: string;
}): EdgeLinkReliabilityAck {
  return {
    ackId: `edge-link-ack-${input.ref.stream.gatewayId}-${input.ref.stream.streamId}-${input.ref.sequenceNumber}`,
    status: input.status,
    gatewayId: input.ref.stream.gatewayId,
    streamId: input.ref.stream.streamId,
    sequenceNumber: input.ref.sequenceNumber,
    eventId: input.ref.eventId,
    traceId: input.ref.traceId,
    payloadHash: input.ref.payloadHash,
    acknowledgedAt: input.acknowledgedAt ?? new Date().toISOString(),
    duplicate: input.duplicate ?? false,
    gapDetected: input.gapDetected ?? false,
    ...(input.replayWindow !== undefined ? { replayWindow: input.replayWindow } : {}),
    ...(input.reason !== undefined ? { reason: input.reason } : {}),
  };
}

export function validateEdgeLinkSequenceRef(ref: EdgeLinkSequenceRef): readonly string[] {
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

  if (!ref.occurredAt.trim()) {
    reasons.push('occurredAt is required');
  }

  return reasons;
}
