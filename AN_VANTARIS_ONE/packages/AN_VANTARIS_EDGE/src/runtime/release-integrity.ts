import { createHash } from 'node:crypto';
import { readFileSync, lstatSync, realpathSync, existsSync } from 'node:fs';
import { dirname, isAbsolute, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import type {
  ChecksumManifest,
  ReleaseAcceptanceResult,
  ReleaseManifest,
  SignatureMetadata,
  ValidationResult,
} from './release-integrity-types.js';

const READINESS_KEY = 'UFMS_EDGE_C4_02_RELEASE_MANIFEST_CHECKSUM_SIGNATURE_FOUNDATION_PASS';
const runtimeDir = dirname(fileURLToPath(import.meta.url));
const EDGE_ROOT = resolve(runtimeDir, '..', '..');
const REPO_ROOT = resolve(EDGE_ROOT, '..');
const INTEGRITY_ROOT = resolve(EDGE_ROOT, 'deploy', 'offline-bundle', 'integrity');

const MANIFEST_DEFAULT_PATH = resolve(INTEGRITY_ROOT, 'RELEASE_MANIFEST.edge.json');
const CHECKSUMS_DEFAULT_PATH = resolve(INTEGRITY_ROOT, 'CHECKSUMS.edge.json');
const SIGNATURE_METADATA_DEFAULT_PATH = resolve(INTEGRITY_ROOT, 'SIGNATURE_METADATA.edge.json');

const ALLOWED_ROOTS = [
  'AN_VANTARIS_EDGE/src/',
  'AN_VANTARIS_EDGE/config/',
  'AN_VANTARIS_EDGE/deploy/',
  'AN_VANTARIS_EDGE/scripts/',
  'AN_VANTARIS_EDGE/docs/',
  'AN_VANTARIS_EDGE/evidence/',
] as const;

function assertInsideEdge(pathValue: string): string {
  const resolved = resolve(pathValue);
  if (!resolved.startsWith(EDGE_ROOT + sep) && resolved !== EDGE_ROOT) {
    throw new Error(`path outside EDGE root is forbidden: ${pathValue}`);
  }
  return resolved;
}

function assertInsideRepo(pathValue: string): string {
  const resolved = resolve(pathValue);
  if (!resolved.startsWith(REPO_ROOT + sep) && resolved !== REPO_ROOT) {
    throw new Error(`path outside repository root is forbidden: ${pathValue}`);
  }
  return resolved;
}

function parseJson<T>(filePath: string): T {
  const raw = readFileSync(filePath, 'utf8');
  return JSON.parse(raw) as T;
}

function isHexSha256(value: unknown): boolean {
  return typeof value === 'string' && /^[a-f0-9]{64}$/.test(value);
}

function hasPathTraversal(value: string): boolean {
  return value.includes('..') || value.includes(`..${sep}`) || value.includes('/../');
}

function isAllowedInventoryPath(relativePath: string): boolean {
  return ALLOWED_ROOTS.some((root) => relativePath.startsWith(root));
}

function rejectRuntimePath(relativePath: string): boolean {
  return relativePath.startsWith('AN_VANTARIS_EDGE/.runtime/');
}

function assertNoExternalSymlink(filePath: string): void {
  const stat = lstatSync(filePath);
  if (!stat.isSymbolicLink()) {
    return;
  }
  const real = realpathSync(filePath);
  assertInsideEdge(real);
}

export function loadReleaseManifest(manifestPath: string = MANIFEST_DEFAULT_PATH): ReleaseManifest {
  const resolved = assertInsideEdge(manifestPath);
  return parseJson<ReleaseManifest>(resolved);
}

export function validateReleaseManifest(manifest: unknown): ValidationResult {
  const errors: string[] = [];
  const row = manifest as Partial<ReleaseManifest>;
  if (row?.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (row?.taskId !== 'UFMS-EDGE-C4-02') errors.push('taskId mismatch');
  if (row?.releaseClassification !== 'FOUNDATION_ONLY') errors.push('releaseClassification must be FOUNDATION_ONLY');
  if (row?.productionRelease !== false) errors.push('productionRelease must be false');
  if (row?.productionSignaturePresent !== false) errors.push('productionSignaturePresent must be false');
  if (row?.signatureMode !== 'SYNTHETIC_METADATA_ONLY') errors.push('signatureMode must be SYNTHETIC_METADATA_ONLY');
  if (row?.checksumAlgorithm !== 'SHA-256') errors.push('checksumAlgorithm must be SHA-256');
  if (row?.sbomPresent !== false) errors.push('sbomPresent must be false');
  if (row?.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  if (!Array.isArray(row?.fileInventory)) errors.push('fileInventory must be array');
  if (Array.isArray(row?.fileInventory)) {
    let prev = '';
    for (const entry of row.fileInventory) {
      if (typeof entry.relativePath !== 'string') {
        errors.push('inventory relativePath must be string');
        continue;
      }
      if (hasPathTraversal(entry.relativePath)) errors.push(`inventory path traversal forbidden: ${entry.relativePath}`);
      if (rejectRuntimePath(entry.relativePath)) errors.push(`runtime path forbidden in inventory: ${entry.relativePath}`);
      if (!isAllowedInventoryPath(entry.relativePath)) errors.push(`inventory path outside allowed roots: ${entry.relativePath}`);
      if (entry.relativePath < prev) errors.push('inventory must be sorted by relativePath');
      prev = entry.relativePath;
      if (!isHexSha256(entry.sha256)) errors.push(`invalid sha256: ${entry.relativePath}`);
    }
  }
  return { ok: errors.length === 0, errors };
}

export function loadChecksumManifest(checksumPath: string = CHECKSUMS_DEFAULT_PATH): ChecksumManifest {
  const resolved = assertInsideEdge(checksumPath);
  return parseJson<ChecksumManifest>(resolved);
}

export function validateChecksumManifest(checksumManifest: unknown): ValidationResult {
  const errors: string[] = [];
  const row = checksumManifest as Partial<ChecksumManifest>;
  if (row?.schemaVersion !== '1.0') errors.push('checksum schemaVersion must be 1.0');
  if (row?.algorithm !== 'SHA-256') errors.push('checksum algorithm must be SHA-256');
  if (row?.productionCertification !== false) errors.push('productionCertification must be false');
  if (row?.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  if (!Array.isArray(row?.files)) errors.push('checksum files must be array');
  if (Array.isArray(row?.files)) {
    if (row.fileCount !== row.files.length) errors.push('fileCount mismatch');
    for (const item of row.files) {
      if (typeof item.path !== 'string' || !item.path.startsWith('AN_VANTARIS_EDGE/')) {
        errors.push('checksum entry path must be under AN_VANTARIS_EDGE');
      }
      if (!isHexSha256(item.sha256)) errors.push(`invalid checksum entry sha256: ${item.path}`);
    }
    const computedAggregate = calculateAggregateDigest(
      row.files.map((item) => ({ path: item.path, sha256: item.sha256 })),
    );
    if (typeof row.aggregateDigest !== 'string' || row.aggregateDigest !== computedAggregate) {
      errors.push('aggregateDigest mismatch');
    }
  }
  return { ok: errors.length === 0, errors };
}

export function calculateFileSha256(filePath: string): string {
  const abs = assertInsideRepo(filePath);
  const bytes = readFileSync(abs);
  return createHash('sha256').update(bytes).digest('hex');
}

export function calculateAggregateDigest(
  entries: readonly { path: string; sha256: string }[],
): string {
  const sorted = [...entries].sort((a, b) => a.path.localeCompare(b.path));
  const payload = sorted.map((entry) => `${entry.path}:${entry.sha256}`).join('\n');
  return createHash('sha256').update(payload).digest('hex');
}

export function verifyFileInventory(
  manifest: ReleaseManifest,
  inventoryRoot: string = REPO_ROOT,
): ValidationResult {
  const errors: string[] = [];
  const root = assertInsideRepo(inventoryRoot);
  for (const entry of manifest.fileInventory) {
    if (!entry.relativePath.startsWith('AN_VANTARIS_EDGE/')) {
      errors.push(`inventory entry outside edge package: ${entry.relativePath}`);
      continue;
    }
    if (rejectRuntimePath(entry.relativePath)) {
      errors.push(`runtime path found in inventory: ${entry.relativePath}`);
      continue;
    }
    const targetPath = resolve(root, entry.relativePath);
    if (!targetPath.startsWith(root + sep) && targetPath !== root) {
      errors.push(`path traversal resolved outside inventory root: ${entry.relativePath}`);
      continue;
    }
    if (!existsSync(targetPath)) {
      errors.push(`inventory file missing: ${entry.relativePath}`);
      continue;
    }
    assertInsideEdge(targetPath);
    assertNoExternalSymlink(targetPath);
    const size = lstatSync(targetPath).size;
    const digest = calculateFileSha256(targetPath);
    if (size !== entry.sizeBytes) {
      errors.push(`size mismatch: ${entry.relativePath}`);
    }
    if (digest !== entry.sha256) {
      errors.push(`sha mismatch: ${entry.relativePath}`);
    }
  }
  return { ok: errors.length === 0, errors };
}

export function validateSignatureMetadata(signature: unknown): ValidationResult {
  const errors: string[] = [];
  const row = signature as Partial<SignatureMetadata>;
  if (row?.schemaVersion !== '1.0') errors.push('signature schemaVersion must be 1.0');
  if (row?.signatureStatus !== 'NOT_PRODUCTION_SIGNED') errors.push('signatureStatus must be NOT_PRODUCTION_SIGNED');
  if (row?.signatureMode !== 'SYNTHETIC_METADATA_ONLY') errors.push('signatureMode must be SYNTHETIC_METADATA_ONLY');
  if (row?.detachedSignaturePresent !== false) errors.push('detachedSignaturePresent must be false');
  if (row?.hsmBacked !== false) errors.push('hsmBacked must be false');
  if (row?.pkcs11Backed !== false) errors.push('pkcs11Backed must be false');
  if (row?.productionCertification !== false) errors.push('productionCertification must be false');
  return { ok: errors.length === 0, errors };
}

export function evaluateReleaseAcceptance(
  manifest: ReleaseManifest,
  checksums: ChecksumManifest,
  signatureMetadata: SignatureMetadata,
): ReleaseAcceptanceResult {
  if (manifest.productionRelease && !manifest.productionSignaturePresent) {
    return 'PRODUCTION_REJECTED_UNSIGNED';
  }
  if (
    manifest.productionRelease ||
    manifest.productionSignaturePresent ||
    signatureMetadata.detachedSignaturePresent ||
    signatureMetadata.productionCertification
  ) {
    return 'FOUNDATION_REJECTED';
  }
  const manifestValidation = validateReleaseManifest(manifest);
  const checksumValidation = validateChecksumManifest(checksums);
  const signatureValidation = validateSignatureMetadata(signatureMetadata);
  if (!manifestValidation.ok || !checksumValidation.ok || !signatureValidation.ok) {
    return 'FOUNDATION_REJECTED';
  }
  return 'FOUNDATION_ACCEPTED_NOT_PRODUCTION';
}

export function loadSignatureMetadata(
  signaturePath: string = SIGNATURE_METADATA_DEFAULT_PATH,
): SignatureMetadata {
  const resolved = isAbsolute(signaturePath) ? signaturePath : resolve(EDGE_ROOT, signaturePath);
  const safePath = assertInsideEdge(resolved);
  return parseJson<SignatureMetadata>(safePath);
}
