import { open } from 'node:fs/promises';

import { parseCsvImportFile, parseJsonImportFile } from '../file-import-parser.js';

import type {
  FileProductionAdapterConfig,
  FileProductionErrorCode,
  FileProductionReadOnlyAdapter,
  FileProductionReadRequest,
  FileProductionReadResult,
} from './file-production-adapter.types.js';
import {
  createPathReferenceId,
  inspectRegularFilePath,
  resolveAllowlistedProductionPath,
} from './file-production-path-policy.js';
import {
  buildFoundationPolicyForProduction,
  containsDangerousKey,
  normalizeCsvRecords,
  normalizeRecordsFromObjects,
  runFoundationValidation,
  validateFoundationJsonRecord,
  validateProductionAdapterConfig,
} from './file-production-normalizer.js';

function stripUtf8Bom(content: string): string {
  return content.charCodeAt(0) === 0xfeff ? content.slice(1) : content;
}

function splitCsvLine(line: string): string[] {
  const parts: string[] = [];
  let current = '';
  let inQuote = false;
  for (let index = 0; index < line.length; index += 1) {
    const char = line[index];
    if (char === '"') {
      const next = line[index + 1];
      if (inQuote && next === '"') {
        current += '"';
        index += 1;
      } else {
        inQuote = !inQuote;
      }
      continue;
    }
    if (char === ',' && !inQuote) {
      parts.push(current);
      current = '';
      continue;
    }
    if (char === '\n' || char === '\r') throw new Error('FILE_CSV_INVALID');
    current += char;
  }
  if (inQuote) throw new Error('FILE_CSV_INVALID');
  parts.push(current);
  return parts;
}

function parseProductionCsv(content: string, config: FileProductionAdapterConfig): { headers: string[]; rows: Record<string, string>[] } {
  const normalized = stripUtf8Bom(content.replace(/\r\n/g, '\n'));
  const lines = normalized.split('\n').filter((line) => line.length > 0);
  if (lines.length === 0) throw new Error('FILE_CSV_INVALID');
  if (lines.some((line) => line.length > config.maxLineBytes)) throw new Error('FILE_LINE_LIMIT_EXCEEDED');
  const headers = splitCsvLine(lines[0]).map((column) => column.trim());
  if (headers.length === 0 || headers.some((column) => column.length === 0)) throw new Error('FILE_CSV_INVALID');
  if (headers.length > config.maxCsvColumns) throw new Error('FILE_CSV_INVALID');
  const rows: Record<string, string>[] = [];
  for (const line of lines.slice(1)) {
    if (line.length > config.maxLineBytes) throw new Error('FILE_LINE_LIMIT_EXCEEDED');
    const cells = splitCsvLine(line);
    if (cells.length !== headers.length) throw new Error('FILE_CSV_INVALID');
    const row: Record<string, string> = {};
    for (let index = 0; index < headers.length; index += 1) {
      row[headers[index]] = cells[index];
    }
    rows.push(row);
  }
  if (rows.length > config.maxRecordCount) throw new Error('FILE_RECORD_LIMIT_EXCEEDED');
  return { headers, rows };
}

function parseProductionJson(content: string, config: FileProductionAdapterConfig): Record<string, unknown>[] {
  const normalized = stripUtf8Bom(content);
  if (normalized.trim().length === 0) throw new Error('FILE_JSON_INVALID');
  if (Buffer.byteLength(normalized, 'utf8') > config.maxFileBytes) throw new Error('FILE_SIZE_LIMIT_EXCEEDED');
  const policy = buildFoundationPolicyForProduction('', config);
  const parsed = parseJsonImportFile(normalized, policy);
  return [...parsed.records];
}

function parseProductionJsonl(
  content: string,
  allowlistedRoot: string,
  config: FileProductionAdapterConfig,
): Record<string, unknown>[] {
  const normalized = stripUtf8Bom(content.replace(/\r\n/g, '\n'));
  if (normalized.trim().length === 0) throw new Error('FILE_JSON_INVALID');
  const lines = normalized.split('\n');
  const records: Record<string, unknown>[] = [];
  for (let lineNumber = 1; lineNumber <= lines.length; lineNumber += 1) {
    const line = lines[lineNumber - 1];
    if (line.length === 0) continue;
    if (line.length > config.maxLineBytes) throw new Error(`FILE_LINE_LIMIT_EXCEEDED:${lineNumber}`);
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch {
      throw new Error(`FILE_JSONL_INVALID:${lineNumber}`);
    }
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      throw new Error(`FILE_JSONL_INVALID:${lineNumber}`);
    }
    const record = parsed as Record<string, unknown>;
    if (containsDangerousKey(record, 0, config.maxJsonDepth)) {
      throw new Error(`FILE_DANGEROUS_KEY_REJECTED:${lineNumber}`);
    }
    const foundationError = validateFoundationJsonRecord(record, allowlistedRoot, config);
    if (foundationError) throw new Error(`FILE_FOUNDATION_VALIDATION_FAILED:${lineNumber}`);
    records.push(record);
    if (records.length > config.maxRecordCount) throw new Error('FILE_RECORD_LIMIT_EXCEEDED');
  }
  if (records.length === 0) throw new Error('FILE_JSON_INVALID');
  return records;
}

async function readBoundedUtf8File(canonicalPath: string, maxFileBytes: number, preOpen: { dev: number; ino: number; sizeBytes: number }): Promise<string> {
  const handle = await open(canonicalPath, 'r');
  try {
    const postStat = await handle.stat();
    if (postStat.dev !== preOpen.dev || postStat.ino !== preOpen.ino) {
      throw new Error('FILE_CHANGED_DURING_OPEN');
    }
    if (!postStat.isFile()) throw new Error('FILE_NOT_REGULAR');
    if (postStat.size !== preOpen.sizeBytes) throw new Error('FILE_CHANGED_DURING_OPEN');
    if (postStat.size > maxFileBytes) throw new Error('FILE_SIZE_LIMIT_EXCEEDED');
    const buffer = Buffer.alloc(postStat.size);
    const { bytesRead } = await handle.read(buffer, 0, postStat.size, 0);
    if (bytesRead !== postStat.size) throw new Error('FILE_READ_FAILED');
    try {
      new TextDecoder('utf-8', { fatal: true }).decode(buffer);
    } catch {
      throw new Error('FILE_ENCODING_INVALID');
    }
    return buffer.toString('utf8');
  } finally {
    await handle.close();
  }
}

/** Validation-harness export for TOCTOU negative coverage; not registered in runtime. */
export async function fileProductionHarnessReadBoundedUtf8File(
  canonicalPath: string,
  maxFileBytes: number,
  preOpen: { dev: number; ino: number; sizeBytes: number },
): Promise<string> {
  return readBoundedUtf8File(canonicalPath, maxFileBytes, preOpen);
}

function mapParserError(error: unknown): { errorCode: FileProductionErrorCode; lineNumber?: number } {
  const message = error instanceof Error ? error.message : 'FILE_READ_FAILED';
  if (message.startsWith('FILE_JSONL_INVALID:')) {
    return { errorCode: 'FILE_JSONL_INVALID', lineNumber: Number(message.split(':')[1]) || undefined };
  }
  if (message.startsWith('FILE_DANGEROUS_KEY_REJECTED:')) {
    return { errorCode: 'FILE_DANGEROUS_KEY_REJECTED', lineNumber: Number(message.split(':')[1]) || undefined };
  }
  if (message.startsWith('FILE_FOUNDATION_VALIDATION_FAILED:')) {
    return { errorCode: 'FILE_FOUNDATION_VALIDATION_FAILED', lineNumber: Number(message.split(':')[1]) || undefined };
  }
  if (message.startsWith('FILE_LINE_LIMIT_EXCEEDED:')) {
    return { errorCode: 'FILE_LINE_LIMIT_EXCEEDED', lineNumber: Number(message.split(':')[1]) || undefined };
  }
  if (message === 'MALFORMED_JSON' || message === 'FILE_JSON_INVALID') return { errorCode: 'FILE_JSON_INVALID' };
  if (message === 'MALFORMED_CSV' || message === 'FILE_CSV_INVALID') return { errorCode: 'FILE_CSV_INVALID' };
  if (message === 'FILE_SIZE_LIMIT_EXCEEDED') return { errorCode: 'FILE_SIZE_LIMIT_EXCEEDED' };
  if (message === 'FILE_RECORD_LIMIT_EXCEEDED') return { errorCode: 'FILE_RECORD_LIMIT_EXCEEDED' };
  if (message === 'FILE_CHANGED_DURING_OPEN') return { errorCode: 'FILE_CHANGED_DURING_OPEN' };
  if (message === 'FILE_NOT_REGULAR') return { errorCode: 'FILE_NOT_REGULAR' };
  if (message === 'FILE_READ_FAILED') return { errorCode: 'FILE_READ_FAILED' };
  if (message === 'FILE_ENCODING_INVALID') return { errorCode: 'FILE_ENCODING_INVALID' };
  return { errorCode: 'FILE_READ_FAILED' };
}

async function readOnceInternal(request: FileProductionReadRequest): Promise<FileProductionReadResult> {
  const configError = validateProductionAdapterConfig(request.config);
  if (configError) {
    return { ok: false, errorCode: configError, pathReferenceId: createPathReferenceId(request.config.rootReferenceId, request.config.inputRelativePath) };
  }

  const allowlistedRoot = request.resolveRoot(request.config.rootReferenceId);
  if (!allowlistedRoot) {
    return {
      ok: false,
      errorCode: 'FILE_PATH_NOT_ALLOWLISTED',
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, request.config.inputRelativePath),
    };
  }

  const resolved = await resolveAllowlistedProductionPath({
    allowlistedRoot,
    inputRelativePath: request.config.inputRelativePath,
    format: request.config.format,
  });
  if (!resolved.ok) {
    return {
      ok: false,
      errorCode: resolved.errorCode,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, request.config.inputRelativePath),
    };
  }

  const inspected = await inspectRegularFilePath(resolved.canonicalPath);
  if (!inspected.ok) {
    return {
      ok: false,
      errorCode: inspected.errorCode,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
    };
  }
  if (inspected.sizeBytes > request.config.maxFileBytes) {
    return {
      ok: false,
      errorCode: 'FILE_SIZE_LIMIT_EXCEEDED',
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
    };
  }

  const foundationError = runFoundationValidation(resolved.canonicalPath, allowlistedRoot, request.config);
  if (foundationError) {
    return {
      ok: false,
      errorCode: foundationError,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
    };
  }

  let content: string;
  try {
    content = await readBoundedUtf8File(resolved.canonicalPath, request.config.maxFileBytes, inspected);
  } catch (error) {
    const mapped = mapParserError(error);
    return {
      ok: false,
      errorCode: mapped.errorCode,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
      lineNumber: mapped.lineNumber,
    };
  }

  try {
    if (request.config.format === 'csv') {
      const policy = buildFoundationPolicyForProduction(allowlistedRoot, request.config);
      const foundationParsed = parseCsvImportFile(content, policy);
      const normalized = normalizeCsvRecords(foundationParsed.headers, foundationParsed.records, request.config);
      if (!normalized.ok) {
        return { ok: false, errorCode: normalized.errorCode, pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath) };
      }
      return {
        ok: true,
        pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
        relativeAllowlistPath: resolved.relativeAllowlistPath,
        format: request.config.format,
        recordCount: normalized.records.length,
        records: normalized.records,
        foundationAccepted: true,
      };
    }

    const objects = request.config.format === 'jsonl'
      ? parseProductionJsonl(content, allowlistedRoot, request.config)
      : parseProductionJson(content, request.config);
    const normalized = normalizeRecordsFromObjects(objects, request.config);
    if (!normalized.ok) {
      return {
        ok: false,
        errorCode: normalized.errorCode,
        pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
        lineNumber: normalized.lineNumber,
      };
    }
    return {
      ok: true,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
      relativeAllowlistPath: resolved.relativeAllowlistPath,
      format: request.config.format,
      recordCount: normalized.records.length,
      records: normalized.records,
      foundationAccepted: true,
    };
  } catch (error) {
    const mapped = mapParserError(error);
    return {
      ok: false,
      errorCode: mapped.errorCode,
      pathReferenceId: createPathReferenceId(request.config.rootReferenceId, resolved.relativeAllowlistPath),
      lineNumber: mapped.lineNumber,
    };
  }
}

export function createFileProductionReadOnlyAdapter(): FileProductionReadOnlyAdapter {
  return {
    readOnce: async (request: FileProductionReadRequest): Promise<FileProductionReadResult> => {
      const timeoutMs = request.config.maxProcessingMilliseconds;
      let timer: NodeJS.Timeout | undefined;
      try {
        return await Promise.race([
          readOnceInternal(request),
          new Promise<FileProductionReadResult>((resolvePromise) => {
            timer = setTimeout(() => {
              resolvePromise({
                ok: false,
                errorCode: 'FILE_READ_TIMEOUT',
                pathReferenceId: createPathReferenceId(request.config.rootReferenceId, request.config.inputRelativePath),
              });
            }, timeoutMs);
          }),
        ]);
      } finally {
        if (timer) clearTimeout(timer);
      }
    },
  };
}

export const fileProductionReadOnlyAdapter: FileProductionReadOnlyAdapter = createFileProductionReadOnlyAdapter();
