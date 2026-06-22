import type { FileReadOnlyPolicy } from '../file-readonly-types.js';
import { parseJsonImportFile } from '../file-import-parser.js';
import { validateFileReadOnlyPolicy } from '../file-readonly-policy.js';
import { validateFileCandidate } from '../file-readonly-validator.js';

import type {
  FileProductionAdapterConfig,
  FileProductionErrorCode,
  FileProductionFormat,
  FileProductionNormalizedRecord,
  FileProductionResourceLimits,
} from './file-production-adapter.types.js';
import { FILE_PRODUCTION_DANGEROUS_KEYS, FILE_PRODUCTION_FORMULA_PREFIXES, FILE_PRODUCTION_LIMIT_CAPS } from './file-production-adapter.types.js';

export function validatePositiveInt(value: unknown, fieldName: string, cap: number): FileProductionErrorCode | null {
  if (typeof value !== 'number' || !Number.isInteger(value) || value <= 0) return 'FILE_CONFIG_INVALID';
  if (value > cap) return 'FILE_CONFIG_INVALID';
  return null;
}

export function validateProductionAdapterConfig(config: FileProductionAdapterConfig): FileProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_FILE_READONLY') return 'FILE_CONFIG_INVALID';
  if (config.enabled !== true) return 'FILE_ADAPTER_DISABLED';
  if (!config.rootReferenceId || !config.inputRelativePath) return 'FILE_CONFIG_INVALID';
  if (!['json', 'jsonl', 'csv'].includes(config.format)) return 'FILE_FORMAT_NOT_ALLOWED';
  if (config.encoding !== 'utf-8') return 'FILE_ENCODING_INVALID';
  if (config.formulaPrefixPolicy !== 'REJECT' && config.formulaPrefixPolicy !== 'MARK') return 'FILE_CONFIG_INVALID';
  if (config.dangerousKeyPolicy !== 'REJECT') return 'FILE_CONFIG_INVALID';

  const limitFields: Array<keyof FileProductionResourceLimits> = [
    'maxFileBytes',
    'maxLineBytes',
    'maxRecordCount',
    'maxJsonDepth',
    'maxFieldCount',
    'maxFieldLength',
    'maxCsvColumns',
    'maxProcessingMilliseconds',
  ];
  for (const field of limitFields) {
    const cap = FILE_PRODUCTION_LIMIT_CAPS[field];
    if (validatePositiveInt(config[field], field, cap)) return 'FILE_CONFIG_INVALID';
  }
  return null;
}

export function buildFoundationPolicyForProduction(allowlistedRoot: string, config: FileProductionAdapterConfig): FileReadOnlyPolicy {
  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-01',
    classification: 'CONTROLLED_LOCAL_READ_ONLY_FOUNDATION',
    allowedRoots: [allowlistedRoot],
    deniedRoots: [],
    allowedExtensions: config.format === 'jsonl' ? ['.jsonl'] : config.format === 'csv' ? ['.csv'] : ['.json'],
    maxFileSizeBytes: Math.min(config.maxFileBytes, FILE_PRODUCTION_LIMIT_CAPS.maxFileBytes),
    rejectTraversal: true,
    rejectSymlinks: true,
    rejectHiddenFiles: true,
    rejectDeviceFiles: true,
    rejectSockets: true,
    rejectDirectories: true,
    requireRegularFile: true,
    requireStableSize: true,
    stableObservationWindowMs: 1,
    duplicateDetectionMode: 'SHA256_LOCAL_FOUNDATION',
    quarantineMode: 'DECISION_ONLY',
    sourceMutationAllowed: false,
    sourceDeletionAllowed: false,
    sourceRenameAllowed: false,
    networkFilesystemAllowed: false,
    csvHeaderRequired: true,
    csvDelimiter: ',',
    csvMaxRows: Math.min(config.maxRecordCount, FILE_PRODUCTION_LIMIT_CAPS.maxRecordCount),
    jsonAllowObject: true,
    jsonAllowArray: true,
    jsonAllowScalar: false,
    jsonMaxDepth: Math.min(config.maxJsonDepth, FILE_PRODUCTION_LIMIT_CAPS.maxJsonDepth),
    candidateStatus: 'CONTROLLED_LOCAL_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_01_FILE_IMPORT_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  };
}

export function validateFoundationJsonRecord(
  record: Record<string, unknown>,
  allowlistedRoot: string,
  config: FileProductionAdapterConfig,
): FileProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(allowlistedRoot, config);
  try {
    parseJsonImportFile(JSON.stringify(record), policy);
    return null;
  } catch {
    return 'FILE_FOUNDATION_VALIDATION_FAILED';
  }
}

export function runFoundationValidation(canonicalPath: string, allowlistedRoot: string, config: FileProductionAdapterConfig): FileProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(allowlistedRoot, config);
  if (config.format !== 'jsonl') {
    const policyValidation = validateFileReadOnlyPolicy(policy);
    if (!policyValidation.ok) return 'FILE_FOUNDATION_VALIDATION_FAILED';
  } else if (!policy.rejectTraversal || !policy.rejectSymlinks || !policy.requireRegularFile) {
    return 'FILE_FOUNDATION_VALIDATION_FAILED';
  }
  const candidate = validateFileCandidate(canonicalPath, policy);
  if (!candidate.ok) return 'FILE_FOUNDATION_VALIDATION_FAILED';
  return null;
}

function flattenValue(value: unknown, prefix: string, output: Record<string, string>, depth: number, limits: FileProductionResourceLimits): FileProductionErrorCode | null {
  if (depth > limits.maxJsonDepth) return 'FILE_JSON_INVALID';
  if (value === null || typeof value === 'boolean' || typeof value === 'number') {
    const keyCount = Object.keys(output).length;
    if (keyCount >= limits.maxFieldCount) return 'FILE_RECORD_LIMIT_EXCEEDED';
    output[prefix || 'value'] = String(value);
    return null;
  }
  if (typeof value === 'string') {
    if (value.length > limits.maxFieldLength) return 'FILE_LINE_LIMIT_EXCEEDED';
    const keyCount = Object.keys(output).length;
    if (keyCount >= limits.maxFieldCount) return 'FILE_RECORD_LIMIT_EXCEEDED';
    output[prefix || 'value'] = value;
    return null;
  }
  if (Array.isArray(value)) {
    for (let index = 0; index < value.length; index += 1) {
      const childPrefix = prefix ? `${prefix}.${index}` : String(index);
      const err = flattenValue(value[index], childPrefix, output, depth + 1, limits);
      if (err) return err;
    }
    return null;
  }
  if (typeof value === 'object') {
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
      if ((FILE_PRODUCTION_DANGEROUS_KEYS as readonly string[]).includes(key)) return 'FILE_DANGEROUS_KEY_REJECTED';
      const childPrefix = prefix ? `${prefix}.${key}` : key;
      const err = flattenValue(child, childPrefix, output, depth + 1, limits);
      if (err) return err;
    }
    return null;
  }
  return 'FILE_JSON_INVALID';
}

export function containsDangerousKey(value: unknown, depth = 0, maxDepth: number): boolean {
  if (depth > maxDepth) return false;
  if (value === null || typeof value !== 'object') return false;
  if (Array.isArray(value)) return value.some((item) => containsDangerousKey(item, depth + 1, maxDepth));
  for (const key of Object.keys(value as Record<string, unknown>)) {
    if ((FILE_PRODUCTION_DANGEROUS_KEYS as readonly string[]).includes(key)) return true;
    if (containsDangerousKey((value as Record<string, unknown>)[key], depth + 1, maxDepth)) return true;
  }
  return false;
}

export function applyFormulaPrefixPolicy(fields: Record<string, string>, policy: 'REJECT' | 'MARK'): FileProductionErrorCode | null {
  for (const [key, value] of Object.entries(fields)) {
    const trimmed = value.trimStart();
    const prefix = FILE_PRODUCTION_FORMULA_PREFIXES.find((item) => trimmed.startsWith(item));
    if (!prefix) continue;
    if (policy === 'REJECT') return 'FILE_FORMULA_PREFIX_REJECTED';
    fields[key] = `'${value}`;
  }
  return null;
}

export function normalizeRecordsFromObjects(
  objects: readonly Record<string, unknown>[],
  config: FileProductionAdapterConfig,
): { ok: true; records: FileProductionNormalizedRecord[] } | { ok: false; errorCode: FileProductionErrorCode; lineNumber?: number } {
  if (objects.length > config.maxRecordCount) return { ok: false, errorCode: 'FILE_RECORD_LIMIT_EXCEEDED' };
  const records: FileProductionNormalizedRecord[] = [];
  for (let index = 0; index < objects.length; index += 1) {
    if (containsDangerousKey(objects[index], 0, config.maxJsonDepth)) {
      return { ok: false, errorCode: 'FILE_DANGEROUS_KEY_REJECTED', lineNumber: index + 1 };
    }
    const fields: Record<string, string> = {};
    const flattenError = flattenValue(objects[index], '', fields, 0, config);
    if (flattenError) return { ok: false, errorCode: flattenError, lineNumber: index + 1 };
    const formulaError = applyFormulaPrefixPolicy(fields, config.formulaPrefixPolicy);
    if (formulaError) return { ok: false, errorCode: formulaError, lineNumber: index + 1 };
    records.push({ fields });
  }
  return { ok: true, records };
}

export function normalizeCsvRecords(headers: readonly string[], rows: readonly Record<string, string>[], config: FileProductionAdapterConfig): { ok: true; records: FileProductionNormalizedRecord[] } | { ok: false; errorCode: FileProductionErrorCode } {
  if (headers.length > config.maxCsvColumns) return { ok: false, errorCode: 'FILE_CSV_INVALID' };
  if (rows.length > config.maxRecordCount) return { ok: false, errorCode: 'FILE_RECORD_LIMIT_EXCEEDED' };
  const records: FileProductionNormalizedRecord[] = [];
  for (const row of rows) {
    const fields: Record<string, string> = {};
    for (const header of headers) {
      const value = row[header] ?? '';
      if (value.length > config.maxFieldLength) return { ok: false, errorCode: 'FILE_LINE_LIMIT_EXCEEDED' };
      fields[header] = value;
    }
    const formulaError = applyFormulaPrefixPolicy(fields, config.formulaPrefixPolicy);
    if (formulaError) return { ok: false, errorCode: formulaError };
    records.push({ fields });
  }
  return { ok: true, records };
}

export function formatToExtension(format: FileProductionFormat): string {
  if (format === 'jsonl') return '.jsonl';
  if (format === 'csv') return '.csv';
  return '.json';
}
