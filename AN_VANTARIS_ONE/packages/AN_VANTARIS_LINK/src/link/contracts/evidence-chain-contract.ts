/**
 * LINK-C6-02 — Evidence chain contract.
 *
 * LINK-owned evidence chain model connecting audit events across ingress,
 * queue, delivery, retry, DLQ, replay, and reliability stages.
 *
 * This contract does not enable production delivery.
 */

import type { LinkAuditEventContract } from './audit-event-contract.js';

export type LinkEvidenceRecordType =
  | 'INGRESS_RECEIVED'
  | 'INGRESS_VALIDATED'
  | 'QUEUE_ENQUEUED'
  | 'QUEUE_DURABLE_APPEND'
  | 'DELIVERY_DRY_RUN'
  | 'DELIVERY_BLOCKED'
  | 'RETRY_DECISION'
  | 'DLQ_MOVED'
  | 'REPLAY_REQUESTED'
  | 'RELIABILITY_ACK'
  | 'SECURITY_REJECTED'
  | 'POLICY_BLOCKED';

export interface LinkEvidenceChainRecord {
  readonly recordId: string;
  readonly recordType: LinkEvidenceRecordType;
  readonly auditId: string;
  readonly eventId: string;
  readonly traceId: string;
  readonly gatewayId: string;
  readonly streamId?: string;
  readonly sequenceNumber?: number;
  readonly queueId?: string;
  readonly deliveryId?: string;
  readonly dlqId?: string;
  readonly reasonCode?: string;
  readonly recordedAt: string;
  readonly previousHash: string | null;
  readonly currentHash: string;
}

export interface LinkEvidenceChainContract {
  readonly evidenceChainId: string;
  readonly traceId: string;
  readonly eventId: string;
  readonly gatewayId: string;
  readonly streamId?: string;
  readonly sequenceNumber?: number;
  readonly records: readonly LinkEvidenceChainRecord[];
  readonly previousHash: string | null;
  readonly currentHash: string;
  readonly chainComplete: boolean;
  readonly productionDeliveryAllowed: false;
}

export function createDeterministicEvidenceHash(input: string): string {
  let hash = 2166136261;

  for (let index = 0; index < input.length; index += 1) {
    hash ^= input.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

export function createEvidenceChainId(input: {
  readonly traceId: string;
  readonly eventId: string;
  readonly gatewayId: string;
}): string {
  return `link-evidence-chain-${input.gatewayId}-${input.eventId}-${input.traceId}`;
}

export function mapAuditStageToEvidenceRecordType(
  stage: LinkAuditEventContract['stage'],
): LinkEvidenceRecordType {
  switch (stage) {
    case 'INGRESS_RECEIVED':
      return 'INGRESS_RECEIVED';
    case 'INGRESS_VALIDATED':
      return 'INGRESS_VALIDATED';
    case 'QUEUE_ENQUEUED':
      return 'QUEUE_ENQUEUED';
    case 'QUEUE_DURABLE_APPEND':
      return 'QUEUE_DURABLE_APPEND';
    case 'DELIVERY_DRY_RUN':
      return 'DELIVERY_DRY_RUN';
    case 'DELIVERY_BLOCKED':
      return 'DELIVERY_BLOCKED';
    case 'RETRY_DECISION':
      return 'RETRY_DECISION';
    case 'DLQ_MOVED':
      return 'DLQ_MOVED';
    case 'REPLAY_REQUESTED':
      return 'REPLAY_REQUESTED';
    case 'RELIABILITY_ACK':
      return 'RELIABILITY_ACK';
    case 'SECURITY_REJECTED':
      return 'SECURITY_REJECTED';
    case 'POLICY_BLOCKED':
      return 'POLICY_BLOCKED';
    case 'DELIVERY_RECEIPT':
      return 'DELIVERY_DRY_RUN';
    case 'EVIDENCE_CHAINED':
      return 'RELIABILITY_ACK';
    case 'INGRESS_REJECTED':
      return 'SECURITY_REJECTED';
  }
}

export function createEvidenceRecordFromAudit(input: {
  readonly audit: LinkAuditEventContract;
  readonly previousHash: string | null;
}): LinkEvidenceChainRecord {
  const recordType = mapAuditStageToEvidenceRecordType(input.audit.stage);
  const recordId = `link-evidence-record-${input.audit.auditId}`;
  const hashInput = [
    recordId,
    recordType,
    input.audit.auditId,
    input.audit.eventId,
    input.audit.traceId,
    input.audit.gatewayId,
    input.audit.streamId ?? '',
    input.audit.sequenceNumber ?? '',
    input.audit.queueId ?? '',
    input.audit.deliveryId ?? '',
    input.audit.dlqId ?? '',
    input.audit.reasonCode ?? '',
    input.audit.recordedAt,
    input.previousHash ?? '',
  ].join('|');

  const currentHash = createDeterministicEvidenceHash(hashInput);

  return {
    recordId,
    recordType,
    auditId: input.audit.auditId,
    eventId: input.audit.eventId,
    traceId: input.audit.traceId,
    gatewayId: input.audit.gatewayId,
    ...(input.audit.streamId !== undefined ? { streamId: input.audit.streamId } : {}),
    ...(input.audit.sequenceNumber !== undefined ? { sequenceNumber: input.audit.sequenceNumber } : {}),
    ...(input.audit.queueId !== undefined ? { queueId: input.audit.queueId } : {}),
    ...(input.audit.deliveryId !== undefined ? { deliveryId: input.audit.deliveryId } : {}),
    ...(input.audit.dlqId !== undefined ? { dlqId: input.audit.dlqId } : {}),
    ...(input.audit.reasonCode !== undefined ? { reasonCode: input.audit.reasonCode } : {}),
    recordedAt: input.audit.recordedAt,
    previousHash: input.previousHash,
    currentHash,
  };
}

export function createEvidenceChainFromAudits(input: {
  readonly audits: readonly LinkAuditEventContract[];
  readonly chainComplete?: boolean;
}): LinkEvidenceChainContract {
  if (input.audits.length === 0) {
    throw new Error('at least one audit event is required');
  }

  const records: LinkEvidenceChainRecord[] = [];
  let previousHash: string | null = null;

  for (const audit of input.audits) {
    const record = createEvidenceRecordFromAudit({
      audit,
      previousHash,
    });
    records.push(record);
    previousHash = record.currentHash;
  }

  const first = input.audits[0];
  const currentHash = records[records.length - 1]?.currentHash ?? createDeterministicEvidenceHash('empty');

  return {
    evidenceChainId: createEvidenceChainId({
      traceId: first.traceId,
      eventId: first.eventId,
      gatewayId: first.gatewayId,
    }),
    traceId: first.traceId,
    eventId: first.eventId,
    gatewayId: first.gatewayId,
    ...(first.streamId !== undefined ? { streamId: first.streamId } : {}),
    ...(first.sequenceNumber !== undefined ? { sequenceNumber: first.sequenceNumber } : {}),
    records,
    previousHash: records[0]?.previousHash ?? null,
    currentHash,
    chainComplete: input.chainComplete ?? false,
    productionDeliveryAllowed: false,
  };
}

export function validateEvidenceChainContract(
  chain: LinkEvidenceChainContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!chain.evidenceChainId.trim()) reasons.push('evidenceChainId is required');
  if (!chain.traceId.trim()) reasons.push('traceId is required');
  if (!chain.eventId.trim()) reasons.push('eventId is required');
  if (!chain.gatewayId.trim()) reasons.push('gatewayId is required');
  if (chain.records.length === 0) reasons.push('records are required');

  let expectedPreviousHash: string | null = null;

  for (const record of chain.records) {
    if (!record.recordId.trim()) reasons.push('recordId is required');
    if (!record.auditId.trim()) reasons.push('auditId is required');
    if (!record.currentHash.trim()) reasons.push('currentHash is required');

    if (record.previousHash !== expectedPreviousHash) {
      reasons.push('evidence chain previousHash mismatch');
    }

    expectedPreviousHash = record.currentHash;
  }

  if (chain.currentHash !== expectedPreviousHash) {
    reasons.push('chain currentHash must match final record hash');
  }

  if (chain.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }

  return reasons;
}
