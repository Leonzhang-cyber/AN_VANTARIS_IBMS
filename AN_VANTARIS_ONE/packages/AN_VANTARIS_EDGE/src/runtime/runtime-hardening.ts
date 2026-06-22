import { lstatSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import type {
  FilesystemOwnershipPolicy,
  PermissionMatrix,
  RuntimeHardeningAcceptanceResult,
  RuntimeIdentityPolicy,
  SensitiveFilePolicy,
  SystemdHardeningPolicy,
  ValidationResult,
} from './runtime-hardening-types.js';

const READINESS_KEY = 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
const runtimeDir = dirname(fileURLToPath(import.meta.url));
const EDGE_ROOT = resolve(runtimeDir, '..', '..');
const HARDENING_ROOT = resolve(EDGE_ROOT, 'deploy', 'offline-bundle', 'hardening');

function assertInsideEdge(pathValue: string): string {
  const resolved = resolve(pathValue);
  if (!resolved.startsWith(EDGE_ROOT + sep) && resolved !== EDGE_ROOT) {
    throw new Error(`path outside edge root: ${pathValue}`);
  }
  return resolved;
}

function readJson<T>(pathValue: string): T {
  return JSON.parse(readFileSync(assertInsideEdge(pathValue), 'utf8')) as T;
}

function modeLooksSafe(mode: string): boolean {
  return /^[0-7]{4}$/.test(mode);
}

export function loadRuntimeIdentityPolicy(
  pathValue: string = resolve(HARDENING_ROOT, 'RUNTIME_IDENTITY.edge.json'),
): RuntimeIdentityPolicy {
  return readJson<RuntimeIdentityPolicy>(pathValue);
}

export function validateRuntimeIdentityPolicy(policy: unknown): ValidationResult {
  const row = policy as RuntimeIdentityPolicy;
  const errors: string[] = [];
  if (row.schemaVersion !== '1.0') errors.push('schemaVersion mismatch');
  if (row.taskId !== 'UFMS-EDGE-C4-04') errors.push('taskId mismatch');
  if (row.classification !== 'HARDENING_FOUNDATION_ONLY') errors.push('classification mismatch');
  if (!row.runtimeUser || !row.runtimeGroup) errors.push('runtime user/group required');
  if (row.rootExecutionAllowed !== false) errors.push('rootExecutionAllowed must be false');
  if (row.userCreationPerformed !== false) errors.push('userCreationPerformed must be false');
  if (row.groupCreationPerformed !== false) errors.push('groupCreationPerformed must be false');
  if (row.realOwnershipChangePerformed !== false) errors.push('realOwnershipChangePerformed must be false');
  if (row.productionHardeningApplied !== false) errors.push('productionHardeningApplied must be false');
  if (row.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  return { ok: errors.length === 0, errors };
}

export function loadFilesystemOwnershipPolicy(
  pathValue: string = resolve(HARDENING_ROOT, 'FILESYSTEM_OWNERSHIP_POLICY.edge.json'),
): FilesystemOwnershipPolicy {
  return readJson<FilesystemOwnershipPolicy>(pathValue);
}

export function loadPermissionMatrix(
  pathValue: string = resolve(HARDENING_ROOT, 'PERMISSION_MATRIX.edge.json'),
): PermissionMatrix {
  return readJson<PermissionMatrix>(pathValue);
}

export function loadSensitiveFilePolicy(
  pathValue: string = resolve(HARDENING_ROOT, 'SENSITIVE_FILE_POLICY.edge.json'),
): SensitiveFilePolicy {
  return readJson<SensitiveFilePolicy>(pathValue);
}

export function loadSystemdHardeningPolicy(
  pathValue: string = resolve(HARDENING_ROOT, 'SYSTEMD_HARDENING.edge.json'),
): SystemdHardeningPolicy {
  return readJson<SystemdHardeningPolicy>(pathValue);
}

export function validatePermissionMode(mode: string): boolean {
  if (!modeLooksSafe(mode)) return false;
  const forbidden = new Set(['0777', '0666']);
  if (forbidden.has(mode)) return false;
  return true;
}

export function validateFilesystemPolicy(
  filesystemPolicy: FilesystemOwnershipPolicy,
  permissionMatrix: PermissionMatrix,
): ValidationResult {
  const errors: string[] = [];
  for (const entry of filesystemPolicy.entries) {
    if (!validatePermissionMode(entry.directoryMode)) errors.push(`unsafe directory mode: ${entry.path}`);
    if (!validatePermissionMode(entry.fileMode)) errors.push(`unsafe file mode: ${entry.path}`);
    if (
      entry.classification === 'IMMUTABLE_RELEASE' &&
      (entry.writableByRuntime !== false || entry.mutable !== false)
    ) {
      errors.push('immutable release must not be runtime writable');
    }
    if (entry.classification === 'POINTER' && entry.symlinkAllowed !== true) {
      errors.push('pointer path must allow symlink');
    }
    if (entry.classification === 'SECRET_MATERIAL' || entry.classification === 'CERTIFICATE_MATERIAL') {
      if (!(entry.fileMode === '0600' || entry.fileMode === '0400')) {
        errors.push(`sensitive material file mode too permissive: ${entry.path}`);
      }
    }
  }
  for (const forbiddenMode of permissionMatrix.forbiddenModes) {
    if (!['0777', '0666'].includes(forbiddenMode)) {
      errors.push(`unexpected forbidden mode value: ${forbiddenMode}`);
    }
  }
  return { ok: errors.length === 0, errors };
}

export function validateSymlinkTarget(baseRoot: string, symlinkPath: string): ValidationResult {
  const errors: string[] = [];
  const base = assertInsideEdge(baseRoot);
  const link = assertInsideEdge(symlinkPath);
  const linkStat = lstatSync(link);
  if (!linkStat.isSymbolicLink()) {
    errors.push('symlinkPath is not symlink');
    return { ok: false, errors };
  }
  const real = realpathSync(link);
  if (!real.startsWith(base + sep) && real !== base) {
    errors.push('symlink target escapes base root');
  }
  const forbiddenPrefixes = ['/etc/', '/opt/', '/var/', '/usr/', '/System/', '/Library/', '/Users/'];
  if (forbiddenPrefixes.some((p) => real.startsWith(p))) {
    errors.push('symlink target points to forbidden system path');
  }
  return { ok: errors.length === 0, errors };
}

export function evaluateRuntimeHardeningAcceptance(
  identity: RuntimeIdentityPolicy,
  filesystem: FilesystemOwnershipPolicy,
  permission: PermissionMatrix,
  sensitive: SensitiveFilePolicy,
  systemd: SystemdHardeningPolicy,
): RuntimeHardeningAcceptanceResult {
  const identityValidation = validateRuntimeIdentityPolicy(identity);
  const filesystemValidation = validateFilesystemPolicy(filesystem, permission);
  if (!identityValidation.ok || !filesystemValidation.ok) {
    return 'HARDENING_FOUNDATION_REJECTED';
  }
  if (sensitive.realMaterialPresent) {
    return 'HARDENING_FOUNDATION_REJECTED';
  }
  if (
    sensitive.entries.some(
      (row) => row.repositoryTrackingAllowed || row.plaintextAllowed || row.maxFileMode === '0644',
    )
  ) {
    return 'HARDENING_FOUNDATION_REJECTED';
  }
  if (systemd.recommendations.some((row) => row.appliedByC4_04 !== false)) {
    return 'HARDENING_FOUNDATION_REJECTED';
  }
  return 'HARDENING_FOUNDATION_ACCEPTED_NOT_APPLIED';
}
