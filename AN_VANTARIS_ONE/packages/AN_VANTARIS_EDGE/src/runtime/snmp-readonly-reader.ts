import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type {
  SnmpReadonlyConfig,
  SnmpReadonlyError,
  SnmpReadonlyEvidence,
  SnmpReadonlyValidationResult,
  SnmpSyntheticFixture,
  SnmpSyntheticVarbind,
} from './snmp-readonly-types.js';
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

function isUnder(absolutePath: string, allowedRoot: string): boolean {
  const normalizedRoot = resolve(allowedRoot);
  const normalizedPath = resolve(absolutePath);
  return normalizedPath == normalizedRoot || normalizedPath.startsWith(normalizedRoot + '/');
}

export function validateSnmpHost(host: string): SnmpReadonlyValidationResult {
  const normalized = host.trim().toLowerCase();
  const allowed =
    normalized == '127.0.0.1' ||
    normalized == 'localhost' ||
    normalized == 'example.invalid' ||
    normalized.startsWith('mock://synthetic-snmp-device');
  if (!allowed) {
    return {
      valid: false,
      errors: ['host_not_allowed_for_snmp_readonly_foundation'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateSnmpCommunity(community: string): SnmpReadonlyValidationResult {
  const normalized = community.trim();
  if (normalized != 'synthetic-public-readonly') {
    return {
      valid: false,
      errors: ['community_must_be_synthetic_placeholder'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateSnmpFixturePath(edgeRoot: string, fixturePath: string): SnmpReadonlyValidationResult & {
  readonly absolutePath: string;
} {
  const resolvedEdgeRoot = resolve(edgeRoot);
  const resolvedFixture = resolve(resolvedEdgeRoot, fixturePath);
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
  return {
    valid: true,
    absolutePath: resolvedFixture,
    errors: [],
  };
}

function validateOidFormat(oid: string): boolean {
  return /^\.?1\.3\.6\.1(\.\d+)+$/.test(oid.trim());
}

export function validateSnmpReadonlyConfig(config: SnmpReadonlyConfig): SnmpReadonlyValidationResult {
  const errors: string[] = [];
  if (!config.connectorId) errors.push('connectorId is required');
  if (!config.host) errors.push('host is required');
  if (config.port <= 0 || config.port > 65535) errors.push('port is invalid');
  if (config.pollingIntervalMs <= 0) errors.push('pollingIntervalMs must be > 0');
  if (config.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
  if (config.retries < 0) errors.push('retries must be >= 0');
  if (config.networkEnabled !== false) errors.push('networkEnabled must be false in c3-03 foundation');
  if (config.supportsWriteback !== false) errors.push('supportsWriteback must be false for snmp readonly');
  const hostCheck = validateSnmpHost(config.host);
  if (!hostCheck.valid) errors.push(...hostCheck.errors);
  const communityCheck = validateSnmpCommunity(config.community);
  if (!communityCheck.valid) errors.push(...communityCheck.errors);
  if (!config.fixturePath) errors.push('fixturePath is required');
  for (const mapping of config.oidMappings) {
    if (!validateOidFormat(mapping.oid)) {
      errors.push(`invalid_oid_mapping:${mapping.oid}`);
    }
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function readSnmpSyntheticFixture(config: SnmpReadonlyConfig): {
  readonly ok: boolean;
  readonly fixturePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly SnmpReadonlyError[];
} {
  const pathCheck = validateSnmpFixturePath('./AN_VANTARIS_EDGE', config.fixturePath);
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
      errors: [{ code: 'fixture_stat_failed', message: error instanceof Error ? error.message : 'fixture stat failed' }],
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
      errors: [{ code: 'fixture_read_failed', message: error instanceof Error ? error.message : 'fixture read failed' }],
    };
  }
}

export function parseSnmpSyntheticFixture(content: string): {
  readonly ok: boolean;
  readonly fixture: SnmpSyntheticFixture | null;
  readonly errors: readonly SnmpReadonlyError[];
} {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_json_parse_failed', message: error instanceof Error ? error.message : 'fixture parse failed' }],
    };
  }
  if (!isObject(parsed)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_invalid_shape', message: 'fixture root must be object' }],
    };
  }
  const varbindsRaw = parsed.varbinds;
  if (!Array.isArray(varbindsRaw)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_varbinds_missing', message: 'varbinds array is required' }],
    };
  }
  const varbinds: SnmpSyntheticVarbind[] = [];
  const errors: SnmpReadonlyError[] = [];
  varbindsRaw.forEach((item, index) => {
    if (!isObject(item)) {
      errors.push({ code: 'varbind_invalid_shape', message: 'varbind must be object', details: { index } });
      return;
    }
    const oid = asString(item.oid);
    if (!validateOidFormat(oid)) {
      errors.push({ code: 'varbind_invalid_oid', message: `invalid oid: ${oid}`, details: { index } });
      return;
    }
    const qualityRaw = asString(item.quality).toLowerCase();
    varbinds.push({
      oid,
      pointRef: asString(item.pointRef),
      assetRef: asString(item.assetRef),
      value:
        typeof item.value == 'number' || typeof item.value == 'string' || typeof item.value == 'boolean'
          ? item.value
          : asString(item.value),
      unit: asString(item.unit) || 'synthetic-unit',
      quality: qualityRaw == 'bad' || qualityRaw == 'uncertain' ? qualityRaw : 'good',
      metadata: isObject(item.metadata) ? item.metadata : {},
    });
  });
  return {
    ok: errors.length == 0,
    fixture: {
      source: asString(parsed.source) || 'synthetic-snmp-device',
      observedAt: asString(parsed.observedAt) || nowIso(),
      varbinds,
    },
    errors,
  };
}

export function extractSnmpVarbindRecords(input: {
  fixture: SnmpSyntheticFixture;
  config: SnmpReadonlyConfig;
}): {
  readonly varbinds: readonly SnmpSyntheticVarbind[];
  readonly errors: readonly SnmpReadonlyError[];
} {
  const errors: SnmpReadonlyError[] = [];
  const mappingByOid = new Map(input.config.oidMappings.map((mapping) => [mapping.oid.replace(/^\./, ''), mapping]));
  const varbinds = input.fixture.varbinds.map((item) => {
    const normalizedOid = item.oid.replace(/^\./, '');
    const mapped = mappingByOid.get(normalizedOid);
    if (!mapped) return item;
    return {
      ...item,
      pointRef: item.pointRef || mapped.pointRef,
      assetRef: item.assetRef || mapped.assetRef,
      unit: item.unit || mapped.unit,
    };
  });
  varbinds.forEach((item, index) => {
    if (!item.pointRef || !item.assetRef) {
      errors.push({
        code: 'varbind_required_field_missing',
        message: 'pointRef and assetRef are required',
        details: { index, oid: item.oid },
      });
    }
  });
  return { varbinds, errors };
}

export function mapSnmpVarbindToPluginSample(input: {
  connectorId: string;
  sourceSystemId: string;
  observedAt: string;
  sequence: number;
  varbind: SnmpSyntheticVarbind;
}): NormalizedSamplePlaceholder {
  return {
    sampleId: `${input.connectorId}-snmp-${input.sequence}`,
    connectorId: input.connectorId,
    sourceSystemId: input.sourceSystemId,
    protocol: 'snmp',
    sampleType: 'telemetry',
    timestamp: input.observedAt,
    payload: {
      oid: input.varbind.oid,
      pointRef: input.varbind.pointRef,
      assetRef: input.varbind.assetRef,
      value: input.varbind.value,
      unit: input.varbind.unit,
      quality: input.varbind.quality,
      metadata: input.varbind.metadata,
      synthetic: true,
    },
  };
}

export function exportSnmpReadonlyEvidence(path: string, payload: SnmpReadonlyEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
