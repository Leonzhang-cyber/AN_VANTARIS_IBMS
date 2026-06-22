/**
 * LINK-C2-03 — ingress ACK lifecycle contract.
 *
 * This LINK-owned contract defines ingress and validation phase ACK semantics.
 * It does not enable production delivery.
 */

import type {
  EdgeHandoffIntakeContract,
  EdgeHandoffIntakeValidationResult,
} from './edge-handoff-intake-contract.js';
import type {
  EdgeProductionStateGuardCode,
  EdgeProductionStateGuardResult,
} from './edge-production-state-guard.js';

export type LinkIngressAckStatus =
  | 'RECEIVED'
  | 'VALIDATED'
  | 'QUEUED'
  | 'REJECTED'
  | 'BLOCKED'
  | 'DLQ';

export type LinkIngressAckReasonCode =
  | 'LINK_INGRESS_RECEIVED'
  | 'LINK_INGRESS_VALIDATED'
  | 'LINK_INGRESS_QUEUED'
  | 'LINK_INGRESS_REJECTED'
  | 'LINK_INGRESS_BLOCKED'
  | 'LINK_INGRESS_DLQ'
  | 'LINK_SCHEMA_INVALID'
  | 'LINK_SECURITY_REJECTED'
  | 'LINK_EDGE_PRODUCTION_BLOCKED'
  | 'LINK_QUEUE_BACKPRESSURE'
  | EdgeProductionStateGuardCode;

export interface LinkIngressAck {
  readonly ackId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly status: LinkIngressAckStatus;
  readonly reasonCode: LinkIngressAckReasonCode;
  readonly reason: string;
  readonly acknowledgedAt: string;
  readonly queueId?: string;
  readonly partition?: number;
  readonly validationReasons?: readonly string[];
}

export interface CreateLinkIngressAckInput {
  readonly intake: EdgeHandoffIntakeContract;
  readonly status: LinkIngressAckStatus;
  readonly reasonCode: LinkIngressAckReasonCode;
  readonly reason: string;
  readonly acknowledgedAt?: string;
  readonly queueId?: string;
  readonly partition?: number;
  readonly validationReasons?: readonly string[];
}

export function createLinkIngressAck(input: CreateLinkIngressAckInput): LinkIngressAck {
  return {
    ackId: `link-ingress-ack-${input.intake.eventId}`,
    eventId: input.intake.eventId,
    traceId: input.intake.traceId,
    gatewayId: input.intake.source.gatewayId,
    status: input.status,
    reasonCode: input.reasonCode,
    reason: input.reason,
    acknowledgedAt: input.acknowledgedAt ?? new Date().toISOString(),
    ...(input.queueId !== undefined ? { queueId: input.queueId } : {}),
    ...(input.partition !== undefined ? { partition: input.partition } : {}),
    ...(input.validationReasons !== undefined
      ? { validationReasons: input.validationReasons }
      : {}),
  };
}

export function createValidationAck(
  intake: EdgeHandoffIntakeContract,
  validation: EdgeHandoffIntakeValidationResult,
): LinkIngressAck {
  if (validation.valid) {
    return createLinkIngressAck({
      intake,
      status: 'VALIDATED',
      reasonCode: 'LINK_INGRESS_VALIDATED',
      reason: 'LINK ingress contract validated',
    });
  }

  return createLinkIngressAck({
    intake,
    status: 'REJECTED',
    reasonCode: 'LINK_SCHEMA_INVALID',
    reason: 'LINK ingress contract validation failed',
    validationReasons: validation.reasons,
  });
}

export function createProductionBlockedAck(
  intake: EdgeHandoffIntakeContract,
  guard: EdgeProductionStateGuardResult,
): LinkIngressAck {
  return createLinkIngressAck({
    intake,
    status: 'BLOCKED',
    reasonCode: guard.code,
    reason: guard.reason,
  });
}

export function createQueuedAck(
  intake: EdgeHandoffIntakeContract,
  queueId: string,
  partition: number,
): LinkIngressAck {
  return createLinkIngressAck({
    intake,
    status: 'QUEUED',
    reasonCode: 'LINK_INGRESS_QUEUED',
    reason: 'LINK ingress event queued',
    queueId,
    partition,
  });
}
