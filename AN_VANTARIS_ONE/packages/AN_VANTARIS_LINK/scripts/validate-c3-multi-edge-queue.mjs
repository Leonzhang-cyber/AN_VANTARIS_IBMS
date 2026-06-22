import assert from 'node:assert/strict';

import {
  createDefaultBlockedEdgeProductionState,
} from '../dist-c3/src/link/contracts/edge-handoff-intake-contract.js';
import {
  createLinkQueueItemContract,
  createPartitionKeyFromIntake,
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
  createReplayCandidateFromRecord,
  validateDurableQueueRecord,
} from '../dist-c3/src/link/contracts/durable-queue-contract.js';

function createIntake({
  tenantId,
  siteId,
  gatewayId,
  edgeId,
  eventId,
  traceId,
  recordType,
  payloadHash,
  occurredAt,
}) {
  return {
    protocolVersion: 'v1',
    eventId,
    traceId,
    correlationId: `corr-${eventId}`,
    recordType,
    occurredAt,
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash,
    normalizedPayload: {
      pointId: `${gatewayId}-${recordType}`,
      value: 1,
      quality: 'GOOD',
    },
    source: {
      gatewayId,
      edgeId,
      siteId,
      tenantId,
      sourceSystem: 'synthetic-multi-edge',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: `evidence-${eventId}`,
        evidenceType: 'handoff',
      },
    ],
  };
}

const intakes = [
  createIntake({
    tenantId: 'tenant-a',
    siteId: 'site-a',
    gatewayId: 'gw-a-001',
    edgeId: 'edge-a-001',
    eventId: 'event-a-telemetry-001',
    traceId: 'trace-a-telemetry-001',
    recordType: 'telemetry',
    payloadHash: 'sha256:a-telemetry-001',
    occurredAt: '2026-06-20T00:00:00.000Z',
  }),
  createIntake({
    tenantId: 'tenant-a',
    siteId: 'site-a',
    gatewayId: 'gw-a-002',
    edgeId: 'edge-a-002',
    eventId: 'event-a-alarm-001',
    traceId: 'trace-a-alarm-001',
    recordType: 'alarm',
    payloadHash: 'sha256:a-alarm-001',
    occurredAt: '2026-06-20T00:00:00.100Z',
  }),
  createIntake({
    tenantId: 'tenant-b',
    siteId: 'site-b',
    gatewayId: 'gw-b-001',
    edgeId: 'edge-b-001',
    eventId: 'event-b-health-001',
    traceId: 'trace-b-health-001',
    recordType: 'health',
    payloadHash: 'sha256:b-health-001',
    occurredAt: '2026-06-20T00:00:00.200Z',
  }),
  createIntake({
    tenantId: 'tenant-b',
    siteId: 'site-b',
    gatewayId: 'gw-b-002',
    edgeId: 'edge-b-002',
    eventId: 'event-b-event-001',
    traceId: 'trace-b-event-001',
    recordType: 'event',
    payloadHash: 'sha256:b-event-001',
    occurredAt: '2026-06-20T00:00:00.300Z',
  }),
  createIntake({
    tenantId: 'tenant-a',
    siteId: 'site-a',
    gatewayId: 'gw-a-001',
    edgeId: 'edge-a-001',
    eventId: 'event-a-telemetry-001',
    traceId: 'trace-a-telemetry-duplicate',
    recordType: 'telemetry',
    payloadHash: 'sha256:a-telemetry-001',
    occurredAt: '2026-06-20T00:00:00.400Z',
  }),
];

const partitionCount = 16;

const queueItems = intakes.map((intake, index) => {
  const partitionKey = createPartitionKeyFromIntake(intake);
  const partitionId = assignPartitionId(partitionKey, partitionCount);

  const item = createLinkQueueItemContract({
    intake,
    queueId: `link-q-multi-${index + 1}`,
    partitionId,
    partitionKey,
    enqueuedAt: `2026-06-20T00:00:0${index + 1}.000Z`,
  });

  assert.deepEqual(validateLinkQueueItemContract(item), []);

  return item;
});

assert.equal(queueItems.length, 5);

const gatewayCounts = new Map();
const tenantCounts = new Map();
const laneCounts = new Map();
const partitionCounts = new Map();

for (const item of queueItems) {
  gatewayCounts.set(item.gatewayId, (gatewayCounts.get(item.gatewayId) ?? 0) + 1);
  tenantCounts.set(item.partitionIdentity.tenantId, (tenantCounts.get(item.partitionIdentity.tenantId) ?? 0) + 1);

  const metadata = createPartitionMetadataFromIntake(
    intakes.find((intake) => intake.eventId === item.eventId && intake.traceId === item.traceId) ?? intakes[0],
    item.priority,
    partitionCount,
  );
  assert.deepEqual(validatePartitionMetadata(metadata), []);

  laneCounts.set(metadata.lane, (laneCounts.get(metadata.lane) ?? 0) + 1);
  partitionCounts.set(item.partitionId, (partitionCounts.get(item.partitionId) ?? 0) + 1);

  const assignment = createPartitionAssignmentFromQueueItem(item);
  assert.equal(assignment.partitionId, item.partitionId);
  assert.equal(assignment.partitionKey, item.partitionKey);

  const durable = createDurableQueueAppendRecord(item, '2026-06-20T00:00:10.000Z');
  assert.deepEqual(validateDurableQueueRecord(durable), []);

  const replayCandidate = createReplayCandidateFromRecord(durable);
  assert.equal(replayCandidate.eligible, true);
}

assert.equal(gatewayCounts.get('gw-a-001'), 2);
assert.equal(gatewayCounts.get('gw-a-002'), 1);
assert.equal(gatewayCounts.get('gw-b-001'), 1);
assert.equal(gatewayCounts.get('gw-b-002'), 1);

assert.equal(tenantCounts.get('tenant-a'), 3);
assert.equal(tenantCounts.get('tenant-b'), 2);

assert.equal(laneCounts.get('CRITICAL'), 1);
assert.equal(laneCounts.get('HIGH'), 2);
assert.equal(laneCounts.get('NORMAL'), 2);

const alarmItem = queueItems.find((item) => item.eventId === 'event-a-alarm-001');
assert.ok(alarmItem);
assert.equal(alarmItem.priority, 'CRITICAL');

const telemetryItems = queueItems.filter((item) => item.partitionIdentity.recordType === 'telemetry');
assert.equal(telemetryItems.length, 2);
assert.ok(telemetryItems.every((item) => item.priority === 'NORMAL'));

const duplicateKeys = new Map();
for (const item of queueItems) {
  const dedupeKey = `${item.gatewayId}:${item.eventId}:${item.payloadHash}`;
  duplicateKeys.set(dedupeKey, (duplicateKeys.get(dedupeKey) ?? 0) + 1);
}

const duplicateCount = [...duplicateKeys.values()].filter((count) => count > 1).length;
assert.equal(duplicateCount, 1);

assert.ok(partitionCounts.size >= 2);

console.log('LINK_C3_05B_MULTI_EDGE_CONCURRENT_QUEUE_VALIDATION_PASS');
