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
  createPartitionMetadataFromIntake,
  validatePartitionMetadata,
} from '../dist-c3/src/link/contracts/partition-priority-contract.js';
import {
  createDurableQueueAppendRecord,
  validateDurableQueueRecord,
} from '../dist-c3/src/link/contracts/durable-queue-contract.js';

function createStableTelemetryIntake({
  eventId,
  traceId,
  gatewayId,
  edgeId,
  deviceId,
  pointId,
  value,
  payloadHash,
  suppressedCount,
  dedupeKey,
}) {
  return {
    protocolVersion: 'v1',
    eventId,
    traceId,
    correlationId: `corr-${eventId}`,
    recordType: 'telemetry',
    occurredAt: '2026-06-20T00:00:00.000Z',
    receivedAt: '2026-06-20T00:00:01.000Z',
    payloadHash,
    normalizedPayload: {
      deviceId,
      pointId,
      value,
      quality: 'GOOD',
      sampleMode: 'DEADBAND',
      changeReason: suppressedCount > 0 ? 'SUPPRESSED_NO_CHANGE' : 'FIRST_SAMPLE',
      dedupeKey,
      suppressedCount,
      valueChanged: false,
      qualityChanged: false,
      deadbandApplied: true,
      deadbandValue: 0.1,
      aggregationWindowMs: 60000,
    },
    source: {
      gatewayId,
      edgeId,
      siteId: 'site-stable-001',
      tenantId: 'tenant-stable-001',
      sourceSystem: 'edge-stable-suppression',
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

function createAlarmIntake() {
  return {
    protocolVersion: 'v1',
    eventId: 'alarm-critical-001',
    traceId: 'trace-alarm-critical-001',
    correlationId: 'corr-alarm-critical-001',
    recordType: 'alarm',
    occurredAt: '2026-06-20T00:00:02.000Z',
    receivedAt: '2026-06-20T00:00:03.000Z',
    payloadHash: 'sha256:alarm-critical-001',
    normalizedPayload: {
      deviceId: 'ahu-001',
      pointId: 'fan-fault',
      active: true,
      severity: 'CRITICAL',
      sampleMode: 'AGGREGATED_REPEAT',
      changeReason: 'ALARM_NEW_ACTIVE',
      repeatCount: 0,
    },
    source: {
      gatewayId: 'gw-stable-001',
      edgeId: 'edge-stable-001',
      siteId: 'site-stable-001',
      tenantId: 'tenant-stable-001',
      sourceSystem: 'edge-stable-suppression',
      connectorType: 'file',
      adapterType: 'readonly',
    },
    decisionState: 'BLOCKED_PRODUCTION_NOT_APPROVED',
    productionState: createDefaultBlockedEdgeProductionState(),
    evidenceRefs: [
      {
        evidenceId: 'evidence-alarm-critical-001',
        evidenceType: 'handoff',
      },
    ],
  };
}

const stableDedupeKey =
  'tenant-stable-001:site-stable-001:gw-stable-001:edge-stable-001:ahu-001:supply-temp:telemetry';

const telemetryIntakes = [
  createStableTelemetryIntake({
    eventId: 'stable-telemetry-001',
    traceId: 'trace-stable-001',
    gatewayId: 'gw-stable-001',
    edgeId: 'edge-stable-001',
    deviceId: 'ahu-001',
    pointId: 'supply-temp',
    value: 23.5,
    payloadHash: 'sha256:stable-temp-23-5',
    suppressedCount: 0,
    dedupeKey: stableDedupeKey,
  }),
  createStableTelemetryIntake({
    eventId: 'stable-telemetry-002',
    traceId: 'trace-stable-002',
    gatewayId: 'gw-stable-001',
    edgeId: 'edge-stable-001',
    deviceId: 'ahu-001',
    pointId: 'supply-temp',
    value: 23.5,
    payloadHash: 'sha256:stable-temp-23-5',
    suppressedCount: 42,
    dedupeKey: stableDedupeKey,
  }),
  createStableTelemetryIntake({
    eventId: 'stable-telemetry-003',
    traceId: 'trace-stable-003',
    gatewayId: 'gw-stable-001',
    edgeId: 'edge-stable-001',
    deviceId: 'ahu-001',
    pointId: 'supply-temp',
    value: 23.5,
    payloadHash: 'sha256:stable-temp-23-5',
    suppressedCount: 84,
    dedupeKey: stableDedupeKey,
  }),
];

const alarmIntake = createAlarmIntake();

const allIntakes = [...telemetryIntakes, alarmIntake];
const partitionCount = 16;

const queueItems = allIntakes.map((intake, index) => {
  const partitionKey = createPartitionKeyFromIntake(intake);
  const partitionId = assignPartitionId(partitionKey, partitionCount);

  const item = createLinkQueueItemContract({
    intake,
    queueId: `link-q-stable-${index + 1}`,
    partitionId,
    partitionKey,
    enqueuedAt: `2026-06-20T00:00:0${index + 1}.000Z`,
  });

  assert.deepEqual(validateLinkQueueItemContract(item), []);

  const metadata = createPartitionMetadataFromIntake(intake, item.priority, partitionCount);
  assert.deepEqual(validatePartitionMetadata(metadata), []);

  const durable = createDurableQueueAppendRecord(item, '2026-06-20T00:00:10.000Z');
  assert.deepEqual(validateDurableQueueRecord(durable), []);

  return { item, intake, metadata, durable };
});

const telemetryItems = queueItems.filter(({ intake }) => intake.recordType === 'telemetry');
const alarmItems = queueItems.filter(({ intake }) => intake.recordType === 'alarm');

assert.equal(telemetryItems.length, 3);
assert.equal(alarmItems.length, 1);

assert.ok(telemetryItems.every(({ item }) => item.priority === 'NORMAL'));
assert.ok(alarmItems.every(({ item }) => item.priority === 'CRITICAL'));

assert.ok(telemetryItems.every(({ metadata }) => metadata.lane === 'NORMAL'));
assert.ok(alarmItems.every(({ metadata }) => metadata.lane === 'CRITICAL'));

const dedupeGroups = new Map();
for (const { intake } of telemetryItems) {
  const dedupeKey = intake.normalizedPayload.dedupeKey;
  dedupeGroups.set(dedupeKey, (dedupeGroups.get(dedupeKey) ?? 0) + 1);
}

assert.equal(dedupeGroups.get(stableDedupeKey), 3);

const payloadHashGroups = new Map();
for (const { item } of telemetryItems) {
  const payloadKey = `${item.gatewayId}:${item.payloadHash}`;
  payloadHashGroups.set(payloadKey, (payloadHashGroups.get(payloadKey) ?? 0) + 1);
}

assert.equal(payloadHashGroups.get('gw-stable-001:sha256:stable-temp-23-5'), 3);

const totalSuppressedCount = telemetryItems.reduce(
  (sum, { intake }) => sum + intake.normalizedPayload.suppressedCount,
  0,
);

assert.equal(totalSuppressedCount, 126);

const criticalLaneCount = queueItems.filter(({ metadata }) => metadata.lane === 'CRITICAL').length;
const normalLaneCount = queueItems.filter(({ metadata }) => metadata.lane === 'NORMAL').length;

assert.equal(criticalLaneCount, 1);
assert.equal(normalLaneCount, 3);

const alarm = alarmItems[0];
assert.equal(alarm.intake.normalizedPayload.changeReason, 'ALARM_NEW_ACTIVE');
assert.equal(alarm.item.priority, 'CRITICAL');

console.log('LINK_C3_05C_STABLE_TELEMETRY_DUPLICATE_AWARENESS_PASS');
