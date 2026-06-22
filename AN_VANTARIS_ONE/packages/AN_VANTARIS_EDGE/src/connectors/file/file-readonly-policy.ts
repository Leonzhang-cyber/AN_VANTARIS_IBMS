import type { FileReadOnlyPolicy, ValidationResult } from './file-readonly-types.js';
import { relative, resolve, sep } from 'node:path';

const ALLOWED_EXTENSIONS = new Set(['.json', '.csv']);

function isInsideRoot(candidate: string, root: string): boolean {
  const normalizedCandidate = resolve(candidate);
  const normalizedRoot = resolve(root);
  const rel = relative(normalizedRoot, normalizedCandidate);
  return rel === '' || (!rel.startsWith('..') && !rel.includes(`..${sep}`));
}

export function validateFileReadOnlyPolicy(policy: FileReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-01') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_LOCAL_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (!Array.isArray(policy.allowedRoots) || policy.allowedRoots.length === 0) errors.push('allowedRoots required');
  if (policy.allowedRoots.some((root) => resolve(root) === resolve('/'))) errors.push('allowedRoots must not be filesystem root');
  if (policy.deniedRoots.some((root) => resolve(root) === resolve('/'))) errors.push('deniedRoots must not include filesystem root');
  for (const allowedRoot of policy.allowedRoots) {
    for (const deniedRoot of policy.deniedRoots) {
      if (isInsideRoot(resolve(allowedRoot), resolve(deniedRoot))) {
        errors.push(`deniedRoots overlaps allowedRoots: ${deniedRoot}`);
      }
    }
  }
  if (!Array.isArray(policy.allowedExtensions) || policy.allowedExtensions.length === 0) errors.push('allowedExtensions required');
  if (policy.allowedExtensions.some((extension) => !ALLOWED_EXTENSIONS.has(extension))) {
    errors.push('allowedExtensions must be .json/.csv only in foundation');
  }
  if (!(policy.maxFileSizeBytes > 0)) errors.push('maxFileSizeBytes must be positive');
  if (!policy.rejectTraversal) errors.push('rejectTraversal must be true');
  if (!policy.rejectSymlinks) errors.push('rejectSymlinks must be true');
  if (!policy.rejectDeviceFiles) errors.push('rejectDeviceFiles must be true');
  if (!policy.rejectSockets) errors.push('rejectSockets must be true');
  if (!policy.requireRegularFile) errors.push('requireRegularFile must be true');
  if (!policy.requireStableSize) errors.push('requireStableSize must be true');
  if (policy.duplicateDetectionMode !== 'SHA256_LOCAL_FOUNDATION') errors.push('duplicateDetectionMode mismatch');
  if (policy.quarantineMode !== 'DECISION_ONLY') errors.push('quarantineMode mismatch');
  if (policy.sourceMutationAllowed) errors.push('sourceMutationAllowed must be false');
  if (policy.sourceDeletionAllowed) errors.push('sourceDeletionAllowed must be false');
  if (policy.sourceRenameAllowed) errors.push('sourceRenameAllowed must be false');
  if (policy.networkFilesystemAllowed) errors.push('networkFilesystemAllowed must be false');
  if (!policy.csvHeaderRequired) errors.push('csvHeaderRequired must be true');
  if (policy.csvDelimiter !== ',') errors.push('csvDelimiter must be comma');
  if (policy.csvMaxRows < 1) errors.push('csvMaxRows must be >=1');
  if (!policy.jsonAllowObject && !policy.jsonAllowArray) errors.push('json must allow object or array');
  if (policy.jsonAllowScalar) errors.push('jsonAllowScalar must be false in foundation');
  if (policy.jsonMaxDepth < 1) errors.push('jsonMaxDepth must be >=1');
  return { ok: errors.length === 0, errors };
}
