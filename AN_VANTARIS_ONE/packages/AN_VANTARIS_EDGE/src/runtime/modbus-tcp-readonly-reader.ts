import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type {
  ModbusSyntheticFixture,
  ModbusSyntheticRegister,
  ModbusTcpReadonlyConfig,
  ModbusTcpReadonlyError,
  ModbusTcpReadonlyEvidence,
  ModbusTcpReadonlyValidationResult,
} from './modbus-tcp-readonly-types.js';
import type { NormalizedSamplePlaceholder } from './protocol-plugin-types.js';

const DEFAULT_MAX_BYTES = 1024 * 1024;
const MAX_REGISTER_QUANTITY = 125;

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

export function validateModbusHost(host: string): ModbusTcpReadonlyValidationResult {
  const normalized = host.trim().toLowerCase();
  const allowed =
    normalized == '127.0.0.1' ||
    normalized == 'localhost' ||
    normalized == 'example.invalid' ||
    normalized.startsWith('mock://synthetic-modbus-device');
  if (!allowed) {
    return {
      valid: false,
      errors: ['host_not_allowed_for_modbus_readonly_foundation'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateModbusFixturePath(edgeRoot: string, fixturePath: string): ModbusTcpReadonlyValidationResult & {
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

export function validateModbusRegisterMapping(mapping: {
  readonly registerType: string;
  readonly address: number;
  readonly quantity: number;
}): ModbusTcpReadonlyValidationResult {
  const errors: string[] = [];
  if (!['holding', 'input', 'coil', 'discrete'].includes(mapping.registerType)) {
    errors.push(`invalid_register_type:${mapping.registerType}`);
  }
  if (!Number.isInteger(mapping.address) || mapping.address < 0) {
    errors.push(`invalid_address:${mapping.address}`);
  }
  if (!Number.isInteger(mapping.quantity) || mapping.quantity <= 0 || mapping.quantity > MAX_REGISTER_QUANTITY) {
    errors.push(`invalid_quantity:${mapping.quantity}`);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function validateModbusTcpReadonlyConfig(config: ModbusTcpReadonlyConfig): ModbusTcpReadonlyValidationResult {
  const errors: string[] = [];
  if (!config.connectorId) errors.push('connectorId is required');
  if (!config.host) errors.push('host is required');
  if (config.port <= 0 || config.port > 65535) errors.push('port is invalid');
  if (!Number.isInteger(config.unitId) || config.unitId < 1 || config.unitId > 247) {
    errors.push('unitId must be 1..247');
  }
  if (config.pollingIntervalMs <= 0) errors.push('pollingIntervalMs must be > 0');
  if (config.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
  if (config.retries < 0) errors.push('retries must be >= 0');
  if (config.networkEnabled !== false) errors.push('networkEnabled must be false in c3-04 foundation');
  if (config.supportsWriteback !== false) errors.push('supportsWriteback must be false for modbus readonly');
  const hostCheck = validateModbusHost(config.host);
  if (!hostCheck.valid) errors.push(...hostCheck.errors);
  if (!config.fixturePath) errors.push('fixturePath is required');
  for (const mapping of config.registerMappings) {
    const mappingCheck = validateModbusRegisterMapping(mapping);
    if (!mappingCheck.valid) errors.push(...mappingCheck.errors);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function readModbusSyntheticFixture(config: ModbusTcpReadonlyConfig): {
  readonly ok: boolean;
  readonly fixturePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly ModbusTcpReadonlyError[];
} {
  const pathCheck = validateModbusFixturePath('./AN_VANTARIS_EDGE', config.fixturePath);
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

export function parseModbusSyntheticFixture(content: string): {
  readonly ok: boolean;
  readonly fixture: ModbusSyntheticFixture | null;
  readonly errors: readonly ModbusTcpReadonlyError[];
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
  const unitId = asNumber(parsed.unitId);
  if (!Number.isInteger(unitId) || unitId < 1 || unitId > 247) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_invalid_unit_id', message: `invalid unitId: ${unitId}` }],
    };
  }
  const registersRaw = parsed.registers;
  if (!Array.isArray(registersRaw)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_registers_missing', message: 'registers array is required' }],
    };
  }
  const registers: ModbusSyntheticRegister[] = [];
  const errors: ModbusTcpReadonlyError[] = [];
  registersRaw.forEach((item, index) => {
    if (!isObject(item)) {
      errors.push({ code: 'register_invalid_shape', message: 'register must be object', details: { index } });
      return;
    }
    const registerType = asString(item.registerType);
    const address = asNumber(item.address);
    if (!['holding', 'input', 'coil', 'discrete'].includes(registerType)) {
      errors.push({ code: 'register_invalid_type', message: `invalid registerType: ${registerType}`, details: { index } });
      return;
    }
    if (!Number.isInteger(address) || address < 0) {
      errors.push({ code: 'register_invalid_address', message: `invalid address: ${address}`, details: { index } });
      return;
    }
    const qualityRaw = asString(item.quality).toLowerCase();
    registers.push({
      registerType: registerType as ModbusSyntheticRegister['registerType'],
      address,
      pointRef: asString(item.pointRef),
      assetRef: asString(item.assetRef),
      value:
        typeof item.value == 'number' || typeof item.value == 'string' || typeof item.value == 'boolean'
          ? item.value
          : asString(item.value),
      unit: asString(item.unit) || 'synthetic-unit',
      quality: qualityRaw == 'bad' || qualityRaw == 'uncertain' ? qualityRaw : 'good',
      scale: asNumber(item.scale) || 1,
      metadata: isObject(item.metadata) ? item.metadata : {},
    });
  });
  return {
    ok: errors.length == 0,
    fixture: {
      source: asString(parsed.source) || 'synthetic-modbus-device',
      observedAt: asString(parsed.observedAt) || nowIso(),
      unitId,
      registers,
    },
    errors,
  };
}

export function extractModbusRegisterRecords(input: {
  fixture: ModbusSyntheticFixture;
  config: ModbusTcpReadonlyConfig;
}): {
  readonly registers: readonly ModbusSyntheticRegister[];
  readonly errors: readonly ModbusTcpReadonlyError[];
} {
  const errors: ModbusTcpReadonlyError[] = [];
  const mappingByKey = new Map(
    input.config.registerMappings.map((mapping) => [`${mapping.registerType}:${mapping.address}`, mapping]),
  );
  const registers = input.fixture.registers.map((item) => {
    const mapped = mappingByKey.get(`${item.registerType}:${item.address}`);
    if (!mapped) return item;
    return {
      ...item,
      pointRef: item.pointRef || mapped.pointRef,
      assetRef: item.assetRef || mapped.assetRef,
      unit: item.unit || mapped.unit,
      scale: item.scale || mapped.scale,
    };
  });
  registers.forEach((item, index) => {
    if (!item.pointRef || !item.assetRef) {
      errors.push({
        code: 'register_required_field_missing',
        message: 'pointRef and assetRef are required',
        details: { index, address: item.address },
      });
    }
  });
  return { registers, errors };
}

export function mapModbusRegisterToPluginSample(input: {
  connectorId: string;
  sourceSystemId: string;
  observedAt: string;
  sequence: number;
  register: ModbusSyntheticRegister;
}): NormalizedSamplePlaceholder {
  const scaledValue =
    typeof input.register.value == 'number' ? input.register.value * (input.register.scale || 1) : input.register.value;
  return {
    sampleId: `${input.connectorId}-modbus-${input.sequence}`,
    connectorId: input.connectorId,
    sourceSystemId: input.sourceSystemId,
    protocol: 'modbus',
    sampleType: 'telemetry',
    timestamp: input.observedAt,
    payload: {
      registerType: input.register.registerType,
      address: input.register.address,
      pointRef: input.register.pointRef,
      assetRef: input.register.assetRef,
      value: scaledValue,
      rawValue: input.register.value,
      unit: input.register.unit,
      quality: input.register.quality,
      scale: input.register.scale,
      metadata: input.register.metadata,
      synthetic: true,
      writeback: false,
    },
  };
}

export function exportModbusTcpReadonlyEvidence(path: string, payload: ModbusTcpReadonlyEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
