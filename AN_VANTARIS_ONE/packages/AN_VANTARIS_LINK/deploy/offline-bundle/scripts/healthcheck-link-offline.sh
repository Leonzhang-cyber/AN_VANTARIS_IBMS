#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../.." && pwd)"
MANIFEST="$ROOT_DIR/AN_VANTARIS_LINK/deploy/offline-bundle/manifests/link-offline-package-manifest.v1.json"
CONTRACTS_MANIFEST="$ROOT_DIR/AN_VANTARIS_Contracts/manifest/AN_VANTARIS_CONTRACTS_SCHEMA_MANIFEST.v1.json"
C7_EVIDENCE="$ROOT_DIR/AN_VANTARIS_LINK/evidence/LINK_C7_05_C7_AGGREGATE_GATE.md"

if [ ! -f "$MANIFEST" ]; then
  echo "LINK_HEALTHCHECK_FAIL_MANIFEST_MISSING"
  exit 1
fi

if [ ! -f "$CONTRACTS_MANIFEST" ]; then
  echo "LINK_HEALTHCHECK_FAIL_CONTRACTS_MANIFEST_MISSING"
  exit 1
fi

if [ ! -f "$C7_EVIDENCE" ]; then
  echo "LINK_HEALTHCHECK_FAIL_C7_DIAGNOSTICS_EVIDENCE_MISSING"
  exit 1
fi

node <<'NODE'
const fs = require('node:fs');
const path = require('node:path');

const root = process.cwd();
const manifestPath = path.join(root, 'AN_VANTARIS_LINK/deploy/offline-bundle/manifests/link-offline-package-manifest.v1.json');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert(manifest.packageStatus === 'STRUCTURE_ONLY', 'packageStatus must remain STRUCTURE_ONLY');
assert(manifest.linkRuntimeEnabled === false, 'linkRuntimeEnabled must remain false');
assert(manifest.linkProductionDeliveryAllowed === false, 'linkProductionDeliveryAllowed must remain false');
assert(manifest.endpointApproved === false, 'endpointApproved must remain false');
assert(manifest.directUfmsDbAccessAllowed === false, 'directUfmsDbAccessAllowed must remain false');
assert(manifest.writebackAllowed === false, 'writebackAllowed must remain false');
assert(manifest.consumerImplementationIncluded === false, 'consumerImplementationIncluded must remain false');

const boundary = manifest.boundary || {};
assert(boundary.structureOnly === true, 'boundary.structureOnly must remain true');
assert(boundary.realUfmsApiDeliveryEnabled === false, 'realUfmsApiDeliveryEnabled must remain false');

console.log('LINK_C8_04_LOCAL_HEALTHCHECK_PASS');
console.log('LINK_OFFLINE_BUNDLE_HEALTHY');
console.log('LINK_C7_DIAGNOSTICS_EVIDENCE_PRESENT');
console.log('LINK_CONTRACTS_MANIFEST_REFERENCE_PRESENT');
console.log('LINK_PRODUCTION_DELIVERY_BLOCK_CONFIRMED');
NODE
