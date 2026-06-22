import type {
  FileReadOnlyPolicy,
  ParsedCsvImport,
  ParsedJsonImport,
} from './file-readonly-types.js';

function computeJsonDepth(value: unknown, depth = 0): number {
  if (value === null || typeof value !== 'object') return depth;
  if (Array.isArray(value)) return value.reduce((max, item) => Math.max(max, computeJsonDepth(item, depth + 1)), depth + 1);
  return Object.values(value).reduce((max, item) => Math.max(max, computeJsonDepth(item, depth + 1)), depth + 1);
}

export function parseJsonImportFile(content: string, policy: FileReadOnlyPolicy): ParsedJsonImport {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch {
    throw new Error('MALFORMED_JSON');
  }
  const depth = computeJsonDepth(parsed, 0);
  if (depth > policy.jsonMaxDepth) throw new Error('MALFORMED_JSON');
  if (Array.isArray(parsed)) {
    if (!policy.jsonAllowArray) throw new Error('MALFORMED_JSON');
    if (!parsed.every((item) => item !== null && typeof item === 'object' && !Array.isArray(item))) {
      throw new Error('MALFORMED_JSON');
    }
    return { kind: 'json', records: parsed as Record<string, unknown>[] };
  }
  if (parsed !== null && typeof parsed === 'object') {
    if (!policy.jsonAllowObject) throw new Error('MALFORMED_JSON');
    return { kind: 'json', records: [parsed as Record<string, unknown>] };
  }
  if (policy.jsonAllowScalar) {
    return { kind: 'json', records: [{ value: parsed }] };
  }
  throw new Error('MALFORMED_JSON');
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
    current += char;
  }
  if (inQuote) throw new Error('MALFORMED_CSV');
  parts.push(current);
  return parts;
}

export function parseCsvImportFile(content: string, policy: FileReadOnlyPolicy): ParsedCsvImport {
  const lines = content.replace(/\r\n/g, '\n').split('\n').filter((line) => line.length > 0);
  if (lines.length === 0) throw new Error('MALFORMED_CSV');
  const header = splitCsvLine(lines[0]).map((column) => column.trim());
  if (policy.csvHeaderRequired && header.some((column) => column.length === 0)) throw new Error('MALFORMED_CSV');
  const width = header.length;
  if (width === 0) throw new Error('MALFORMED_CSV');
  const body = lines.slice(1);
  if (body.length > policy.csvMaxRows) throw new Error('MALFORMED_CSV');
  const records = body.map((line) => {
    const cells = splitCsvLine(line);
    if (cells.length !== width) throw new Error('MALFORMED_CSV');
    const row: Record<string, string> = {};
    for (let index = 0; index < width; index += 1) {
      row[header[index]] = cells[index];
    }
    return row;
  });
  return { kind: 'csv', headers: header, records };
}
