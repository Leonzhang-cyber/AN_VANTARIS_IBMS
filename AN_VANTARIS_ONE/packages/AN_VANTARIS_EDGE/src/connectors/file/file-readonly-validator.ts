import { lstatSync, realpathSync, statSync } from 'node:fs';
import { extname, relative, resolve, sep } from 'node:path';

import type {
  FileCandidateValidation,
  FileQuarantineDecision,
  FileQuarantineReason,
  FileReadOnlyPolicy,
  FileStabilityEvaluation,
  ValidationResult,
} from './file-readonly-types.js';

function isInsideRoot(candidate: string, root: string): boolean {
  const rel = relative(root, candidate);
  return rel === '' || (!rel.startsWith('..') && !rel.includes(`..${sep}`));
}

function pathHasTraversalSegments(inputPath: string): boolean {
  return inputPath.split(/[\\/]+/).some((segment) => segment === '..');
}

function canonicalRoot(root: string): string {
  try {
    return realpathSync(root);
  } catch {
    return resolve(root);
  }
}

function pathHasSymlink(candidate: string, allowedRoot: string): boolean {
  const resolvedRoot = resolve(allowedRoot);
  const resolvedCandidate = resolve(candidate);
  if (!isInsideRoot(resolvedCandidate, resolvedRoot)) return true;
  const rel = relative(resolvedRoot, resolvedCandidate);
  if (rel === '') return false;
  const segments = rel.split(/[\\/]+/).filter(Boolean);
  let current = resolvedRoot;
  for (const segment of segments) {
    current = resolve(current, segment);
    const lst = lstatSync(current);
    if (lst.isSymbolicLink()) return true;
  }
  return false;
}

export function resolveAllowedFilePath(inputPath: string, policy: FileReadOnlyPolicy): string {
  const candidate = resolve(inputPath);
  if (policy.rejectTraversal && pathHasTraversalSegments(inputPath)) throw new Error('PATH_TRAVERSAL_DETECTED');
  const allowedRoots = policy.allowedRoots.map((root) => canonicalRoot(root));
  const deniedRoots = policy.deniedRoots.map((root) => canonicalRoot(root));
  const allowed = allowedRoots.find((root) => isInsideRoot(candidate, root));
  if (!allowed) throw new Error('PATH_OUTSIDE_ALLOWLIST');
  if (policy.rejectSymlinks && pathHasSymlink(candidate, allowed)) throw new Error('SYMLINK_REJECTED');
  const canonicalCandidate = canonicalizePathForEvidence(candidate);
  if (!isInsideRoot(canonicalCandidate, allowed)) throw new Error('PATH_OUTSIDE_ALLOWLIST');
  for (const deniedRoot of deniedRoots) {
    if (allowedRoots.some((allowedRoot) => isInsideRoot(allowedRoot, deniedRoot))) {
      continue;
    }
    if (isInsideRoot(canonicalCandidate, deniedRoot)) throw new Error('PATH_OUTSIDE_ALLOWLIST');
  }
  return canonicalCandidate;
}

export function validateFileCandidate(inputPath: string, policy: FileReadOnlyPolicy): FileCandidateValidation {
  const errors: string[] = [];
  let canonicalPath = '';
  try {
    canonicalPath = resolveAllowedFilePath(inputPath, policy);
  } catch (error) {
    const reason = (error as Error).message as FileQuarantineReason;
    return { ok: false, canonicalPath: resolve(inputPath), extension: extname(inputPath).toLowerCase(), sizeBytes: 0, quarantineReason: reason, errors: [reason] };
  }

  const lst = lstatSync(canonicalPath);
  if (policy.rejectSymlinks && lst.isSymbolicLink()) errors.push('SYMLINK_REJECTED');
  const st = statSync(canonicalPath);
  if (policy.rejectDirectories && st.isDirectory()) errors.push('NON_REGULAR_FILE');
  if (policy.requireRegularFile && !st.isFile()) errors.push('NON_REGULAR_FILE');
  if (policy.rejectSockets && lst.isSocket()) errors.push('NON_REGULAR_FILE');
  if (policy.rejectDeviceFiles && (lst.isBlockDevice() || lst.isCharacterDevice())) errors.push('NON_REGULAR_FILE');
  const extension = extname(canonicalPath).toLowerCase();
  if (st.isFile() && !policy.allowedExtensions.includes(extension)) errors.push('FILE_TYPE_NOT_ALLOWED');
  const containingRoot = policy.allowedRoots.map((root) => canonicalRoot(root)).find((root) => isInsideRoot(canonicalPath, root));
  const relativeToRoot = containingRoot ? relative(containingRoot, canonicalPath) : canonicalPath;
  if (policy.rejectHiddenFiles && relativeToRoot.split(/[\\/]+/).some((segment) => segment.startsWith('.') && segment.length > 1)) {
    errors.push('HIDDEN_FILE_REJECTED');
  }
  if (st.size > policy.maxFileSizeBytes) errors.push('FILE_TOO_LARGE');

  return {
    ok: errors.length === 0,
    canonicalPath,
    extension,
    sizeBytes: st.size,
    quarantineReason: errors[0] as FileQuarantineReason | undefined,
    errors,
  };
}

export async function evaluateFileStability(filePath: string, policy: FileReadOnlyPolicy): Promise<FileStabilityEvaluation> {
  const first = statSync(filePath);
  await new Promise((resolvePromise) => setTimeout(resolvePromise, policy.stableObservationWindowMs));
  const second = statSync(filePath);
  const stable = first.isFile() && second.isFile() && first.size === second.size && first.mtimeMs === second.mtimeMs && first.ino === second.ino;
  if (!stable) {
    return {
      stable: false,
      reason: 'FILE_NOT_STABLE',
      firstSize: first.size,
      secondSize: second.size,
      firstMtimeMs: first.mtimeMs,
      secondMtimeMs: second.mtimeMs,
    };
  }
  return {
    stable: true,
    firstSize: first.size,
    secondSize: second.size,
    firstMtimeMs: first.mtimeMs,
    secondMtimeMs: second.mtimeMs,
  };
}

export function evaluateQuarantineDecision(reason: FileQuarantineReason | undefined, canonicalPath: string, policy: FileReadOnlyPolicy): FileQuarantineDecision {
  if (!reason) return { quarantine: false, mode: policy.quarantineMode };
  return {
    quarantine: true,
    mode: policy.quarantineMode,
    reason,
    suggestedTarget: `${canonicalPath}.quarantine`,
  };
}

export function validatePathSafetyConfiguration(policy: FileReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (!policy.rejectTraversal) errors.push('rejectTraversal must be true');
  if (!policy.rejectSymlinks) errors.push('rejectSymlinks must be true');
  if (!policy.requireRegularFile) errors.push('requireRegularFile must be true');
  if (policy.networkFilesystemAllowed) errors.push('networkFilesystemAllowed must be false');
  return { ok: errors.length === 0, errors };
}

export function detectNetworkFilesystemDisallowed(pathValue: string, policy: FileReadOnlyPolicy): boolean {
  if (policy.networkFilesystemAllowed) return false;
  const lowered = pathValue.toLowerCase();
  return lowered.startsWith('//') || lowered.startsWith('\\\\') || lowered.includes('/net/') || lowered.includes('nfs') || lowered.includes('smb');
}

export function canonicalizePathForEvidence(pathValue: string): string {
  try {
    return realpathSync(pathValue);
  } catch {
    return resolve(pathValue);
  }
}
