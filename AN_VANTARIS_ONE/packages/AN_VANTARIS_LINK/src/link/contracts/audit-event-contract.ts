/**
 * LINK-C6-01 — Audit event contract.
 *
 * LINK-owned audit event model for ingress, queue, delivery, retry, DLQ,
 * replay, reliability, security, and policy stages.
 *
 * This contract does not enable production delivery.
 */

export type LinkAuditType =
  | 'INGRESS'
  | 'QUEUE'
  | 'DELIVERY'
  | 'RETRY'
  | 'DLQ'
  | 'REPLAY'
  | 'RELIABILITY'
  | 'SECURITY'
  | 'POLICY'
  | 'EVIDENCE';

export type LinkAuditSeverity = 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';

export type LinkAuditStage =
  | 'INGRESS_RECEIVED'
  | 'INGRESS_VALIDATED'
  | 'INGRESS_REJECTED'
  | 'QUEUE_ENQUEUED'
  | 'QUEUE_DURABLE_APPEND'
  | 'DELIVERY_DRY_RUN'
  | 'DELIVERY_BLOCKED'
  | 'DELIVERY_RECEIPT'
  | 'RETRY_DECISION'
  | 'DLQ_MOVED'
  | 'REPLAY_REQUESTED'
  | 'RELIABILITY_ACK'
  | 'SECURITY_REJECTED'
  | 'POLICY_BLOCKED'
  | 'EVIDENCE_CHAINED';

export type LinkAuditActorType =
  | 'EDGE_GATEWAY'
  | 'LINK_RUNTIME'
  | 'LINK_OPERATOR'
  | 'SYSTEM'
  | 'UNKNOWN';

export interface LinkAuditEvidenceRef {
  readonly evidenceId: string;
  readonly evidenceType:
    | 'ingress'
    | 'queue'
    | 'delivery'
    | 'retry'
    | 'dlq'
    | 'replay'
    | 'reliability'
    | 'security'
    | 'policy'
    | 'chain'
    | 'unknown';
  readonly sourcePath?: string;
  readonly hash?: string;
}

export interface LinkAuditEventContract {
  readonly auditId: string;
  readonly auditType: LinkAuditType;
  readonly severity: LinkAuditSeverity;
  readonly stage: LinkAuditStage;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId?: string;
  readonly sequenceNumber?: number;
  readonly queueId?: string;
  readonly deliveryId?: string;
  readonly dlqId?: string;
  readonly reasonCode?: string;
  readonly occurredAt: string;
  readonly recordedAt: string;
  readonly actorType: LinkAuditActorType;
  readonly evidenceRefs: readonly LinkAuditEvidenceRef[];
  readonly productionDeliveryAllowed: false;
}

export interface CreateLinkAuditEventInput {
  readonly auditType: LinkAuditType;
  readonly severity: LinkAuditSeverity;
  readonly stage: LinkAuditStage;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId?: string;
  readonly sequenceNumber?: number;
  readonly queueId?: string;
  readonly deliveryId?: string;
  readonly dlqId?: string;
  readonly reasonCode?: string;
  readonly occurredAt: string;
  readonly recordedAt?: string;
  readonly actorType?: LinkAuditActorType;
  readonly evidenceRefs?: readonly LinkAuditEvidenceRef[];
}

export function createLinkAuditId(input: {
  readonly stage: LinkAuditStage;
  readonly eventId: string;
  readonly traceId: string;
}): string {
  return `link-audit-${input.stage}-${input.eventId}-${input.traceId}`;
}

export function createLinkAuditEvent(
  input: CreateLinkAuditEventInput,
): LinkAuditEventContract {
  return {
    auditId: createLinkAuditId({
      stage: input.stage,
      eventId: input.eventId,
      traceId: input.traceId,
    }),
    auditType: input.auditType,
    severity: input.severity,
    stage: input.stage,
    eventId: input.eventId,
    traceId: input.traceId,
    gatewayId: input.gatewayId,
    ...(input.streamId !== undefined ? { streamId: input.streamId } : {}),
    ...(input.sequenceNumber !== undefined ? { sequenceNumber: input.sequenceNumber } : {}),
    ...(input.queueId !== undefined ? { queueId: input.queueId } : {}),
    ...(input.deliveryId !== undefined ? { deliveryId: input.deliveryId } : {}),
    ...(input.dlqId !== undefined ? { dlqId: input.dlqId } : {}),
    ...(input.reasonCode !== undefined ? { reasonCode: input.reasonCode } : {}),
    occurredAt: input.occurredAt,
    recordedAt: input.recordedAt ?? new Date().toISOString(),
    actorType: input.actorType ?? 'LINK_RUNTIME',
    evidenceRefs: input.evidenceRefs ?? [],
    productionDeliveryAllowed: false,
  };
}

export function validateLinkAuditEventContract(
  audit: LinkAuditEventContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!audit.auditId.trim()) reasons.push('auditId is required');
  if (!audit.eventId.trim()) reasons.push('eventId is required');
  if (!audit.traceId.trim()) reasons.push('traceId is required');
  if (!audit.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!audit.occurredAt.trim()) reasons.push('occurredAt is required');
  if (!audit.recordedAt.trim()) reasons.push('recordedAt is required');

  if (
    audit.sequenceNumber !== undefined &&
    (!Number.isInteger(audit.sequenceNumber) || audit.sequenceNumber < 0)
  ) {
    reasons.push('sequenceNumber must be a non-negative integer');
  }

  if (audit.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }

  return reasons;
}
