import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type { NormalizedSamplePlaceholder } from './protocol-plugin-types.js';
import type {
  BacnetIpReadonlyConfig,
  BacnetIpReadonlyError,
  BacnetIpReadonlyEvidence,
  BacnetIpReadonlyValidationResult,
  BacnetSyntheticFixture,
  BacnetSyntheticPoint,
} from './bacnet-ip-readonly-types.js';

const DEFAULT_MAX_BYTES = 1024 * 1024;

const ALLOWED_OBJECT_TYPES = new Set([
  'analogInput',
  'analogOutput',
  'analogValue',
  'binaryInput',
  'binaryOutput',
  'binaryValue',
  'multiStateInput',
  'multiStateOutput',
  'multiStateValue',
]);

const ALLOWED_PROPERTY_IDENTIFIERS = new Set(['presentValue', 'statusFlags', 'reliability', 'units']);

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asNumber(value: unknown): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : 0;
}

function isUnder(absolutePath: string, allowedRoot: string): boolean {
  const normalizedRoot = resolve(allowedRoot);
  const normalizedPath = resolve(absolutePath);
  return normalizedPath == normalizedRoot || normalizedPath.startsWith(normalizedRoot + '/');
}

export function validateBacnetHost(host: string): BacnetIpReadonlyValidationResult {
  const normalized = host.trim().toLowerCase();
  const allowed =
    normalized == '127.0.0.1' ||
    normalized == 'localhost' ||
    normalized == 'example.invalid' ||
    normalized.startsWith('mock://synthetic-bacnet-device');
  if (!allowed) {
    return {
      valid: false,
      errors: ['host_not_allowed_for_bacnet_ip_readonly_foundation'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateBacnetFixturePath(edgeRoot: string, fixturePath: string): BacnetIpReadonlyValidationResult & {
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

function validatePointShape(point: {
  readonly objectType: string;
  readonly objectInstance: number;
  readonly propertyIdentifier: string;
}): BacnetIpReadonlyValidationResult {
  const errors: string[] = [];
  if (!ALLOWED_OBJECT_TYPES.has(point.objectType)) {
    errors.push(`invalid_object_type:${point.objectType}`);
  }
  if (!Number.isInteger(point.objectInstance) || point.objectInstance < 0) {
    errors.push(`invalid_object_instance:${point.objectInstance}`);
  }
  if (!ALLOWED_PROPERTY_IDENTIFIERS.has(point.propertyIdentifier)) {
    errors.push(`invalid_property_identifier:${point.propertyIdentifier}`);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function validateBacnetIpReadonlyConfig(config: BacnetIpReadonlyConfig): BacnetIpReadonlyValidationResult {
  const errors: string[] = [];
  if (!config.connectorId) errors.push('connectorId is required');
  if (config.protocol != 'bacnet-ip-readonly') errors.push('protocol must be bacnet-ip-readonly');
  if (!config.host) errors.push('host is required');
  if (config.port <= 0 || config.port > 65535) errors.push('port is invalid');
  if (config.pollingIntervalMs <= 0) errors.push('pollingIntervalMs must be > 0');
  if (config.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
  if (config.retries < 0) errors.push('retries must be >= 0');
  if (config.networkEnabled !== false) errors.push('networkEnabled must be false in c3-05 foundation');
  if (config.supportsWriteback !== false) errors.push('supportsWriteback must be false for bacnet readonly');
  const hostCheck = validateBacnetHost(config.host);
  if (!hostCheck.valid) errors.push(...hostCheck.errors);
  if (!config.fixturePath) errors.push('fixturePath is required');
  for (const mapping of config.pointMappings) {
    const pointCheck = validatePointShape(mapping);
    if (!pointCheck.valid) errors.push(...pointCheck.errors);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function readBacnetSyntheticFixture(config: BacnetIpReadonlyConfig): {
  readonly ok: boolean;
  readonly fixturePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly BacnetIpReadonlyError[];
} {
  const pathCheck = validateBacnetFixturePath('./AN_VANTARIS_EDGE', config.fixturePath);
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
      errors: [{ code: 'fixture_too_large', message: `fixture exceeds max bytes: ${fileSize}` }],
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

export function parseBacnetSyntheticFixture(content: string): {
  readonly ok: boolean;
  readonly fixture: BacnetSyntheticFixture | null;
  readonly errors: readonly BacnetIpReadonlyError[];
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
  if (asString(parsed.protocol) != 'bacnet-ip-readonly') {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_protocol_invalid', message: 'fixture protocol must be bacnet-ip-readonly' }],
    };
  }
  if (parsed.networkEnabled !== false) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_network_enabled_invalid', message: 'fixture networkEnabled must be false' }],
    };
  }
  const device = isObject(parsed.device) ? parsed.device : null;
  if (!device) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_device_missing', message: 'device object is required' }],
    };
  }
  const pointsRaw = parsed.points;
  if (!Array.isArray(pointsRaw)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_points_missing', message: 'points array is required' }],
    };
  }

  const points: BacnetSyntheticPoint[] = [];
  const errors: BacnetIpReadonlyError[] = [];
  pointsRaw.forEach((item, index) => {
    if (!isObject(item)) {
      errors.push({ code: 'point_invalid_shape', message: 'point must be object', details: { index } });
      return;
    }
    const objectType = asString(item.objectType);
    const propertyIdentifier = asString(item.propertyIdentifier);
    const pointCheck = validatePointShape({
      objectType,
      objectInstance: asNumber(item.objectInstance),
      propertyIdentifier,
    });
    if (!pointCheck.valid) {
      errors.push({
        code: 'point_mapping_invalid',
        message: pointCheck.errors.join('; '),
        details: { index },
      });
      return;
    }
    const statusRaw = asString(item.status).toLowerCase();
    points.push({
      pointId: asString(item.pointId),
      objectType: objectType as BacnetSyntheticPoint['objectType'],
      objectInstance: asNumber(item.objectInstance),
      propertyIdentifier: propertyIdentifier as BacnetSyntheticPoint['propertyIdentifier'],
      value:
        typeof item.value == 'number' || typeof item.value == 'string' || typeof item.value == 'boolean'
          ? item.value
          : asString(item.value),
      engineeringUnit: asString(item.engineeringUnit) || 'synthetic-unit',
      status: statusRaw == 'bad' || statusRaw == 'uncertain' ? statusRaw : 'good',
      timestamp: asString(item.timestamp) || nowIso(),
    });
  });
  return {
    ok: errors.length == 0,
    fixture: {
      connectorId: asString(parsed.connectorId) || 'connector-bacnet-example-01',
      protocol: 'bacnet-ip-readonly',
      networkEnabled: false,
      source: 'synthetic-fixture',
      device: {
        deviceId: asNumber(device.deviceId),
        name: asString(device.name) || 'Synthetic BACnet Device',
        address: asString(device.address) || 'mock://synthetic-bacnet-device',
        vendorName: asString(device.vendorName) || 'Synthetic Vendor',
      },
      points,
    },
    errors,
  };
}

export function extractBacnetPointRecords(input: {
  fixture: BacnetSyntheticFixture;
  config: BacnetIpReadonlyConfig;
}): {
  readonly points: readonly BacnetSyntheticPoint[];
  readonly errors: readonly BacnetIpReadonlyError[];
} {
  const errors: BacnetIpReadonlyError[] = [];
  const mappingByPointId = new Map(input.config.pointMappings.map((mapping) => [mapping.pointId, mapping]));
  const points = input.fixture.points.map((point) => {
    const mapped = mappingByPointId.get(point.pointId);
    if (!mapped) return point;
    return {
      ...point,
      engineeringUnit: point.engineeringUnit || mapped.engineeringUnit,
    };
  });
  points.forEach((point, index) => {
    if (!point.pointId) {
      errors.push({
        code: 'point_id_missing',
        message: 'pointId is required',
        details: { index },
      });
    }
  });
  return { points, errors };
}

export function mapBacnetPointToPluginSample(input: {
  connectorId: string;
  sourceSystemId: string;
  sequence: number;
  point: BacnetSyntheticPoint;
}): NormalizedSamplePlaceholder {
  return {
    sampleId: `${input.connectorId}-bacnet-${input.sequence}`,
    connectorId: input.connectorId,
    sourceSystemId: input.sourceSystemId,
    protocol: 'bacnet',
    sampleType: 'telemetry',
    timestamp: input.point.timestamp,
    payload: {
      pointId: input.point.pointId,
      objectType: input.point.objectType,
      objectInstance: input.point.objectInstance,
      propertyIdentifier: input.point.propertyIdentifier,
      value: input.point.value,
      engineeringUnit: input.point.engineeringUnit,
      status: input.point.status,
      synthetic: true,
      writeback: false,
    },
  };
}

export function exportBacnetIpReadonlyEvidence(path: string, payload: BacnetIpReadonlyEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
