#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../.." && pwd)"
MANIFEST="$ROOT_DIR/AN_VANTARIS_LINK/deploy/offline-bundle/manifests/link-offline-package-manifest.v1.json"

if [ ! -f "$MANIFEST" ]; then
  echo "LINK_OFFLINE_PACKAGE_MANIFEST_MISSING"
  exit 1
fi

node <<'NODE'
const fs = require('node:fs');
const path = require('node:path');

const root = process.cwd();
const manifestPath = path.join(root, 'AN_VANTARIS_LINK/deploy/offline-bundle/manifests/link-offline-package-manifest.v1.json');

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

assert(manifest.manifestVersion === 'link-offline-package-manifest.v1', 'invalid manifestVersion');
assert(manifest.packageName === 'AN_VANTARIS_LINK_OFFLINE_BUNDLE', 'invalid packageName');
assert(manifest.packageStatus === 'STRUCTURE_ONLY', 'packageStatus must remain STRUCTURE_ONLY');
assert(manifest.scope === 'AN_VANTARIS_LINK', 'scope must be AN_VANTARIS_LINK');

assert(manifest.linkRuntimeEnabled === false, 'linkRuntimeEnabled must remain false');
assert(manifest.linkProductionDeliveryAllowed === false, 'linkProductionDeliveryAllowed must remain false');
assert(manifest.endpointApproved === false, 'endpointApproved must remain false');
assert(manifest.directUfmsDbAccessAllowed === false, 'directUfmsDbAccessAllowed must remain false');
assert(manifest.writebackAllowed === false, 'writebackAllowed must remain false');
assert(manifest.consumerImplementationIncluded === false, 'consumerImplementationIncluded must remain false');

const contractsManifest = path.join(root, manifest.contractsManifestRef);
assert(fs.existsSync(contractsManifest), `missing contracts manifest: ${manifest.contractsManifestRef}`);

assert(Array.isArray(manifest.bundleFiles), 'bundleFiles must be array');
assert(manifest.bundleFiles.length >= 6, 'bundleFiles must contain expected offline bundle files');

for (const item of manifest.bundleFiles) {
  assert(item.path, 'bundle file missing path');
  const filePath = path.join(root, item.path);
  assert(fs.existsSync(filePath), `missing bundle file: ${item.path}`);

  if (item.executable === true) {
    fs.accessSync(filePath, fs.constants.X_OK);
  }
}

assert(Array.isArray(manifest.validationCommands), 'validationCommands must be array');
assert(
  manifest.validationCommands.includes('npm --prefix AN_VANTARIS_LINK run typecheck'),
  'missing typecheck validation command',
);
assert(
  manifest.validationCommands.includes('bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh'),
  'missing boundary scan validation command',
);

const boundary = manifest.boundary;
assert(boundary.structureOnly === true, 'boundary.structureOnly must remain true');
assert(boundary.contractOnlyReference === true, 'boundary.contractOnlyReference must remain true');
assert(boundary.linkRuntimeEnabled === false, 'boundary.linkRuntimeEnabled must remain false');
assert(boundary.linkProductionDeliveryAllowed === false, 'boundary.linkProductionDeliveryAllowed must remain false');
assert(boundary.endpointApproved === false, 'boundary.endpointApproved must remain false');
assert(boundary.directUfmsDbAccessAllowed === false, 'boundary.directUfmsDbAccessAllowed must remain false');
assert(boundary.writebackAllowed === false, 'boundary.writebackAllowed must remain false');
assert(boundary.consumerImplementationIncluded === false, 'boundary.consumerImplementationIncluded must remain false');
assert(boundary.realUfmsApiDeliveryEnabled === false, 'boundary.realUfmsApiDeliveryEnabled must remain false');

console.log('LINK_C8_03_PACKAGE_VERIFICATION_SCRIPT_VALIDATE_PASS');
console.log('LINK_OFFLINE_PACKAGE_STRUCTURE_ONLY_CONFIRMED');
console.log('LINK_PRODUCTION_DELIVERY_BLOCK_CONFIRMED');
NODE
