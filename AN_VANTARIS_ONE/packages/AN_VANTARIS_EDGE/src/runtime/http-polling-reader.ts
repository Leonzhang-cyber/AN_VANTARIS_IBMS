import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type {
  HttpPollingConfig,
  HttpPollingError,
  HttpPollingEvidence,
  HttpPollingRecord,
  HttpPollingResponseFixture,
  HttpPollingValidationResult,
} from './http-polling-types.js';
import type { NormalizedSamplePlaceholder } from './protocol-plugin-types.js';

const DEFAULT_MAX_BYTES = 1024 * 1024;

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : fallback;
}

function isUnder(absolutePath: string, allowedRoot: string): boolean {
  const normalizedRoot = resolve(allowedRoot);
  const normalizedPath = resolve(absolutePath);
  return normalizedPath == normalizedRoot || normalizedPath.startsWith(normalizedRoot + '/');
}

function deepGet(input: unknown, path: string): unknown {
  if (!path) return input;
  const parts = path.split('.').filter((part) => part.length > 0);
  let current: unknown = input;
  for (const part of parts) {
    if (!isObject(current)) return undefined;
    current = current[part];
  }
  return current;
}

export function validateHttpPollingUrl(url: string): HttpPollingValidationResult {
  const normalized = url.trim();
  const allowed =
    normalized.startsWith('mock://') ||
    normalized.startsWith('https://example.invalid/') ||
    normalized.startsWith('http://127.0.0.1/') ||
    normalized.startsWith('http://localhost/');
  if (!allowed) {
    return {
      valid: false,
      errors: ['url_not_allowed_for_c3_foundation'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateHttpPollingFixturePath(edgeRoot: string, fixturePath: string): HttpPollingValidationResult & {
  readonly absolutePath: string;
} {
  const resolvedEdgeRoot = resolve(edgeRoot);
  const resolvedFixture = resolve(resolvedEdgeRoot, fixturePath);
  const deniedPrefixes = ['/Users/', '/etc/', '/tmp/', '/var/', '/Volumes/'];
  const allowedConfigSamples = resolve(resolvedEdgeRoot, 'config/samples');
  const allowedRuntimeInput = resolve(resolvedEdgeRoot, '.runtime/input');
  const valid = isUnder(resolvedFixture, allowedConfigSamples) || isUnder(resolvedFixture, allowedRuntimeInput);
  if (!valid) {
    return {
      valid: false,
      absolutePath: resolvedFixture,
      errors: [`fixture_path_not_allowed:${resolvedFixture}`],
    };
  }
  const denied = deniedPrefixes.some((prefix) => resolvedFixture.startsWith(prefix) && !resolvedFixture.startsWith(resolvedEdgeRoot));
  if (denied) {
    return {
      valid: false,
      absolutePath: resolvedFixture,
      errors: [`fixture_path_denied_prefix:${resolvedFixture}`],
    };
  }
  return {
    valid: true,
    absolutePath: resolvedFixture,
    errors: [],
  };
}

export function validateHttpPollingConfig(config: HttpPollingConfig): HttpPollingValidationResult {
  const errors: string[] = [];
  if (!config.connectorId) errors.push('connectorId is required');
  if (!config.endpointRef) errors.push('endpointRef is required');
  if (!config.url) errors.push('url is required');
  if (!config.fixturePath) errors.push('fixturePath is required');
  if (config.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
  if (config.intervalMs <= 0) errors.push('intervalMs must be > 0');
  if (config.networkEnabled !== false) errors.push('networkEnabled must be false in c3-02 foundation');
  const urlCheck = validateHttpPollingUrl(config.url);
  if (!urlCheck.valid) errors.push(...urlCheck.errors);
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function readHttpPollingFixture(config: HttpPollingConfig): {
  readonly ok: boolean;
  readonly fixturePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly HttpPollingError[];
} {
  const pathCheck = validateHttpPollingFixturePath('./AN_VANTARIS_EDGE', config.fixturePath);
  if (!pathCheck.valid) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: pathCheck.errors.map((message) => ({ code: 'fixture_path_invalid', message })),
    };
  }
  let fileSize = 0;
  try {
    fileSize = statSync(pathCheck.absolutePath).size;
  } catch (error) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [
        {
          code: 'fixture_stat_failed',
          message: error instanceof Error ? error.message : 'fixture stat failed',
        },
      ],
    };
  }
  if (fileSize > DEFAULT_MAX_BYTES) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: fileSize,
      content: '',
      errors: [
        {
          code: 'fixture_too_large',
          message: `fixture exceeds max bytes: ${fileSize}`,
          details: { fileSize, maxBytes: DEFAULT_MAX_BYTES },
        },
      ],
    };
  }
  try {
    const content = readFileSync(pathCheck.absolutePath, 'utf8');
    return {
      ok: true,
      fixturePath: pathCheck.absolutePath,
      bytesRead: Buffer.byteLength(content, 'utf8'),
      content,
      errors: [],
    };
  } catch (error) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [
        {
          code: 'fixture_read_failed',
          message: error instanceof Error ? error.message : 'fixture read failed',
        },
      ],
    };
  }
}

export function parseHttpPollingResponseFixture(content: string): {
  readonly ok: boolean;
  readonly fixture: HttpPollingResponseFixture | null;
  readonly errors: readonly HttpPollingError[];
} {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    return {
      ok: false,
      fixture: null,
      errors: [
        {
          code: 'fixture_json_parse_failed',
          message: error instanceof Error ? error.message : 'fixture parse failed',
        },
      ],
    };
  }
  if (!isObject(parsed)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_invalid_shape', message: 'fixture root must be object' }],
    };
  }
  const recordsRaw = parsed.records;
  if (!Array.isArray(recordsRaw)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_records_missing', message: 'records array is required' }],
    };
  }
  return {
    ok: true,
    fixture: {
      source: asString(parsed.source) || 'synthetic-http-system',
      observedAt: asString(parsed.observedAt) || nowIso(),
      records: recordsRaw.filter((item) => isObject(item)) as readonly Record<string, unknown>[],
    },
    errors: [],
  };
}

export function extractHttpPollingRecords(
  fixture: HttpPollingResponseFixture,
  config: HttpPollingConfig,
): {
  readonly records: readonly HttpPollingRecord[];
  readonly errors: readonly HttpPollingError[];
} {
  const recordsRaw = deepGet(fixture, config.responseMapping.recordsPath);
  const list = Array.isArray(recordsRaw) ? recordsRaw : fixture.records;
  const records: HttpPollingRecord[] = [];
  const errors: HttpPollingError[] = [];
  list.forEach((item, index) => {
    if (!isObject(item)) {
      errors.push({
        code: 'record_invalid_shape',
        message: 'record must be object',
        details: { index },
      });
      return;
    }
    const pointRef = asString(deepGet(item, config.responseMapping.pointRefField));
    const assetRef = asString(deepGet(item, config.responseMapping.assetRefField));
    const observedAt = asString(deepGet(item, config.responseMapping.observedAtField)) || fixture.observedAt;
    if (!pointRef || !assetRef || !observedAt) {
      errors.push({
        code: 'record_required_field_missing',
        message: 'pointRef/assetRef/observedAt are required',
        details: { index },
      });
      return;
    }
    const qualityRaw = asString(deepGet(item, config.responseMapping.qualityField)).toLowerCase();
    records.push({
      sourceRef: fixture.source,
      pointRef,
      assetRef,
      value: (deepGet(item, config.responseMapping.valueField) ?? '') as number | string | boolean,
      unit: asString(item.unit) || 'synthetic-unit',
      quality: qualityRaw == 'bad' || qualityRaw == 'uncertain' ? qualityRaw : 'good',
      observedAt,
      metadata: isObject(deepGet(item, config.responseMapping.metadataField))
        ? (deepGet(item, config.responseMapping.metadataField) as Record<string, unknown>)
        : {},
    });
  });
  return { records, errors };
}

export function mapHttpPollingRecordToPluginSample(input: {
  connectorId: string;
  sourceSystemId: string;
  sequence: number;
  record: HttpPollingRecord;
}): NormalizedSamplePlaceholder {
  return {
    sampleId: `${input.connectorId}-http-${input.sequence}`,
    connectorId: input.connectorId,
    sourceSystemId: input.sourceSystemId,
    protocol: 'http',
    sampleType: 'telemetry',
    timestamp: input.record.observedAt,
    payload: {
      sourceRef: input.record.sourceRef,
      pointRef: input.record.pointRef,
      assetRef: input.record.assetRef,
      value: input.record.value,
      unit: input.record.unit,
      quality: input.record.quality,
      metadata: input.record.metadata,
      synthetic: true,
    },
  };
}

export function exportHttpPollingEvidence(path: string, payload: HttpPollingEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}

export function runHttpPollingFixtureParse(config: HttpPollingConfig): {
  readonly validation: HttpPollingValidationResult;
  readonly records: readonly HttpPollingRecord[];
  readonly errors: readonly HttpPollingError[];
  readonly bytesRead: number;
  readonly fixturePath: string;
} {
  const validation = validateHttpPollingConfig(config);
  const fixtureRead = readHttpPollingFixture(config);
  if (!fixtureRead.ok) {
    return {
      validation,
      records: [],
      errors: [...fixtureRead.errors],
      bytesRead: fixtureRead.bytesRead,
      fixturePath: fixtureRead.fixturePath,
    };
  }
  const fixtureParsed = parseHttpPollingResponseFixture(fixtureRead.content);
  if (!fixtureParsed.ok || !fixtureParsed.fixture) {
    return {
      validation,
      records: [],
      errors: [...fixtureParsed.errors],
      bytesRead: fixtureRead.bytesRead,
      fixturePath: fixtureRead.fixturePath,
    };
  }
  const extracted = extractHttpPollingRecords(fixtureParsed.fixture, config);
  return {
    validation,
    records: extracted.records,
    errors: [...extracted.errors],
    bytesRead: fixtureRead.bytesRead,
    fixturePath: fixtureRead.fixturePath,
  };
}
