import type {
  HttpPollingReadOnlyPolicy,
  HttpResponseMetadata,
  HttpResponseMetadataValidation,
  ParsedHttpCsvResponse,
  ParsedHttpJsonResponse,
  ValidationResult,
} from './http-readonly-types.js';

function normalizeContentType(value: string | undefined): string {
  return (value ?? '').split(';')[0].trim().toLowerCase();
}

function isRedirectStatus(statusCode: number): boolean {
  return statusCode >= 300 && statusCode < 400;
}

export function validateHttpResponseMetadata(
  metadata: HttpResponseMetadata,
  policy: HttpPollingReadOnlyPolicy,
): HttpResponseMetadataValidation {
  const errors: string[] = [];

  if (isRedirectStatus(metadata.statusCode)) {
    errors.push('HTTP_REDIRECT_REJECTED');
  }

  if (metadata.statusCode < 200 || metadata.statusCode >= 300) {
    if (!policy.retryableStatusCodes.includes(metadata.statusCode)) {
      errors.push('HTTP_STATUS_NOT_ACCEPTED');
    }
  }

  const contentType = normalizeContentType(metadata.contentType);
  if (contentType && !policy.allowedContentTypes.map((x) => x.toLowerCase()).includes(contentType)) {
    errors.push('HTTP_CONTENT_TYPE_NOT_ALLOWED');
  }

  const size = metadata.contentLength ?? metadata.bodyBytes;
  if (size > policy.maxResponseBytes) {
    errors.push('HTTP_RESPONSE_TOO_LARGE');
  }

  if (metadata.redirectLocation) {
    errors.push('HTTP_REDIRECT_REJECTED');
  }

  return {
    ok: errors.length === 0,
    metadata,
    errors,
  };
}

function jsonDepth(value: unknown, depth = 0, maxDepth = 16): number {
  if (value === null || typeof value !== 'object') return depth;
  if (Array.isArray(value)) {
    return Math.max(depth, ...value.map((item) => jsonDepth(item, depth + 1, maxDepth)));
  }
  return Math.max(
    depth,
    ...Object.values(value as Record<string, unknown>).map((item) => jsonDepth(item, depth + 1, maxDepth)),
  );
}

export function parseHttpJsonResponse(
  body: string,
  policy: HttpPollingReadOnlyPolicy,
): ParsedHttpJsonResponse | ValidationResult {
  let parsed: unknown;
  try {
    parsed = JSON.parse(body);
  } catch {
    return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
  }

  if (parsed === null || typeof parsed !== 'object') {
    if (!policy.jsonAllowScalar) return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
    return { kind: 'json', records: [{ value: parsed }] };
  }

  if (Array.isArray(parsed)) {
    if (!policy.jsonAllowArray) return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
    if (jsonDepth(parsed, 0, policy.jsonMaxDepth) > policy.jsonMaxDepth) {
      return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
    }
    return { kind: 'json', records: parsed as Record<string, unknown>[] };
  }

  if (!policy.jsonAllowObject) return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
  if (jsonDepth(parsed, 0, policy.jsonMaxDepth) > policy.jsonMaxDepth) {
    return { ok: false, errors: ['MALFORMED_JSON_RESPONSE'] };
  }
  return { kind: 'json', records: [parsed as Record<string, unknown>] };
}

function splitCsvLine(line: string, delimiter: string): string[] {
  const cells: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (ch === delimiter && !inQuotes) {
      cells.push(current);
      current = '';
      continue;
    }
    current += ch;
  }
  cells.push(current);
  return cells;
}

export function parseHttpCsvResponse(
  body: string,
  policy: HttpPollingReadOnlyPolicy,
): ParsedHttpCsvResponse | ValidationResult {
  const lines = body.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n').filter((line) => line.length > 0);
  if (lines.length === 0) return { ok: false, errors: ['MALFORMED_CSV_RESPONSE'] };
  if (policy.csvHeaderRequired && lines.length < 2) return { ok: false, errors: ['MALFORMED_CSV_RESPONSE'] };

  const headers = splitCsvLine(lines[0], policy.csvDelimiter).map((cell) => cell.trim());
  if (headers.some((header) => header.length === 0)) return { ok: false, errors: ['MALFORMED_CSV_RESPONSE'] };

  const records: Record<string, string>[] = [];
  for (const line of lines.slice(1)) {
    const cells = splitCsvLine(line, policy.csvDelimiter);
    if (cells.length !== headers.length) return { ok: false, errors: ['MALFORMED_CSV_RESPONSE'] };
    const record: Record<string, string> = {};
    headers.forEach((header, index) => {
      record[header] = cells[index];
    });
    records.push(record);
  }

  if (records.length > policy.csvMaxRows) return { ok: false, errors: ['MALFORMED_CSV_RESPONSE'] };
  return { kind: 'csv', headers, records };
}
