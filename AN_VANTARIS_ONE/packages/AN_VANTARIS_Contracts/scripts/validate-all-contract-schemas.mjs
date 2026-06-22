import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const manifestPath = path.join(
  root,
  'AN_VANTARIS_Contracts/manifest/AN_VANTARIS_CONTRACTS_SCHEMA_MANIFEST.v1.json',
);

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function getBoundary(schema, schemaPath) {
  const boundary = schema?.properties?.boundary?.properties;
  assert(boundary, `missing boundary properties: ${schemaPath}`);
  return boundary;
}

function assertConst(boundary, key, expected, schemaPath) {
  assert(boundary[key], `missing boundary.${key}: ${schemaPath}`);
  assert(
    boundary[key].const === expected,
    `unexpected boundary.${key} in ${schemaPath}: expected ${expected}, got ${boundary[key].const}`,
  );
}

assert(fs.existsSync(manifestPath), `missing manifest: ${manifestPath}`);

const manifest = readJson(manifestPath);

assert(
  manifest.manifestVersion === 'an-vantaris-contracts-schema-manifest.v1',
  'invalid manifestVersion',
);
assert(manifest.status === 'CONTRACT_ONLY', 'manifest must remain CONTRACT_ONLY');
assert(manifest.runtimeEnabled === false, 'manifest runtimeEnabled must remain false');
assert(
  manifest.productionDeliveryAllowed === false,
  'manifest productionDeliveryAllowed must remain false',
);
assert(
  manifest.directUfmsDbAccessAllowed === false,
  'manifest directUfmsDbAccessAllowed must remain false',
);
assert(manifest.writebackAllowed === false, 'manifest writebackAllowed must remain false');
assert(
  manifest.consumerImplementationIncluded === false,
  'manifest consumerImplementationIncluded must remain false',
);

const expectedGroupIds = new Set(['CONTRACTS-C1', 'CONTRACTS-C2', 'CONTRACTS-C3']);
const groupIds = new Set(manifest.schemaGroups.map((group) => group.groupId));

for (const expectedGroupId of expectedGroupIds) {
  assert(groupIds.has(expectedGroupId), `missing manifest group: ${expectedGroupId}`);
}

let schemaCount = 0;
const schemaIds = new Set();

for (const group of manifest.schemaGroups) {
  assert(group.status === 'COMPLETE', `manifest group not complete: ${group.groupId}`);
  assert(Array.isArray(group.schemas), `manifest group schemas missing: ${group.groupId}`);
  assert(group.schemas.length > 0, `manifest group schemas empty: ${group.groupId}`);

  for (const item of group.schemas) {
    schemaCount += 1;

    assert(item.schemaId, `missing schemaId in group ${group.groupId}`);
    assert(item.schemaVersion, `missing schemaVersion for ${item.schemaId}`);
    assert(item.domain, `missing domain for ${item.schemaId}`);
    assert(item.layer, `missing layer for ${item.schemaId}`);
    assert(item.path, `missing path for ${item.schemaId}`);
    assert(!schemaIds.has(item.schemaId), `duplicate schemaId: ${item.schemaId}`);

    schemaIds.add(item.schemaId);

    const schemaPath = path.join(root, item.path);
    assert(fs.existsSync(schemaPath), `schema path does not exist: ${item.path}`);

    const schema = readJson(schemaPath);

    assert(
      schema.$schema === 'https://json-schema.org/draft/2020-12/schema',
      `invalid $schema: ${item.path}`,
    );
    assert(schema.$id === item.schemaId, `schema $id mismatch: ${item.path}`);
    assert(schema.type === 'object', `schema type must be object: ${item.path}`);
    assert(
      schema.additionalProperties === false,
      `schema additionalProperties must be false: ${item.path}`,
    );
    assert(
      schema.properties?.schemaVersion?.const === item.schemaVersion,
      `schemaVersion const mismatch: ${item.path}`,
    );

    const boundary = getBoundary(schema, item.path);

    if (item.domain === 'airport' || item.domain === 'consumer-boundary') {
      assertConst(boundary, 'contractOnly', true, item.path);
    }

    if (boundary.edgeRuntimeEnabled) {
      assertConst(boundary, 'edgeRuntimeEnabled', false, item.path);
    }

    if (boundary.linkProductionDeliveryAllowed) {
      assertConst(boundary, 'linkProductionDeliveryAllowed', false, item.path);
    }

    if (boundary.directUfmsDbAccessAllowed) {
      assertConst(boundary, 'directUfmsDbAccessAllowed', false, item.path);
    }

    if (boundary.writebackAllowed) {
      assertConst(boundary, 'writebackAllowed', false, item.path);
    }

    if (boundary.consumerImplementationIncluded) {
      assertConst(boundary, 'consumerImplementationIncluded', false, item.path);
    }

    if (boundary.runtimeConnectorImplemented) {
      assertConst(boundary, 'runtimeConnectorImplemented', false, item.path);
    }

    if (boundary.runtimeMappingApplied) {
      assertConst(boundary, 'runtimeMappingApplied', false, item.path);
    }

    if (boundary.runtimeAssetWriteApplied) {
      assertConst(boundary, 'runtimeAssetWriteApplied', false, item.path);
    }

    if (boundary.runtimeLocationWriteApplied) {
      assertConst(boundary, 'runtimeLocationWriteApplied', false, item.path);
    }

    if (boundary.workOrderRuntimeCreated) {
      assertConst(boundary, 'workOrderRuntimeCreated', false, item.path);
    }

    if (boundary.vantarisOneRuntimeImplemented) {
      assertConst(boundary, 'vantarisOneRuntimeImplemented', false, item.path);
    }

    if (boundary.ucdeRuntimeImplemented) {
      assertConst(boundary, 'ucdeRuntimeImplemented', false, item.path);
    }

    if (boundary.evidenceReviewRuntimeImplemented) {
      assertConst(boundary, 'evidenceReviewRuntimeImplemented', false, item.path);
    }

    if (boundary.ufmsApiRuntimeImplemented) {
      assertConst(boundary, 'ufmsApiRuntimeImplemented', false, item.path);
    }

    if (boundary.ufmsBackendModified) {
      assertConst(boundary, 'ufmsBackendModified', false, item.path);
    }
  }
}

assert(schemaCount === 14, `expected 14 schemas, found ${schemaCount}`);

console.log('CONTRACTS_C4_02_FULL_SCHEMA_VALIDATION_PASS');
console.log(`CONTRACTS_SCHEMA_COUNT_${schemaCount}`);
