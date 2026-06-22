import assert from 'node:assert/strict';

import {
  createDefaultLinkRuntimeHealthSnapshot,
  deriveLinkRuntimeHealthStatus,
  deriveLinkRuntimeReadyStatus,
  validateLinkRuntimeHealthSnapshotContract,
} from '../dist-c7/src/link/contracts/runtime-health-snapshot-contract.js';

import {
  createLinkDiagnosticsBundleFromHealthSnapshot,
  createLinkDiagnosticsBundleHash,
  deriveLinkDiagnosticsBundleStatus,
  validateLinkRuntimeDiagnosticsBundleContract,
} from '../dist-c7/src/link/contracts/runtime-diagnostics-bundle-contract.js';

const snapshot = createDefaultLinkRuntimeHealthSnapshot({
  linkNodeId: 'link-node-c7-001',
  generatedAt: '2026-06-20T00:00:00.000Z',
});

assert.equal(snapshot.linkNodeId, 'link-node-c7-001');
assert.equal(snapshot.runtimeEnabled, false);
assert.equal(snapshot.productionDeliveryAllowed, false);
assert.equal(snapshot.writebackAllowed, false);
assert.equal(snapshot.directDbAccessAllowed, false);
assert.equal(snapshot.delivery.productionDeliveryAllowed, false);
assert.deepEqual(validateLinkRuntimeHealthSnapshotContract(snapshot), []);

const derivedHealth = deriveLinkRuntimeHealthStatus({
  ingress: snapshot.ingress,
  queue: snapshot.queue,
  dlq: snapshot.dlq,
  delivery: snapshot.delivery,
  retryReplay: snapshot.retryReplay,
  gatewayLiveness: snapshot.gatewayLiveness,
  evidence: snapshot.evidence,
});

assert.equal(derivedHealth, 'BLOCKED');
assert.equal(deriveLinkRuntimeReadyStatus(derivedHealth), 'BLOCKED');

const bundle = createLinkDiagnosticsBundleFromHealthSnapshot({
  healthSnapshot: snapshot,
  generatedAt: '2026-06-20T00:00:01.000Z',
  exportScope: 'FIELD_ENGINEER',
  evidenceRefs: [
    {
      evidenceId: 'link-c7-evidence-001',
      evidenceType: 'health',
      sourcePath: 'AN_VANTARIS_LINK/evidence/LINK_C7_00_RUNTIME_OPERATIONS_DIAGNOSTICS_PLAN.md',
    },
  ],
  warnings: ['production delivery remains blocked'],
});

assert.equal(bundle.linkNodeId, 'link-node-c7-001');
assert.equal(bundle.exportScope, 'FIELD_ENGINEER');
assert.equal(bundle.healthStatus, snapshot.healthStatus);
assert.equal(bundle.status, deriveLinkDiagnosticsBundleStatus(snapshot.healthStatus));
assert.equal(bundle.items.length, 8);
assert.equal(bundle.manifest.itemCount, bundle.items.length);
assert.deepEqual(bundle.manifest.itemIds, bundle.items.map((item) => item.itemId));

const expectedHash = createLinkDiagnosticsBundleHash({
  bundleId: bundle.bundleId,
  itemIds: bundle.manifest.itemIds,
  generatedAt: bundle.generatedAt,
});

assert.equal(bundle.manifest.bundleHash, expectedHash);
assert.equal(bundle.containsSecretMaterial, false);
assert.equal(bundle.manifest.containsSecretMaterial, false);
assert.equal(bundle.runtimeEnabled, false);
assert.equal(bundle.productionDeliveryAllowed, false);
assert.equal(bundle.writebackAllowed, false);
assert.equal(bundle.directDbAccessAllowed, false);
assert.equal(bundle.manifest.runtimeEnabled, false);
assert.equal(bundle.manifest.productionDeliveryAllowed, false);
assert.equal(bundle.manifest.writebackAllowed, false);
assert.equal(bundle.manifest.directDbAccessAllowed, false);

const itemTypes = bundle.items.map((item) => item.itemType);
assert.ok(itemTypes.includes('health_snapshot'));
assert.ok(itemTypes.includes('ingress_summary'));
assert.ok(itemTypes.includes('queue_summary'));
assert.ok(itemTypes.includes('dlq_summary'));
assert.ok(itemTypes.includes('delivery_summary'));
assert.ok(itemTypes.includes('retry_replay_summary'));
assert.ok(itemTypes.includes('gateway_liveness_summary'));
assert.ok(itemTypes.includes('evidence_summary'));

assert.ok(bundle.items.every((item) => item.containsSecretMaterial === false));
assert.deepEqual(validateLinkRuntimeDiagnosticsBundleContract(bundle), []);

const invalidSnapshot = {
  ...snapshot,
  productionDeliveryAllowed: true,
};

assert.ok(
  validateLinkRuntimeHealthSnapshotContract(invalidSnapshot).includes(
    'productionDeliveryAllowed must remain false',
  ),
);

const invalidBundle = {
  ...bundle,
  containsSecretMaterial: true,
};

assert.ok(
  validateLinkRuntimeDiagnosticsBundleContract(invalidBundle).includes(
    'containsSecretMaterial must remain false',
  ),
);

console.log('LINK_C7_03_RUNTIME_DIAGNOSTICS_VALIDATION_PASS');
