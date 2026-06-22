import assert from 'node:assert/strict';

import {
  createDefaultBlockedEdgeProductionState,
} from '../dist-c3/src/link/contracts/edge-handoff-intake-contract.js';
import {
  createLinkQueueStateSnapshot,
  createLinkQueueStateTransition,
  canTransitionLinkQueueState,
  isTerminalLinkQueueState,
  isRetryableLinkQueueState,
  mapLegacyQueueStateToGaState,
} from '../dist-c3/src/link/contracts/queue-state-contract.js';
import {
  createLinkQueueItemContract,
  createPartitionKeyFromIntake,
  inferQueuePriorityFromRecordType,
  validateLinkQueueItemContract,
} from '../dist-c3/src/link/contracts/queue-item-contract.js';
import {
  assignPartitionId,
  createPartitionAssignmentFromQueueItem,
  createPartitionMetadataFromIntake,
  validatePartitionMetadata,
} from '../dist-c3/src/link/contracts/partition-priority-contract.js';
import {
  createDurableQueueAppendRecord,
  createDurableQueueStateTransitionRecord,
  createDryRunRecoveryPlan,
  createReplayCandidateFromRecord,
  validateDurableQueueRecord,
} from '../dist-c3/src/link/contracts/durable-queue-contract.js';

function createValidIntake(overrides = {}) {
  const base = {
    protocolVersion: 'v1',
    eventId: 'edge-event-c3-001',
    traceId: 'trace-c3-001',
    correlationId: 'corr-c3-001',
    recordType: 'alarm',
    occurredAt: '2026-06-20T00:00:00.000Z',
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash: 'sha256:c3-example',
    normalizedPayload: {
      pointId: 'ALARM-001',
      value: 1,
      severity: 'CRITICAL',
    },
    source: {
      gatewayId: 'gw-c3-001',
      edgeId: 'edge-c3-001',
      siteId: 'site-c3-001',
      tenantId: 'tenant-c3-001',
      sourceSystem: 'synthetic',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: 'evidence-c3-001',
        evidenceType: 'handoff',
      },
    ],
  };

  return {
    ...base,
    ...overrides,
    source: {
      ...base.source,
      ...(overrides.source ?? {}),
    },
    productionState: {
      ...base.productionState,
      ...(overrides.productionState ?? {}),
    },
  };
}

const intake = createValidIntake();

assert.equal(mapLegacyQueueStateToGaState('PENDING'), 'QUEUED');
assert.equal(mapLegacyQueueStateToGaState('RETRYING'), 'RETRY_PENDING');
assert.equal(mapLegacyQueueStateToGaState('FAILED'), 'DLQ');
assert.equal(mapLegacyQueueStateToGaState('DELIVERED'), 'DELIVERED');

assert.equal(isTerminalLinkQueueState('ACKED'), true);
assert.equal(isTerminalLinkQueueState('DLQ'), true);
assert.equal(isTerminalLinkQueueState('QUEUED'), false);

assert.equal(isRetryableLinkQueueState('RETRY_PENDING'), true);
assert.equal(isRetryableLinkQueueState('QUEUED'), true);
assert.equal(isRetryableLinkQueueState('ACKED'), false);

assert.equal(canTransitionLinkQueueState('RECEIVED', 'VALIDATED'), true);
assert.equal(canTransitionLinkQueueState('QUEUED', 'DELIVERING'), true);
assert.equal(canTransitionLinkQueueState('ACKED', 'QUEUED'), false);

const snapshot = createLinkQueueStateSnapshot('QUEUED', 'INGRESS_QUEUED', 0, '2026-06-20T00:00:01.000Z');
assert.equal(snapshot.state, 'QUEUED');
assert.equal(snapshot.retryable, true);
assert.equal(snapshot.terminal, false);

const transition = createLinkQueueStateTransition(
  'QUEUED',
  'DELIVERING',
  'DELIVERY_STARTED',
  '2026-06-20T00:00:02.000Z',
);
assert.equal(transition.from, 'QUEUED');
assert.equal(transition.to, 'DELIVERING');

const partitionKey = createPartitionKeyFromIntake(intake);
assert.equal(partitionKey, 'tenant-c3-001:site-c3-001:gw-c3-001:alarm');

assert.equal(inferQueuePriorityFromRecordType('alarm'), 'CRITICAL');
assert.equal(inferQueuePriorityFromRecordType('event'), 'HIGH');
assert.equal(inferQueuePriorityFromRecordType('telemetry'), 'NORMAL');

const partitionId = assignPartitionId(partitionKey, 8);
assert.equal(Number.isInteger(partitionId), true);
assert.ok(partitionId >= 0);
assert.ok(partitionId < 8);

const item = createLinkQueueItemContract({
  intake,
  queueId: 'link-q-c3-001',
  partitionId,
  partitionKey,
  enqueuedAt: '2026-06-20T00:00:03.000Z',
});

assert.equal(item.queueId, 'link-q-c3-001');
assert.equal(item.eventId, intake.eventId);
assert.equal(item.traceId, intake.traceId);
assert.equal(item.gatewayId, intake.source.gatewayId);
assert.equal(item.priority, 'CRITICAL');
assert.equal(item.state, 'QUEUED');
assert.equal(item.partitionKey, partitionKey);
assert.deepEqual(validateLinkQueueItemContract(item), []);

const metadata = createPartitionMetadataFromIntake(intake, item.priority, 8);
assert.equal(metadata.gatewayId, intake.source.gatewayId);
assert.equal(metadata.recordType, 'alarm');
assert.equal(metadata.priority, 'CRITICAL');
assert.equal(metadata.lane, 'CRITICAL');
assert.deepEqual(validatePartitionMetadata(metadata), []);

const assignment = createPartitionAssignmentFromQueueItem(item);
assert.equal(assignment.partitionId, item.partitionId);
assert.equal(assignment.partitionKey, item.partitionKey);
assert.equal(assignment.lane, 'CRITICAL');

const appendRecord = createDurableQueueAppendRecord(item, '2026-06-20T00:00:04.000Z');
assert.equal(appendRecord.kind, 'QUEUE_APPEND');
assert.equal(appendRecord.queueId, item.queueId);
assert.equal(appendRecord.state, 'QUEUED');
assert.deepEqual(validateDurableQueueRecord(appendRecord), []);

const transitionRecord = createDurableQueueStateTransitionRecord({
  item,
  to: 'RETRY_PENDING',
  reason: 'DELIVERY_RETRY_PENDING',
  recordedAt: '2026-06-20T00:00:05.000Z',
});
assert.equal(transitionRecord.kind, 'QUEUE_STATE_TRANSITION');
assert.equal(transitionRecord.state, 'RETRY_PENDING');
assert.deepEqual(validateDurableQueueRecord(transitionRecord), []);

const recoveryPlan = createDryRunRecoveryPlan({
  partitionId,
  recoveredRecords: 2,
});
assert.equal(recoveryPlan.source, 'DRY_RUN');
assert.equal(recoveryPlan.recoveredRecords, 2);
assert.equal(recoveryPlan.skippedRecords, 0);

const replayCandidate = createReplayCandidateFromRecord(appendRecord);
assert.equal(replayCandidate.eligible, true);

const ackedRecord = {
  ...appendRecord,
  state: 'ACKED',
};
const blockedReplayCandidate = createReplayCandidateFromRecord(ackedRecord);
assert.equal(blockedReplayCandidate.eligible, false);

console.log('LINK_C3_05_QUEUE_VALIDATION_HARNESS_PASS');
