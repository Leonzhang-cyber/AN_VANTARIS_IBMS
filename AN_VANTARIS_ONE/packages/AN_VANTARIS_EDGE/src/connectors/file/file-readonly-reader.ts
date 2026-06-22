import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { basename, extname, relative, resolve } from 'node:path';

import { parseCsvImportFile, parseJsonImportFile } from './file-import-parser.js';
import type {
  FileDigestIdentity,
  FileDuplicateResult,
  FileImportAcceptanceResult,
  FileReadOnlyIngestionResult,
  FileReadOnlyPolicy,
  ParsedImportResult,
} from './file-readonly-types.js';
import {
  canonicalizePathForEvidence,
  detectNetworkFilesystemDisallowed,
  evaluateFileStability,
  evaluateQuarantineDecision,
  validateFileCandidate,
} from './file-readonly-validator.js';

export function calculateFileDigest(filePath: string): FileDigestIdentity {
  const content = readFileSync(filePath);
  const digestSha256 = createHash('sha256').update(content).digest('hex');
  return {
    digestSha256,
    sizeBytes: content.byteLength,
    extension: extname(filePath).toLowerCase(),
  };
}

export function detectDuplicateFile(identity: FileDigestIdentity, seen: Set<string>): FileDuplicateResult {
  const identityKey = `${identity.digestSha256}:${identity.sizeBytes}:${identity.extension}:${identity.relativePath ?? ''}`;
  const duplicate = seen.has(identityKey);
  if (!duplicate) seen.add(identityKey);
  return { duplicate, identityKey };
}

export async function readFileCandidateReadOnly(
  inputPath: string,
  policy: FileReadOnlyPolicy,
  seen: Set<string>,
): Promise<FileReadOnlyIngestionResult> {
  if (detectNetworkFilesystemDisallowed(inputPath, policy)) {
    return {
      accepted: false,
      canonicalPath: resolve(inputPath),
      duplicate: { duplicate: false, identityKey: '' },
      quarantineDecision: evaluateQuarantineDecision('NETWORK_FILESYSTEM_NOT_ALLOWED', resolve(inputPath), policy),
      errors: ['NETWORK_FILESYSTEM_NOT_ALLOWED'],
    };
  }

  const candidate = validateFileCandidate(inputPath, policy);
  const canonicalPath = canonicalizePathForEvidence(candidate.canonicalPath);
  if (!candidate.ok) {
    return {
      accepted: false,
      canonicalPath,
      duplicate: { duplicate: false, identityKey: '' },
      quarantineDecision: evaluateQuarantineDecision(candidate.quarantineReason, canonicalPath, policy),
      errors: [...candidate.errors],
    };
  }

  const stability = await evaluateFileStability(canonicalPath, policy);
  if (!stability.stable) {
    return {
      accepted: false,
      canonicalPath,
      duplicate: { duplicate: false, identityKey: '' },
      quarantineDecision: evaluateQuarantineDecision('FILE_NOT_STABLE', canonicalPath, policy),
      errors: ['FILE_NOT_STABLE'],
    };
  }

  const digest = calculateFileDigest(canonicalPath);
  const root = policy.allowedRoots.map((item) => resolve(item)).find((item) => canonicalPath.startsWith(item));
  const duplicate = detectDuplicateFile(
    {
      ...digest,
      relativePath: root ? relative(root, canonicalPath) : basename(canonicalPath),
    },
    seen,
  );

  if (duplicate.duplicate) {
    return {
      accepted: false,
      canonicalPath,
      duplicate,
      quarantineDecision: evaluateQuarantineDecision('DUPLICATE_DETECTED', canonicalPath, policy),
      errors: ['DUPLICATE_DETECTED'],
    };
  }

  const content = readFileSync(canonicalPath, 'utf8');
  let parsed: ParsedImportResult;
  try {
    if (candidate.extension === '.json') {
      parsed = parseJsonImportFile(content, policy);
    } else if (candidate.extension === '.csv') {
      parsed = parseCsvImportFile(content, policy);
    } else {
      return {
        accepted: false,
        canonicalPath,
        duplicate,
        quarantineDecision: evaluateQuarantineDecision('FILE_TYPE_NOT_ALLOWED', canonicalPath, policy),
        errors: ['FILE_TYPE_NOT_ALLOWED'],
      };
    }
  } catch (error) {
    const reason = (error as Error).message === 'MALFORMED_CSV' ? 'MALFORMED_CSV' : 'MALFORMED_JSON';
    return {
      accepted: false,
      canonicalPath,
      duplicate,
      quarantineDecision: evaluateQuarantineDecision(reason, canonicalPath, policy),
      errors: [reason],
    };
  }

  return {
    accepted: true,
    canonicalPath,
    duplicate,
    quarantineDecision: evaluateQuarantineDecision(undefined, canonicalPath, policy),
    parsed,
    errors: [],
  };
}

export function evaluateFileImportAcceptance(results: readonly FileReadOnlyIngestionResult[]): FileImportAcceptanceResult {
  if (results.length === 0) return 'FILE_IMPORT_READ_ONLY_FOUNDATION_REJECTED';
  const allReadOnlySafe = results.every((result) => result.quarantineDecision.mode === 'DECISION_ONLY');
  const anyMutationIndicator = results.some((result) =>
    (result.errors.includes('SOURCE_MUTATED') || result.errors.includes('SOURCE_DELETED') || result.errors.includes('SOURCE_RENAMED')),
  );
  if (!allReadOnlySafe || anyMutationIndicator) return 'FILE_IMPORT_READ_ONLY_FOUNDATION_REJECTED';
  return 'FILE_IMPORT_READ_ONLY_FOUNDATION_ACCEPTED';
}
