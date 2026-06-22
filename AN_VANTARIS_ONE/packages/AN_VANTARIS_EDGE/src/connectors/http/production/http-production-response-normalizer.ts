import { validateHttpPollingPolicy } from '../http-readonly-policy.js';
import { parseHttpCsvResponse, parseHttpJsonResponse, validateHttpResponseMetadata } from '../http-response-validator.js';
import type { HttpPollingReadOnlyPolicy, HttpResponseMetadata } from '../http-readonly-types.js';

import type {
  HttpProductionAdapterConfig,
  HttpProductionErrorCode,
  HttpProductionMethod,
  HttpProductionNormalizedRecord,
  HttpProductionResourceLimits,
} from './http-production-adapter.types.js';
import {
  HTTP_PRODUCTION_ALLOWED_METHODS,
  HTTP_PRODUCTION_DANGEROUS_KEYS,
  HTTP_PRODUCTION_DENIED_HEADER_NAMES,
  HTTP_PRODUCTION_FORMULA_PREFIXES,
  HTTP_PRODUCTION_WRITE_METHODS,
} from './http-production-adapter.types.js';
import { buildFoundationPolicyForProduction, validateProductionResourceLimits } from './http-production-target-policy.js';

export function validateProductionAdapterConfig(config: HttpProductionAdapterConfig): HttpProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_HTTP_READONLY') return 'HTTP_CONFIG_INVALID';
  if (config.enabled !== true) return 'HTTP_ADAPTER_DISABLED';
  if (!config.targetReferenceId || !config.relativePath) return 'HTTP_CONFIG_INVALID';
  if (!HTTP_PRODUCTION_ALLOWED_METHODS.includes(config.method)) return 'HTTP_METHOD_NOT_ALLOWED';
  if ((HTTP_PRODUCTION_WRITE_METHODS as readonly string[]).includes(config.method)) return 'HTTP_METHOD_NOT_ALLOWED';
  if (config.tlsMode !== 'REQUIRED' && config.tlsMode !== 'LOOPBACK_HTTP_TEST') return 'HTTP_CONFIG_INVALID';
  if (config.dnsMode !== 'VALIDATED_RESOLVER' && config.dnsMode !== 'INJECTED_TEST') return 'HTTP_CONFIG_INVALID';
  if (config.formulaPrefixPolicy !== 'REJECT' && config.formulaPrefixPolicy !== 'MARK') return 'HTTP_CONFIG_INVALID';
  if (config.dangerousKeyPolicy !== 'REJECT') return 'HTTP_CONFIG_INVALID';
  if (!Array.isArray(config.expectedContentTypes) || config.expectedContentTypes.length === 0) return 'HTTP_CONFIG_INVALID';
  return validateProductionResourceLimits(config);
}

export function validateProductionMethod(method: string): HttpProductionErrorCode | null {
  const normalized = method.trim().toUpperCase() as HttpProductionMethod;
  if (!HTTP_PRODUCTION_ALLOWED_METHODS.includes(normalized)) return 'HTTP_METHOD_NOT_ALLOWED';
  if ((HTTP_PRODUCTION_WRITE_METHODS as readonly string[]).includes(normalized)) return 'HTTP_METHOD_NOT_ALLOWED';
  return null;
}

export function runFoundationPolicyValidation(
  hostname: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): HttpProductionErrorCode | null {
  const normalizedHost = hostname.trim().toLowerCase().replace(/\.$/, '');
  if (testMode && config.tlsMode === 'LOOPBACK_HTTP_TEST' && (normalizedHost === '127.0.0.1' || normalizedHost === '::1' || normalizedHost === 'localhost')) {
    return null;
  }

  const policy = buildFoundationPolicyForProduction(hostname, config, testMode);
  const validation = validateHttpPollingPolicy({
    ...policy,
    syntheticTransportOnly: false,
    networkAccessAllowed: false,
    redirectPolicy: config.maxRedirects > 0 ? 'FOLLOW' : 'REJECT',
    maxRedirects: config.maxRedirects,
  });
  if (!validation.ok) return 'HTTP_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function validateResolvedHeaders(
  headers: Readonly<Record<string, string>>,
  config: HttpProductionAdapterConfig,
): HttpProductionErrorCode | null {
  const entries = Object.entries(headers);
  if (entries.length > config.maxHeaderCount) return 'HTTP_HEADER_LIMIT_EXCEEDED';

  let authorizationCount = 0;
  for (const [name, value] of entries) {
    const lower = name.toLowerCase();
    if ((HTTP_PRODUCTION_DENIED_HEADER_NAMES as readonly string[]).includes(lower)) return 'HTTP_HEADER_REJECTED';
    if (/\r|\n/.test(name) || /\r|\n/.test(value)) return 'HTTP_HEADER_REJECTED';
    if (lower === 'authorization') authorizationCount += 1;
    if (authorizationCount > 1) return 'HTTP_HEADER_REJECTED';
    if (Buffer.byteLength(`${name}:${value}`, 'utf8') > config.maxHeaderBytes) return 'HTTP_HEADER_LIMIT_EXCEEDED';
  }
  return null;
}

export function containsDangerousKey(value: unknown, depth = 0, maxDepth: number): boolean {
  if (depth > maxDepth) return false;
  if (value === null || typeof value !== 'object') return false;
  if (Array.isArray(value)) return value.some((item) => containsDangerousKey(item, depth + 1, maxDepth));
  for (const key of Object.keys(value as Record<string, unknown>)) {
    if ((HTTP_PRODUCTION_DANGEROUS_KEYS as readonly string[]).includes(key)) return true;
    if (containsDangerousKey((value as Record<string, unknown>)[key], depth + 1, maxDepth)) return true;
  }
  return false;
}

function flattenValue(
  value: unknown,
  prefix: string,
  output: Record<string, string>,
  depth: number,
  limits: HttpProductionResourceLimits,
): HttpProductionErrorCode | null {
  if (depth > limits.maxJsonDepth) return 'HTTP_JSON_INVALID';
  if (value === null || typeof value === 'boolean' || typeof value === 'number') {
    if (Object.keys(output).length >= limits.maxFieldCount) return 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED';
    output[prefix || 'value'] = String(value);
    return null;
  }
  if (typeof value === 'string') {
    if (value.length > limits.maxFieldLength) return 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED';
    if (Object.keys(output).length >= limits.maxFieldCount) return 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED';
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
      if ((HTTP_PRODUCTION_DANGEROUS_KEYS as readonly string[]).includes(key)) return 'HTTP_DANGEROUS_KEY_REJECTED';
      const childPrefix = prefix ? `${prefix}.${key}` : key;
      const err = flattenValue(child, childPrefix, output, depth + 1, limits);
      if (err) return err;
    }
    return null;
  }
  return 'HTTP_JSON_INVALID';
}

export function applyFormulaPrefixPolicy(
  fields: Record<string, string>,
  policy: 'REJECT' | 'MARK',
): HttpProductionErrorCode | null {
  for (const [key, value] of Object.entries(fields)) {
    const trimmed = value.trimStart();
    const prefix = HTTP_PRODUCTION_FORMULA_PREFIXES.find((item) => trimmed.startsWith(item));
    if (!prefix) continue;
    if (policy === 'REJECT') return 'HTTP_FORMULA_PREFIX_REJECTED';
    fields[key] = `'${value}`;
  }
  return null;
}

export function validateFoundationJsonRecord(
  record: Record<string, unknown>,
  hostname: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): HttpProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(hostname, config, testMode);
  const parsed = parseHttpJsonResponse(JSON.stringify(record), policy);
  if ('ok' in parsed && parsed.ok === false) return 'HTTP_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function parseProductionNdjson(
  body: string,
  hostname: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): { ok: true; records: Record<string, unknown>[] } | { ok: false; errorCode: HttpProductionErrorCode; lineNumber?: number } {
  const normalized = body.replace(/\r\n/g, '\n').replace(/^\uFEFF/, '');
  if (normalized.trim().length === 0) return { ok: false, errorCode: 'HTTP_NDJSON_INVALID', lineNumber: 1 };
  const lines = normalized.split('\n');
  const records: Record<string, unknown>[] = [];
  for (let lineNumber = 1; lineNumber <= lines.length; lineNumber += 1) {
    const line = lines[lineNumber - 1];
    if (line.length === 0) continue;
    let parsed: unknown;
    try {
      parsed = JSON.parse(line);
    } catch {
      return { ok: false, errorCode: 'HTTP_NDJSON_INVALID', lineNumber };
    }
    if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return { ok: false, errorCode: 'HTTP_NDJSON_INVALID', lineNumber };
    }
    const record = parsed as Record<string, unknown>;
    if (containsDangerousKey(record, 0, config.maxJsonDepth)) {
      return { ok: false, errorCode: 'HTTP_DANGEROUS_KEY_REJECTED', lineNumber };
    }
    const foundationError = validateFoundationJsonRecord(record, hostname, config, testMode);
    if (foundationError) return { ok: false, errorCode: foundationError, lineNumber };
    records.push(record);
    if (records.length > config.maxRecordCount) return { ok: false, errorCode: 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
  }
  if (records.length === 0) return { ok: false, errorCode: 'HTTP_NDJSON_INVALID', lineNumber: 1 };
  return { ok: true, records };
}

export function normalizeRecordsFromObjects(
  objects: readonly Record<string, unknown>[],
  config: HttpProductionAdapterConfig,
): { ok: true; records: HttpProductionNormalizedRecord[] } | { ok: false; errorCode: HttpProductionErrorCode; lineNumber?: number } {
  if (objects.length > config.maxRecordCount) return { ok: false, errorCode: 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
  const records: HttpProductionNormalizedRecord[] = [];
  for (let index = 0; index < objects.length; index += 1) {
    if (containsDangerousKey(objects[index], 0, config.maxJsonDepth)) {
      return { ok: false, errorCode: 'HTTP_DANGEROUS_KEY_REJECTED', lineNumber: index + 1 };
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

export function normalizeCsvRecords(
  headers: readonly string[],
  rows: readonly Record<string, string>[],
  config: HttpProductionAdapterConfig,
): { ok: true; records: HttpProductionNormalizedRecord[] } | { ok: false; errorCode: HttpProductionErrorCode } {
  if (rows.length > config.maxRecordCount) return { ok: false, errorCode: 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
  const records: HttpProductionNormalizedRecord[] = [];
  for (const row of rows) {
    const fields: Record<string, string> = {};
    for (const header of headers) {
      const value = row[header] ?? '';
      if (value.length > config.maxFieldLength) return { ok: false, errorCode: 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
      fields[header] = value;
    }
    const formulaError = applyFormulaPrefixPolicy(fields, config.formulaPrefixPolicy);
    if (formulaError) return { ok: false, errorCode: formulaError };
    records.push({ fields });
  }
  return { ok: true, records };
}

export function validateAndParseResponseBody(
  body: string,
  metadata: HttpResponseMetadata,
  hostname: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): { ok: true; records: HttpProductionNormalizedRecord[] } | { ok: false; errorCode: HttpProductionErrorCode; lineNumber?: number } {
  const policy = buildFoundationPolicyForProduction(hostname, config, testMode);
  const metadataValidation = validateHttpResponseMetadata(metadata, {
    ...policy,
    maxResponseBytes: config.maxResponseBytes,
    allowedContentTypes: [...config.expectedContentTypes],
  });
  if (!metadataValidation.ok) {
    if (metadataValidation.errors.includes('HTTP_CONTENT_TYPE_NOT_ALLOWED')) return { ok: false, errorCode: 'HTTP_CONTENT_TYPE_NOT_ALLOWED' };
    if (metadataValidation.errors.includes('HTTP_RESPONSE_TOO_LARGE')) return { ok: false, errorCode: 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
    return { ok: false, errorCode: 'HTTP_STATUS_REJECTED' };
  }

  const contentType = (metadata.contentType ?? '').split(';')[0].trim().toLowerCase();
  if (contentType === 'application/x-ndjson' || contentType === 'application/ndjson') {
    const ndjson = parseProductionNdjson(body, hostname, config, testMode);
    if (!ndjson.ok) return ndjson;
    return normalizeRecordsFromObjects(ndjson.records, config);
  }

  if (contentType === 'text/csv' || contentType === 'application/csv') {
    const parsed = parseHttpCsvResponse(body, policy);
    if ('ok' in parsed && parsed.ok === false) return { ok: false, errorCode: 'HTTP_CSV_INVALID' };
    const csvParsed = parsed as Extract<typeof parsed, { kind: 'csv' }>;
    const normalized = normalizeCsvRecords(csvParsed.headers, csvParsed.records, config);
    if (!normalized.ok) return normalized;
    return normalized;
  }

  const parsedJson = parseHttpJsonResponse(body.replace(/^\uFEFF/, ''), policy);
  if ('ok' in parsedJson && parsedJson.ok === false) return { ok: false, errorCode: 'HTTP_JSON_INVALID' };
  const jsonParsed = parsedJson as Extract<typeof parsedJson, { kind: 'json' }>;
  return normalizeRecordsFromObjects(jsonParsed.records, config);
}

export type { HttpPollingReadOnlyPolicy, HttpResponseMetadata };
