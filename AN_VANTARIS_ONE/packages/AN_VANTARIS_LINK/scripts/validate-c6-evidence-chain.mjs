import assert from 'node:assert/strict';

import {
  createLinkAuditEvent,
  validateLinkAuditEventContract,
} from '../dist-c6/src/link/contracts/audit-event-contract.js';

import {
  createEvidenceChainFromAudits,
  createEvidenceRecordFromAudit,
  createDeterministicEvidenceHash,
  mapAuditStageToEvidenceRecordType,
  validateEvidenceChainContract,
} from '../dist-c6/src/link/contracts/evidence-chain-contract.js';

const base = {
  eventId: 'evidence-event-001',
  traceId: 'evidence-trace-001',
  gatewayId: 'gw-evidence-001',
  streamId: 'alarm',
  sequenceNumber: 3001,
  occurredAt: '2026-06-20T00:00:00.000Z',
};

const audits = [
  createLinkAuditEvent({
    auditType: 'INGRESS',
    severity: 'INFO',
    stage: 'INGRESS_RECEIVED',
    ...base,
    recordedAt: '2026-06-20T00:00:01.000Z',
    actorType: 'EDGE_GATEWAY',
    evidenceRefs: [
      {
        evidenceId: 'ingress-evidence-001',
        evidenceType: 'ingress',
      },
    ],
  }),
  createLinkAuditEvent({
    auditType: 'INGRESS',
    severity: 'INFO',
    stage: 'INGRESS_VALIDATED',
    ...base,
    recordedAt: '2026-06-20T00:00:02.000Z',
    actorType: 'LINK_RUNTIME',
  }),
  createLinkAuditEvent({
    auditType: 'QUEUE',
    severity: 'INFO',
    stage: 'QUEUE_ENQUEUED',
    ...base,
    queueId: 'link-q-evidence-001',
    recordedAt: '2026-06-20T00:00:03.000Z',
  }),
  createLinkAuditEvent({
    auditType: 'DELIVERY',
    severity: 'INFO',
    stage: 'DELIVERY_DRY_RUN',
    ...base,
    queueId: 'link-q-evidence-001',
    deliveryId: 'link-delivery-evidence-001',
    recordedAt: '2026-06-20T00:00:04.000Z',
  }),
  createLinkAuditEvent({
    auditType: 'RETRY',
    severity: 'WARN',
    stage: 'RETRY_DECISION',
    ...base,
    queueId: 'link-q-evidence-001',
    deliveryId: 'link-delivery-evidence-001',
    reasonCode: 'LINK_DELIVERY_TIMEOUT',
    recordedAt: '2026-06-20T00:00:05.000Z',
  }),
  createLinkAuditEvent({
    auditType: 'DLQ',
    severity: 'ERROR',
    stage: 'DLQ_MOVED',
    ...base,
    queueId: 'link-q-evidence-001',
    deliveryId: 'link-delivery-evidence-001',
    dlqId: 'link-dlq-evidence-001',
    reasonCode: 'LINK_DELIVERY_RETRY_EXHAUSTED',
    recordedAt: '2026-06-20T00:00:06.000Z',
  }),
  createLinkAuditEvent({
    auditType: 'REPLAY',
    severity: 'WARN',
    stage: 'REPLAY_REQUESTED',
    ...base,
    reasonCode: 'SEQUENCE_GAP',
    recordedAt: '2026-06-20T00:00:07.000Z',
  }),
  createLinkAuditEvent({
    auditType: 'RELIABILITY',
    severity: 'INFO',
    stage: 'RELIABILITY_ACK',
    ...base,
    reasonCode: 'ACKED',
    recordedAt: '2026-06-20T00:00:08.000Z',
  }),
];

for (const audit of audits) {
  assert.deepEqual(validateLinkAuditEventContract(audit), []);
  assert.equal(audit.productionDeliveryAllowed, false);
  assert.equal(audit.eventId, base.eventId);
  assert.equal(audit.traceId, base.traceId);
  assert.equal(audit.gatewayId, base.gatewayId);
  assert.equal(audit.streamId, base.streamId);
  assert.equal(audit.sequenceNumber, base.sequenceNumber);
}

assert.equal(mapAuditStageToEvidenceRecordType('INGRESS_RECEIVED'), 'INGRESS_RECEIVED');
assert.equal(mapAuditStageToEvidenceRecordType('QUEUE_ENQUEUED'), 'QUEUE_ENQUEUED');
assert.equal(mapAuditStageToEvidenceRecordType('DELIVERY_DRY_RUN'), 'DELIVERY_DRY_RUN');
assert.equal(mapAuditStageToEvidenceRecordType('DLQ_MOVED'), 'DLQ_MOVED');
assert.equal(mapAuditStageToEvidenceRecordType('REPLAY_REQUESTED'), 'REPLAY_REQUESTED');
assert.equal(mapAuditStageToEvidenceRecordType('RELIABILITY_ACK'), 'RELIABILITY_ACK');

const firstRecord = createEvidenceRecordFromAudit({
  audit: audits[0],
  previousHash: null,
});
assert.equal(firstRecord.previousHash, null);
assert.ok(firstRecord.currentHash.startsWith('fnv1a32:'));

const secondRecord = createEvidenceRecordFromAudit({
  audit: audits[1],
  previousHash: firstRecord.currentHash,
});
assert.equal(secondRecord.previousHash, firstRecord.currentHash);
assert.ok(secondRecord.currentHash.startsWith('fnv1a32:'));
assert.notEqual(secondRecord.currentHash, firstRecord.currentHash);

const deterministicHash = createDeterministicEvidenceHash('same-input');
assert.equal(deterministicHash, createDeterministicEvidenceHash('same-input'));
assert.notEqual(deterministicHash, createDeterministicEvidenceHash('different-input'));

const chain = createEvidenceChainFromAudits({
  audits,
  chainComplete: true,
});

assert.equal(chain.traceId, base.traceId);
assert.equal(chain.eventId, base.eventId);
assert.equal(chain.gatewayId, base.gatewayId);
assert.equal(chain.streamId, base.streamId);
assert.equal(chain.sequenceNumber, base.sequenceNumber);
assert.equal(chain.records.length, audits.length);
assert.equal(chain.chainComplete, true);
assert.equal(chain.productionDeliveryAllowed, false);
assert.deepEqual(validateEvidenceChainContract(chain), []);

for (let index = 0; index < chain.records.length; index += 1) {
  const record = chain.records[index];

  if (index === 0) {
    assert.equal(record.previousHash, null);
  } else {
    assert.equal(record.previousHash, chain.records[index - 1].currentHash);
  }

  assert.ok(record.currentHash.startsWith('fnv1a32:'));
}

assert.equal(chain.currentHash, chain.records[chain.records.length - 1].currentHash);

const tamperedChain = {
  ...chain,
  records: [
    ...chain.records.slice(0, 1),
    {
      ...chain.records[1],
      previousHash: 'fnv1a32:tampered',
    },
    ...chain.records.slice(2),
  ],
};

assert.ok(validateEvidenceChainContract(tamperedChain).includes('evidence chain previousHash mismatch'));

console.log('LINK_C6_03_EVIDENCE_CHAIN_VALIDATION_PASS');
