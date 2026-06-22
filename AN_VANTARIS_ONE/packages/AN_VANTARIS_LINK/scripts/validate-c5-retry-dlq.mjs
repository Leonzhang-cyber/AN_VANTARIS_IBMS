import assert from 'node:assert/strict';

import {
  createDefaultBlockedEdgeProductionState,
} from '../dist-c5/src/link/contracts/edge-handoff-intake-contract.js';
import {
  createLinkQueueItemContract,
  createPartitionKeyFromIntake,
} from '../dist-c5/src/link/contracts/queue-item-contract.js';
import {
  assignPartitionId,
} from '../dist-c5/src/link/contracts/partition-priority-contract.js';
import {
  createSyntheticDryRunDeliveryTarget,
} from '../dist-c5/src/link/contracts/delivery-target-contract.js';
import {
  createIdempotencyInputFromQueueItem,
  createLinkDeliveryHeaders,
  createLinkDeliveryIdempotencyContract,
} from '../dist-c5/src/link/contracts/delivery-idempotency-contract.js';
import {
  createDryRunDeliveryAttempt,
} from '../dist-c5/src/link/contracts/delivery-attempt-receipt-contract.js';
import {
  createDefaultLinkRetryPolicy,
  calculateRetryBackoffMs,
  hasRetryBudget,
  isNonRetryableReason,
  isRetryableReason,
  validateLinkRetryPolicyContract,
} from '../dist-c5/src/link/contracts/retry-policy-contract.js';
import {
  createLinkRetryDecision,
  validateLinkRetryDecisionContract,
} from '../dist-c5/src/link/contracts/retry-decision-contract.js';
import {
  getLinkDlqReasonDefinition,
  isLinkDlqReasonOperatorActionRequired,
  isLinkDlqReasonReplayEligible,
  isLinkDlqReasonRetryable,
} from '../dist-c5/src/link/contracts/dlq-reason-taxonomy.js';
import {
  createLinkDlqMovementFromDelivery,
  createLinkDlqMovementFromQueue,
  validateLinkDlqMovementContract,
} from '../dist-c5/src/link/contracts/dlq-movement-contract.js';

function createIntake() {
  return {
    protocolVersion: 'v1',
    eventId: 'retry-dlq-event-001',
    traceId: 'retry-dlq-trace-001',
    correlationId: 'retry-dlq-corr-001',
    recordType: 'event',
    occurredAt: '2026-06-20T00:00:00.000Z',
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash: 'sha256:retry-dlq-event-001',
    normalizedPayload: {
      deviceId: 'ahu-001',
      pointId: 'fan-status',
      value: 'FAULT',
      streamId: 'event',
      sequenceNumber: 88,
      dedupeKey: 'tenant-a:site-a:gw-a:edge-a:ahu-001:fan-status:event',
    },
    source: {
      gatewayId: 'gw-a',
      edgeId: 'edge-a',
      siteId: 'site-a',
      tenantId: 'tenant-a',
      sourceSystem: 'synthetic-c5',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: 'evidence-c5-001',
        evidenceType: 'handoff',
      },
    ],
  };
}

const intake = createIntake();
const partitionKey = createPartitionKeyFromIntake(intake);
const partitionId = assignPartitionId(partitionKey, 16);

const item = createLinkQueueItemContract({
  intake,
  queueId: 'link-q-c5-001',
  partitionId,
  partitionKey,
  enqueuedAt: '2026-06-20T00:00:02.000Z',
});

const target = createSyntheticDryRunDeliveryTarget('target-c5-dry-run');
const idempotencyInput = createIdempotencyInputFromQueueItem(intake, item);
const idempotency = createLinkDeliveryIdempotencyContract(idempotencyInput);
const headers = createLinkDeliveryHeaders({
  idempotency,
  deliveryId: 'delivery-c5-001',
});

const attempt = createDryRunDeliveryAttempt({
  item,
  target,
  idempotency,
  headers,
  attemptNumber: 1,
  startedAt: '2026-06-20T00:00:05.000Z',
});

const policy = createDefaultLinkRetryPolicy('retry-policy-c5');
assert.equal(validateLinkRetryPolicyContract(policy).valid, true);

assert.equal(isRetryableReason(policy, 'LINK_DELIVERY_TIMEOUT'), true);
assert.equal(isRetryableReason(policy, 'LINK_NETWORK_ERROR'), true);
assert.equal(isNonRetryableReason(policy, 'LINK_SCHEMA_INVALID'), true);
assert.equal(isNonRetryableReason(policy, 'LINK_DELIVERY_PRODUCTION_BLOCKED'), true);

assert.equal(
  calculateRetryBackoffMs({
    policy,
    attemptNumber: 1,
    deterministicJitterSeed: 10,
  }),
  510,
);

assert.equal(
  calculateRetryBackoffMs({
    policy,
    attemptNumber: 2,
    deterministicJitterSeed: 10,
  }),
  1010,
);

assert.equal(
  hasRetryBudget({
    policy,
    globalUsed: 0,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: 0,
    replay: false,
  }),
  true,
);

assert.equal(
  hasRetryBudget({
    policy,
    globalUsed: policy.budget.globalRetryBudget,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: 0,
    replay: false,
  }),
  false,
);

const retryDecision = createLinkRetryDecision({
  policy,
  reasonCode: 'LINK_DELIVERY_TIMEOUT',
  attemptNumber: 1,
  nowMs: Date.parse('2026-06-20T00:00:00.000Z'),
  deterministicJitterSeed: 10,
  replay: false,
  budgetUsage: {
    globalUsed: 0,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: 0,
  },
});
assert.deepEqual(validateLinkRetryDecisionContract(retryDecision), []);
assert.equal(retryDecision.shouldRetry, true);
assert.equal(retryDecision.retryable, true);
assert.equal(retryDecision.dlqRequired, false);
assert.equal(retryDecision.backoffMs, 510);

const exhaustedDecision = createLinkRetryDecision({
  policy,
  reasonCode: 'LINK_DELIVERY_TIMEOUT',
  attemptNumber: policy.maxAttempts,
  nowMs: Date.parse('2026-06-20T00:00:00.000Z'),
  deterministicJitterSeed: 10,
  replay: false,
  budgetUsage: {
    globalUsed: 0,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: 0,
  },
});
assert.equal(exhaustedDecision.shouldRetry, false);
assert.equal(exhaustedDecision.retryable, true);
assert.equal(exhaustedDecision.dlqRequired, true);

const nonRetryableDecision = createLinkRetryDecision({
  policy,
  reasonCode: 'LINK_SCHEMA_INVALID',
  attemptNumber: 1,
  nowMs: Date.parse('2026-06-20T00:00:00.000Z'),
  replay: false,
  budgetUsage: {
    globalUsed: 0,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: 0,
  },
});
assert.equal(nonRetryableDecision.shouldRetry, false);
assert.equal(nonRetryableDecision.retryable, false);
assert.equal(nonRetryableDecision.dlqRequired, false);

const budgetStormDecision = createLinkRetryDecision({
  policy,
  reasonCode: 'LINK_DELIVERY_TIMEOUT',
  attemptNumber: 1,
  nowMs: Date.parse('2026-06-20T00:00:00.000Z'),
  replay: true,
  budgetUsage: {
    globalUsed: 0,
    targetUsed: 0,
    gatewayUsed: 0,
    streamUsed: 0,
    replayUsed: policy.budget.replayRetryBudget,
  },
});
assert.equal(budgetStormDecision.shouldRetry, false);
assert.equal(budgetStormDecision.retryable, true);
assert.equal(budgetStormDecision.stormProtected, true);
assert.equal(budgetStormDecision.dlqRequired, true);

const timeoutReason = getLinkDlqReasonDefinition('LINK_DELIVERY_TIMEOUT');
assert.equal(timeoutReason.category, 'DELIVERY');
assert.equal(isLinkDlqReasonRetryable('LINK_DELIVERY_TIMEOUT'), true);
assert.equal(isLinkDlqReasonReplayEligible('LINK_DELIVERY_TIMEOUT'), true);

const schemaReason = getLinkDlqReasonDefinition('LINK_SCHEMA_INVALID');
assert.equal(schemaReason.category, 'SCHEMA');
assert.equal(isLinkDlqReasonRetryable('LINK_SCHEMA_INVALID'), false);
assert.equal(isLinkDlqReasonOperatorActionRequired('LINK_SCHEMA_INVALID'), true);

const retryExhaustedReason = getLinkDlqReasonDefinition('LINK_DELIVERY_RETRY_EXHAUSTED');
assert.equal(retryExhaustedReason.category, 'RETRY_EXHAUSTED');
assert.equal(retryExhaustedReason.operatorActionRequired, true);

const deliveryDlq = createLinkDlqMovementFromDelivery({
  attempt,
  reasonCode: 'LINK_DELIVERY_RETRY_EXHAUSTED',
  movedAt: '2026-06-20T00:01:00.000Z',
  evidenceRefs: [
    {
      evidenceId: 'delivery-evidence-c5-001',
      evidenceType: 'delivery',
    },
  ],
});
assert.equal(validateLinkDlqMovementContract(deliveryDlq).valid, true);
assert.equal(deliveryDlq.queueId, item.queueId);
assert.equal(deliveryDlq.deliveryId, attempt.deliveryId);
assert.equal(deliveryDlq.streamId, 'event');
assert.equal(deliveryDlq.sequenceNumber, 88);
assert.equal(deliveryDlq.category, 'RETRY_EXHAUSTED');
assert.equal(deliveryDlq.replayEligible, true);
assert.equal(deliveryDlq.productionDeliveryAllowed, false);

const queueDlq = createLinkDlqMovementFromQueue({
  item,
  reasonCode: 'LINK_QUEUE_EXPIRED',
  movedAt: '2026-06-20T00:02:00.000Z',
});
assert.equal(validateLinkDlqMovementContract(queueDlq).valid, true);
assert.equal(queueDlq.category, 'QUEUE');
assert.equal(queueDlq.replayEligible, false);
assert.equal(queueDlq.productionDeliveryAllowed, false);

console.log('LINK_C5_05_RETRY_DLQ_VALIDATION_PASS');
