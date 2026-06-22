import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type {
  FileImportConfig,
  FileImportError,
  FileImportEvidence,
  FileImportParseResult,
  FileImportRecord,
  FileImportStats,
  FileImportValidationResult,
} from './file-import-types.js';

const DEFAULT_MAX_BYTES = 1024 * 1024;
const DEFAULT_MAX_JSONL_LINES = 5000;

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function isUnder(absolutePath: string, allowedRoot: string): boolean {
  const normalizedRoot = resolve(allowedRoot);
  const normalizedPath = resolve(absolutePath);
  return normalizedPath == normalizedRoot || normalizedPath.startsWith(normalizedRoot + '/');
}

function toRecord(raw: Record<string, unknown>): FileImportRecord {
  const qualityRaw = asString(raw.quality).toLowerCase();
  const quality = qualityRaw == 'bad' || qualityRaw == 'uncertain' ? qualityRaw : 'good';
  const sampleType = asString(raw.sampleType);
  const safeSampleType =
    sampleType == 'telemetry' ||
    sampleType == 'event' ||
    sampleType == 'alarm' ||
    sampleType == 'health' ||
    sampleType == 'evidence'
      ? sampleType
      : undefined;
  return {
    sourceRef: asString(raw.sourceRef),
    pointRef: asString(raw.pointRef),
    value:
      typeof raw.value == 'number' || typeof raw.value == 'string' || typeof raw.value == 'boolean'
        ? raw.value
        : asString(raw.value),
    unit: asString(raw.unit),
    quality,
    observedAt: asString(raw.observedAt),
    assetRef: asString(raw.assetRef),
    metadata: isObject(raw.metadata) ? raw.metadata : {},
    sampleType: safeSampleType,
    message: asString(raw.message) || undefined,
  };
}

export function validateFileImportPath(edgeRoot: string, inputPath: string): FileImportValidationResult & {
  readonly absolutePath: string;
} {
  const resolvedEdgeRoot = resolve(edgeRoot);
  const resolvedInput = resolve(resolvedEdgeRoot, inputPath);
  const allowedConfigSamples = resolve(resolvedEdgeRoot, 'config/samples');
  const allowedRuntimeInput = resolve(resolvedEdgeRoot, '.runtime/input');
  const valid = isUnder(resolvedInput, allowedConfigSamples) || isUnder(resolvedInput, allowedRuntimeInput);
  if (!valid) {
    return {
      valid: false,
      absolutePath: resolvedInput,
      errors: [`path_not_allowed:${resolvedInput}`],
    };
  }
  return {
    valid: true,
    absolutePath: resolvedInput,
    errors: [],
  };
}

export function readFileImportSample(config: FileImportConfig): {
  readonly ok: boolean;
  readonly absolutePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly FileImportError[];
} {
  const pathCheck = validateFileImportPath(config.edgeRoot, config.samplePath);
  if (!pathCheck.valid) {
    return {
      ok: false,
      absolutePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: pathCheck.errors.map((message) => ({ code: 'path_not_allowed', message })),
    };
  }
  const maxBytes = config.maxBytes > 0 ? config.maxBytes : DEFAULT_MAX_BYTES;
  let fileSize = 0;
  try {
    fileSize = statSync(pathCheck.absolutePath).size;
  } catch (error) {
    return {
      ok: false,
      absolutePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [
        {
          code: 'file_stat_failed',
          message: error instanceof Error ? error.message : 'file stat failed',
        },
      ],
    };
  }
  if (fileSize > maxBytes) {
    return {
      ok: false,
      absolutePath: pathCheck.absolutePath,
      bytesRead: fileSize,
      content: '',
      errors: [
        {
          code: 'file_too_large',
          message: `file exceeds maxBytes: ${fileSize} > ${maxBytes}`,
          details: { fileSize, maxBytes },
        },
      ],
    };
  }
  try {
    const content = readFileSync(pathCheck.absolutePath, 'utf8');
    return {
      ok: true,
      absolutePath: pathCheck.absolutePath,
      bytesRead: Buffer.byteLength(content, 'utf8'),
      content,
      errors: [],
    };
  } catch (error) {
    return {
      ok: false,
      absolutePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [
        {
          code: 'file_read_failed',
          message: error instanceof Error ? error.message : 'file read failed',
        },
      ],
    };
  }
}

export function validateFileImportRecord(record: FileImportRecord): FileImportValidationResult {
  const errors: string[] = [];
  if (!record.sourceRef) errors.push('sourceRef is required');
  if (!record.pointRef) errors.push('pointRef is required');
  if (record.value === '' || record.value == null) errors.push('value is required');
  if (!record.unit) errors.push('unit is required');
  if (!record.observedAt) errors.push('observedAt is required');
  if (!record.assetRef) errors.push('assetRef is required');
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function parseFileImportJson(content: string, sourcePath: string): FileImportParseResult {
  const records: FileImportRecord[] = [];
  const validationErrors: FileImportError[] = [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    return {
      ok: false,
      format: 'json',
      records: [],
      validationErrors: [
        {
          code: 'json_parse_failed',
          message: error instanceof Error ? error.message : 'json parse failed',
        },
      ],
      bytesRead: Buffer.byteLength(content, 'utf8'),
      lineCount: content.length == 0 ? 0 : content.split('\n').length,
      sourcePath,
    };
  }
  const rawList = Array.isArray(parsed) ? parsed : [parsed];
  rawList.forEach((item, index) => {
    if (!isObject(item)) {
      validationErrors.push({
        code: 'invalid_record_shape',
        message: 'record must be an object',
        line: index + 1,
      });
      return;
    }
    const record = toRecord(item);
    const valid = validateFileImportRecord(record);
    if (!valid.valid) {
      validationErrors.push({
        code: 'invalid_record_fields',
        message: valid.errors.join('; '),
        line: index + 1,
      });
      return;
    }
    records.push(record);
  });
  return {
    ok: validationErrors.length == 0,
    format: 'json',
    records,
    validationErrors,
    bytesRead: Buffer.byteLength(content, 'utf8'),
    lineCount: content.length == 0 ? 0 : content.split('\n').length,
    sourcePath,
  };
}

export function parseFileImportJsonl(content: string, sourcePath: string, maxLines = DEFAULT_MAX_JSONL_LINES): FileImportParseResult {
  const records: FileImportRecord[] = [];
  const validationErrors: FileImportError[] = [];
  const lines = content.split('\n').filter((line) => line.trim().length > 0);
  if (lines.length > maxLines) {
    return {
      ok: false,
      format: 'jsonl',
      records: [],
      validationErrors: [
        {
          code: 'jsonl_line_limit_exceeded',
          message: `line count exceeds limit: ${lines.length} > ${maxLines}`,
          details: { lineCount: lines.length, maxLines },
        },
      ],
      bytesRead: Buffer.byteLength(content, 'utf8'),
      lineCount: lines.length,
      sourcePath,
    };
  }
  lines.forEach((line, index) => {
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch (error) {
      validationErrors.push({
        code: 'jsonl_parse_failed',
        message: error instanceof Error ? error.message : 'jsonl parse failed',
        line: index + 1,
      });
      return;
    }
    if (!isObject(parsed)) {
      validationErrors.push({
        code: 'invalid_record_shape',
        message: 'record must be an object',
        line: index + 1,
      });
      return;
    }
    const record = toRecord(parsed);
    const valid = validateFileImportRecord(record);
    if (!valid.valid) {
      validationErrors.push({
        code: 'invalid_record_fields',
        message: valid.errors.join('; '),
        line: index + 1,
      });
      return;
    }
    records.push(record);
  });
  return {
    ok: validationErrors.length == 0,
    format: 'jsonl',
    records,
    validationErrors,
    bytesRead: Buffer.byteLength(content, 'utf8'),
    lineCount: lines.length,
    sourcePath,
  };
}

export function exportFileImportEvidence(path: string, payload: FileImportEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}

export function parseFileImportFromConfig(config: FileImportConfig): {
  readonly parseResult: FileImportParseResult;
  readonly stats: FileImportStats;
} {
  const readResult = readFileImportSample(config);
  if (!readResult.ok) {
    const parseResult: FileImportParseResult = {
      ok: false,
      format: config.format,
      records: [],
      validationErrors: readResult.errors,
      bytesRead: readResult.bytesRead,
      lineCount: 0,
      sourcePath: readResult.absolutePath,
    };
    return {
      parseResult,
      stats: {
        recordsRead: 0,
        recordsValid: 0,
        recordsInvalid: readResult.errors.length,
        bytesRead: readResult.bytesRead,
        lineCount: 0,
        generatedAt: nowIso(),
      },
    };
  }
  const parseResult =
    config.format == 'json'
      ? parseFileImportJson(readResult.content, readResult.absolutePath)
      : parseFileImportJsonl(readResult.content, readResult.absolutePath, config.maxJsonlLines);
  return {
    parseResult,
    stats: {
      recordsRead: parseResult.records.length + parseResult.validationErrors.length,
      recordsValid: parseResult.records.length,
      recordsInvalid: parseResult.validationErrors.length,
      bytesRead: parseResult.bytesRead,
      lineCount: parseResult.lineCount,
      generatedAt: nowIso(),
    },
  };
}
