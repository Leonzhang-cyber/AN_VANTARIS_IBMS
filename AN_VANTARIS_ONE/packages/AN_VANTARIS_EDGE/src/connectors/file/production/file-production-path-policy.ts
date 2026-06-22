import { createHash } from 'node:crypto';
import { lstat, realpath } from 'node:fs/promises';
import { extname, join, relative, resolve, sep } from 'node:path';

import type { FileProductionErrorCode, FileProductionFormat } from './file-production-adapter.types.js';

export const FILE_PRODUCTION_DENIED_ROOTS = [
  '/',
  '~',
  '/etc',
  '/private',
  '/System',
  '/Library',
  '/usr',
  '/bin',
  '/sbin',
  '/dev',
  '/proc',
  '/sys',
  '/var',
  '/tmp',
] as const;

const FORMAT_EXTENSIONS: Record<FileProductionFormat, readonly string[]> = {
  json: ['.json'],
  jsonl: ['.jsonl'],
  csv: ['.csv'],
};

function isInsideRoot(candidate: string, root: string): boolean {
  const rel = relative(root, candidate);
  return rel === '' || (!rel.startsWith('..') && !rel.includes(`..${sep}`));
}

function pathHasTraversalSegments(inputPath: string): boolean {
  return inputPath.split(/[\\/]+/).some((segment) => segment === '..');
}

function normalizeDeniedRoot(root: string, homeDir: string | undefined): string {
  if (root === '~') return homeDir ? resolve(homeDir) : root;
  return resolve(root);
}

export function createPathReferenceId(rootReferenceId: string, inputRelativePath: string): string {
  const digest = createHash('sha256')
    .update(`${rootReferenceId}\0${inputRelativePath}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `file-root:${rootReferenceId}:${digest}`;
}

export function validateRelativeInputPath(inputRelativePath: string): FileProductionErrorCode | null {
  if (!inputRelativePath || inputRelativePath.trim().length === 0) return 'FILE_PATH_NOT_ALLOWLISTED';
  if (inputRelativePath.startsWith('/') || /^[a-zA-Z]:/.test(inputRelativePath)) return 'FILE_PATH_NOT_ALLOWLISTED';
  if (pathHasTraversalSegments(inputRelativePath)) return 'FILE_PATH_TRAVERSAL_REJECTED';
  return null;
}

export async function resolveAllowlistedProductionPath(input: {
  allowlistedRoot: string;
  inputRelativePath: string;
  format: FileProductionFormat;
  homeDir?: string;
}): Promise<{ ok: true; canonicalPath: string; relativeAllowlistPath: string } | { ok: false; errorCode: FileProductionErrorCode }> {
  const relError = validateRelativeInputPath(input.inputRelativePath);
  if (relError) return { ok: false, errorCode: relError };

  const allowedRoot = resolve(input.allowlistedRoot);
  for (const denied of FILE_PRODUCTION_DENIED_ROOTS) {
    const deniedRoot = normalizeDeniedRoot(denied, input.homeDir);
    if (denied === '/') {
      if (allowedRoot === '/') return { ok: false, errorCode: 'FILE_PATH_NOT_ALLOWLISTED' };
      continue;
    }
    if (deniedRoot === allowedRoot || isInsideRoot(allowedRoot, deniedRoot)) {
      return { ok: false, errorCode: 'FILE_PATH_NOT_ALLOWLISTED' };
    }
  }

  let canonicalRoot: string;
  try {
    canonicalRoot = await realpath(allowedRoot);
  } catch {
    return { ok: false, errorCode: 'FILE_PATH_NOT_ALLOWLISTED' };
  }

  const candidate = resolve(canonicalRoot, input.inputRelativePath);
  if (!isInsideRoot(candidate, canonicalRoot)) return { ok: false, errorCode: 'FILE_PATH_TRAVERSAL_REJECTED' };

  const relSegments = relative(canonicalRoot, candidate).split(/[\\/]+/).filter(Boolean);
  let walk = canonicalRoot;
  for (const segment of relSegments) {
    walk = join(walk, segment);
    try {
      const lst = await lstat(walk);
      if (lst.isSymbolicLink()) return { ok: false, errorCode: 'FILE_SYMLINK_REJECTED' };
    } catch {
      return { ok: false, errorCode: 'FILE_NOT_FOUND' };
    }
  }

  let canonicalPath: string;
  try {
    canonicalPath = await realpath(candidate);
  } catch {
    return { ok: false, errorCode: 'FILE_NOT_FOUND' };
  }

  if (!isInsideRoot(canonicalPath, canonicalRoot)) return { ok: false, errorCode: 'FILE_PATH_TRAVERSAL_REJECTED' };

  const extension = extname(canonicalPath).toLowerCase();
  if (!FORMAT_EXTENSIONS[input.format].includes(extension)) return { ok: false, errorCode: 'FILE_FORMAT_NOT_ALLOWED' };

  return {
    ok: true,
    canonicalPath,
    relativeAllowlistPath: relative(canonicalRoot, canonicalPath),
  };
}

export async function inspectRegularFilePath(canonicalPath: string): Promise<{ ok: true; sizeBytes: number; dev: number; ino: number } | { ok: false; errorCode: FileProductionErrorCode }> {
  try {
    const lst = await lstat(canonicalPath);
    if (lst.isSymbolicLink()) return { ok: false, errorCode: 'FILE_SYMLINK_REJECTED' };
    if (lst.isDirectory()) return { ok: false, errorCode: 'FILE_NOT_REGULAR' };
    if (lst.isSocket() || lst.isFIFO()) return { ok: false, errorCode: 'FILE_SPECIAL_TYPE_REJECTED' };
    if (lst.isBlockDevice() || lst.isCharacterDevice()) return { ok: false, errorCode: 'FILE_SPECIAL_TYPE_REJECTED' };
    if (!lst.isFile()) return { ok: false, errorCode: 'FILE_NOT_REGULAR' };
    return { ok: true, sizeBytes: lst.size, dev: lst.dev, ino: lst.ino };
  } catch {
    return { ok: false, errorCode: 'FILE_NOT_FOUND' };
  }
}
