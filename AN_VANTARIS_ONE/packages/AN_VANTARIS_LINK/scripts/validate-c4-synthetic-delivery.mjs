import assert from 'node:assert/strict';

import {
  createDefaultBlockedEdgeProductionState,
} from '../dist-c4/src/link/contracts/edge-handoff-intake-contract.js';
import {
  createLinkQueueItemContract,
  createPartitionKeyFromIntake,
  validateLinkQueueItemContract,
} from '../dist-c4/src/link/contracts/queue-item-contract.js';
import {
  assignPartitionId,
} from '../dist-c4/src/link/contracts/partition-priority-contract.js';
import {
  createSyntheticDryRunDeliveryTarget,
  validateLinkDeliveryTargetContract,
} from '../dist-c4/src/link/contracts/delivery-target-contract.js';
import {
  createIdempotencyInputFromQueueItem,
  createLinkDeliveryHeaders,
  createLinkDeliveryIdempotencyContract,
  validateLinkDeliveryIdempotencyContract,
} from '../dist-c4/src/link/contracts/delivery-idempotency-contract.js';
import {
  createEdgeLinkReliabilityAck,
  createEdgeLinkReliabilityKey,
  createReplayWindowFromGap,
  detectSequenceGap,
  isDuplicateSequence,
  validateEdgeLinkSequenceRef,
} from '../dist-c4/src/link/contracts/edge-link-reliability-contract.js';
import {
  createBlockedDeliveryAttempt,
  createDryRunDeliveryAttempt,
  createLinkDeliveryReceipt,
  validateLinkDeliveryAttemptContract,
  validateLinkDeliveryReceiptContract,
} from '../dist-c4/src/link/contracts/delivery-attempt-receipt-contract.js';
import {
  assertProductionDeliveryBlockedForC4,
  evaluateProductionDeliveryBlockGuard,
} from '../dist-c4/src/link/contracts/production-delivery-block-guard.js';

function createIntake(overrides = {}) {
  const base = {
    protocolVersion: 'v1',
    eventId: 'delivery-event-001',
    traceId: 'delivery-trace-001',
    correlationId: 'delivery-corr-001',
    recordType: 'alarm',
    occurredAt: '2026-06-20T00:00:00.000Z',
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash: 'sha256:delivery-event-001',
    normalizedPayload: {
      deviceId: 'ahu-001',
      pointId: 'fan-fault',
      active: true,
      severity: 'CRITICAL',
      dedupeKey: 'tenant-a:site-a:gw-a:edge-a:ahu-001:fan-fault:alarm',
      streamId: 'alarm',
      sequenceNumber: 77,
    },
    source: {
      gatewayId: 'gw-a',
      edgeId: 'edge-a',
      siteId: 'site-a',
      tenantId: 'tenant-a',
      sourceSystem: 'synthetic-c4',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: 'evidence-c4-001',
        evidenceType: 'handoff',
      },
    ],
  };

  return {
    ...base,
    ...overrides,
    normalizedPayload: {
      ...base.normalizedPayload,
      ...(overrides.normalizedPayload ?? {}),
    },
    source: {
      ...base.source,
      ...(overrides.source ?? {}),
    },
  };
}

const intake = createIntake();
const partitionKey = createPartitionKeyFromIntake(intake);
const partitionId = assignPartitionId(partitionKey, 16);

const item = createLinkQueueItemContract({
  intake,
  queueId: 'link-q-c4-001',
  partitionId,
  partitionKey,
  enqueuedAt: '2026-06-20T00:00:02.000Z',
});

assert.deepEqual(validateLinkQueueItemContract(item), []);
assert.equal(item.priority, 'CRITICAL');

const target = createSyntheticDryRunDeliveryTarget('target-c4-dry-run');
assert.deepEqual(validateLinkDeliveryTargetContract(target).reasons, []);
assert.equal(target.productionDeliveryAllowed, false);

const idempotencyInput = createIdempotencyInputFromQueueItem(intake, item);
assert.equal(idempotencyInput.streamId, 'alarm');
assert.equal(idempotencyInput.sequenceNumber, 77);
assert.equal(idempotencyInput.dedupeKey, 'tenant-a:site-a:gw-a:edge-a:ahu-001:fan-fault:alarm');

const idempotency = createLinkDeliveryIdempotencyContract(idempotencyInput);
assert.deepEqual(validateLinkDeliveryIdempotencyContract(idempotency), []);
assert.ok(idempotency.idempotencyKey.includes('alarm'));
assert.ok(idempotency.reliabilityKey.includes('77'));
assert.ok(idempotency.duplicateRiskKey.includes('sha256:delivery-event-001'));

const headers = createLinkDeliveryHeaders({
  idempotency,
  deliveryId: 'delivery-c4-001',
});

assert.equal(headers['X-VANTARIS-Trace-Id'], 'delivery-trace-001');
assert.equal(headers['X-VANTARIS-Gateway-Id'], 'gw-a');
assert.equal(headers['X-VANTARIS-Stream-Id'], 'alarm');
assert.equal(headers['X-VANTARIS-Sequence-Number'], '77');
assert.equal(headers['X-VANTARIS-Link-Queue-Id'], 'link-q-c4-001');
assert.equal(headers['X-VANTARIS-Link-Delivery-Id'], 'delivery-c4-001');

const sequenceRef = {
  stream: {
    gatewayId: 'gw-a',
    edgeId: 'edge-a',
    streamId: 'alarm',
    tenantId: 'tenant-a',
    siteId: 'site-a',
  },
  sequenceNumber: 77,
  eventId: intake.eventId,
  traceId: intake.traceId,
  payloadHash: intake.payloadHash,
  occurredAt: intake.occurredAt,
};

assert.deepEqual(validateEdgeLinkSequenceRef(sequenceRef), []);
assert.equal(createEdgeLinkReliabilityKey(sequenceRef), idempotency.reliabilityKey);

const ledger = {
  gatewayId: 'gw-a',
  streamId: 'alarm',
  lastAcceptedSequence: 75,
  seenEventIds: [],
  seenPayloadHashes: [],
  duplicateCount: 0,
  gapRanges: [],
};

const gap = detectSequenceGap(ledger, sequenceRef, '2026-06-20T00:00:03.000Z');
assert.ok(gap);
assert.equal(gap.fromSequence, 76);
assert.equal(gap.toSequence, 76);

const replayWindow = createReplayWindowFromGap(gap);
assert.equal(replayWindow.fromSequence, 76);
assert.equal(replayWindow.toSequence, 76);
assert.equal(replayWindow.reason, 'SEQUENCE_GAP');

const replayAck = createEdgeLinkReliabilityAck({
  ref: sequenceRef,
  status: 'REPLAY_REQUESTED',
  gapDetected: true,
  replayWindow,
  acknowledgedAt: '2026-06-20T00:00:04.000Z',
});
assert.equal(replayAck.status, 'REPLAY_REQUESTED');
assert.equal(replayAck.gapDetected, true);

const duplicateLedger = {
  ...ledger,
  lastAcceptedSequence: 77,
  seenEventIds: ['delivery-event-001'],
  seenPayloadHashes: ['sha256:delivery-event-001'],
};
assert.equal(isDuplicateSequence(duplicateLedger, sequenceRef), true);

const guard = evaluateProductionDeliveryBlockGuard({
  target,
  item,
  idempotency,
});
assert.equal(guard.allowed, true);
assert.equal(guard.dryRunAllowed, true);
assert.equal(guard.code, 'LINK_DELIVERY_DRY_RUN_ALLOWED');

const dryRunAttempt = createDryRunDeliveryAttempt({
  item,
  target,
  idempotency,
  headers,
  attemptNumber: 1,
  startedAt: '2026-06-20T00:00:05.000Z',
});
assert.deepEqual(validateLinkDeliveryAttemptContract(dryRunAttempt), []);
assert.equal(dryRunAttempt.status, 'DELIVERY_DRY_RUN_ACCEPTED');
assert.equal(dryRunAttempt.sequenceNumber, 77);

const dryRunReceipt = createLinkDeliveryReceipt({
  attempt: dryRunAttempt,
  completedAt: '2026-06-20T00:00:06.000Z',
});
assert.deepEqual(validateLinkDeliveryReceiptContract(dryRunReceipt), []);
assert.equal(dryRunReceipt.accepted, true);
assert.equal(dryRunReceipt.dryRun, true);
assert.equal(dryRunReceipt.productionDelivery, false);

const productionLookingTarget = {
  ...target,
  targetType: 'UFMS_APP_API',
  status: 'APPROVED_PRODUCTION',
  baseUrl: 'https://ufms.example.invalid',
  endpointPath: '/api/v1/link/events',
  approved: true,
  productionDeliveryAllowed: true,
  approvalRef: {
    approvalId: 'prod-approval-not-active-in-c4',
    approvalType: 'production_approval',
  },
  credentialRef: {
    credentialRefId: 'machine-ref-only',
    credentialType: 'machine_identity',
    secretMaterialStored: false,
  },
};

const forcedBlock = assertProductionDeliveryBlockedForC4({
  target: productionLookingTarget,
  item,
  idempotency,
});
assert.equal(forcedBlock.allowed, false);
assert.equal(forcedBlock.dryRunAllowed, false);
assert.equal(forcedBlock.code, 'LINK_DELIVERY_PRODUCTION_BLOCKED');

const blockedAttempt = createBlockedDeliveryAttempt({
  item,
  target: productionLookingTarget,
  idempotency,
  headers,
  attemptNumber: 1,
  startedAt: '2026-06-20T00:00:07.000Z',
});
assert.deepEqual(validateLinkDeliveryAttemptContract(blockedAttempt), []);
assert.equal(blockedAttempt.status, 'DELIVERY_BLOCKED');

const blockedReceipt = createLinkDeliveryReceipt({
  attempt: blockedAttempt,
  completedAt: '2026-06-20T00:00:08.000Z',
});
assert.deepEqual(validateLinkDeliveryReceiptContract(blockedReceipt), []);
assert.equal(blockedReceipt.accepted, false);
assert.equal(blockedReceipt.productionDelivery, false);

console.log('LINK_C4_05_SYNTHETIC_DELIVERY_VALIDATION_PASS');
