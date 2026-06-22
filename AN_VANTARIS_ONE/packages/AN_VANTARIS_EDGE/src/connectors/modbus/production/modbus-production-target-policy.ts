import { createHash } from 'node:crypto';

import { evaluateModbusTargetRisk, normalizeModbusTarget, validateModbusTarget } from '../modbus-target-validator.js';
import type { ModbusTcpReadOnlyPolicy } from '../modbus-readonly-types.js';

import type {
  ModbusProductionAdapterConfig,
  ModbusProductionErrorCode,
  ModbusProductionResolvedTarget,
  ModbusProductionResourceLimits,
} from './modbus-production-adapter.types.js';
import {
  MODBUS_PRODUCTION_COIL_MAX_QUANTITY,
  MODBUS_PRODUCTION_LIMIT_CAPS,
  MODBUS_PRODUCTION_METADATA_HOSTS,
  MODBUS_PRODUCTION_REGISTER_MAX_QUANTITY,
} from './modbus-production-adapter.types.js';

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

export function createTargetReferenceId(targetReferenceId: string, functionCode: number, startAddress: number): string {
  const digest = createHash('sha256')
    .update(`${targetReferenceId}\0${functionCode}\0${startAddress}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `modbus-target:${targetReferenceId}:${digest}`;
}

export function createTargetHash(hostname: string, port: number): string {
  return createHash('sha256').update(`${hostname}\0${port}`, 'utf8').digest('hex').slice(0, 16);
}

export function isMetadataHost(hostname: string): boolean {
  const normalized = normalizeHostname(hostname);
  return MODBUS_PRODUCTION_METADATA_HOSTS.some((host) => normalized === normalizeHostname(host));
}

export function validateResolvedIpAddress(
  ip: string,
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): ModbusProductionErrorCode | null {
  const normalized = ip.trim().toLowerCase();
  if (isMetadataHost(normalized)) return 'MODBUS_METADATA_TARGET_REJECTED';
  if (normalized === '169.254.169.254' || normalized === '100.100.100.200') return 'MODBUS_METADATA_TARGET_REJECTED';
  if (normalized === '0.0.0.0') return 'MODBUS_TARGET_NOT_ALLOWLISTED';
  if (LOOPBACK_HOSTS.has(normalized)) {
    return testMode ? null : 'MODBUS_TARGET_NOT_ALLOWLISTED';
  }
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(normalized)) {
    if (testMode || allowPrivateNetworkReference) return null;
    return 'MODBUS_TARGET_NOT_ALLOWLISTED';
  }
  if (normalized.startsWith('169.254.') || normalized.startsWith('fe80:') || normalized === '::1') {
    return testMode ? null : 'MODBUS_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateAllResolvedIps(
  ips: readonly string[],
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): ModbusProductionErrorCode | null {
  if (ips.length === 0) return 'MODBUS_DNS_RESULT_REJECTED';
  for (const ip of ips) {
    const err = validateResolvedIpAddress(ip, testMode, allowPrivateNetworkReference);
    if (err) return err;
  }
  return null;
}

export function buildFoundationPolicyForProduction(
  target: ModbusProductionResolvedTarget,
  config: ModbusProductionAdapterConfig,
  testMode: boolean,
): ModbusTcpReadOnlyPolicy {
  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-04',
    classification: 'CONTROLLED_MODBUS_TCP_READ_ONLY_FOUNDATION',
    allowedTransports: ['MODBUS_TCP'],
    allowedFunctionCodes: [1, 2, 3, 4],
    deniedFunctionCodes: [5, 6, 15, 16, 22, 23],
    allowedTargets: testMode ? [normalizeHostname(target.hostname)] : [],
    deniedTargets: [...MODBUS_PRODUCTION_METADATA_HOSTS],
    allowedPorts: testMode ? [target.port] : [config.targetPort],
    allowedUnitIds: [config.unitId],
    registerSpaces: ['COIL', 'DISCRETE_INPUT', 'HOLDING_REGISTER', 'INPUT_REGISTER'],
    allowedAddressRanges: [
      { space: 'COIL', start: 0, end: 65535 },
      { space: 'DISCRETE_INPUT', start: 0, end: 65535 },
      { space: 'HOLDING_REGISTER', start: 0, end: 65535 },
      { space: 'INPUT_REGISTER', start: 0, end: 65535 },
    ],
    maxRegistersPerRequest: Math.min(config.maxQuantity, MODBUS_PRODUCTION_REGISTER_MAX_QUANTITY),
    maxCoilsPerRequest: Math.min(config.maxQuantity, MODBUS_PRODUCTION_COIL_MAX_QUANTITY),
    maxResponseBytes: Math.min(config.maxFrameBytes, MODBUS_PRODUCTION_LIMIT_CAPS.maxFrameBytes),
    timeoutMs: Math.min(config.responseTimeoutMs, MODBUS_PRODUCTION_LIMIT_CAPS.responseTimeoutMs),
    maxRetryAttempts: 0,
    retryableErrors: [],
    nonRetryableErrors: [],
    backoffBaseMs: 100,
    backoffMultiplier: 2,
    backoffMaxMs: 5000,
    byteOrder: config.byteOrder,
    wordOrder: config.wordOrder,
    networkAccessAllowed: false,
    dnsResolutionMode: 'MODELED_ONLY',
    syntheticTransportOnly: false,
    writeOperationsAllowed: false,
    candidateStatus: 'CONTROLLED_MODBUS_TCP_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_04_MODBUS_TCP_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  } as unknown as ModbusTcpReadOnlyPolicy;
}

export function validateProductionTarget(
  target: ModbusProductionResolvedTarget,
  config: ModbusProductionAdapterConfig,
  testMode: boolean,
): ModbusProductionErrorCode | null {
  if (!(target.port >= 1 && target.port <= 65535)) return 'MODBUS_PORT_NOT_ALLOWED';
  if (isMetadataHost(target.hostname)) return 'MODBUS_METADATA_TARGET_REJECTED';

  if (testMode && config.tcpMode === 'LOOPBACK_TEST') {
    if (!LOOPBACK_HOSTS.has(normalizeHostname(target.hostname))) return 'MODBUS_TARGET_NOT_ALLOWLISTED';
    if (target.port !== config.targetPort) return 'MODBUS_PORT_NOT_ALLOWED';
    return null;
  }

  const policy = buildFoundationPolicyForProduction(target, config, false);
  const validation = validateModbusTarget(target.hostname, target.port, policy);
  if (!validation.ok) {
    if (validation.errors.some((e) => e.includes('METADATA'))) return 'MODBUS_METADATA_TARGET_REJECTED';
    if (validation.errors.some((e) => e.includes('PORT'))) return 'MODBUS_PORT_NOT_ALLOWED';
    return 'MODBUS_TARGET_NOT_ALLOWLISTED';
  }

  const normalized = normalizeModbusTarget(target.hostname, target.port, policy);
  if (!normalized) return 'MODBUS_TARGET_NOT_ALLOWLISTED';
  const risk = evaluateModbusTargetRisk(normalized, policy);
  if (!risk.ok) {
    if (risk.errors.some((e) => e.includes('METADATA'))) return 'MODBUS_METADATA_TARGET_REJECTED';
    return 'MODBUS_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validatePositiveInt(value: unknown, min: number, max: number): boolean {
  return typeof value === 'number' && Number.isInteger(value) && value >= min && value <= max;
}

export function validateProductionResourceLimits(limits: ModbusProductionResourceLimits): ModbusProductionErrorCode | null {
  if (!validatePositiveInt(limits.maxFrameBytes, 1, MODBUS_PRODUCTION_LIMIT_CAPS.maxFrameBytes)) return 'MODBUS_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxQuantity, 1, MODBUS_PRODUCTION_LIMIT_CAPS.maxQuantity)) return 'MODBUS_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxRegisterAddress, 1, MODBUS_PRODUCTION_LIMIT_CAPS.maxRegisterAddress)) return 'MODBUS_CONFIG_INVALID';
  if (!validatePositiveInt(limits.connectTimeoutMs, 1, MODBUS_PRODUCTION_LIMIT_CAPS.connectTimeoutMs)) return 'MODBUS_CONFIG_INVALID';
  if (!validatePositiveInt(limits.responseTimeoutMs, 1, MODBUS_PRODUCTION_LIMIT_CAPS.responseTimeoutMs)) return 'MODBUS_CONFIG_INVALID';
  if (!Number.isInteger(limits.maxRetryCount) || limits.maxRetryCount < 0 || limits.maxRetryCount > MODBUS_PRODUCTION_LIMIT_CAPS.maxRetryCount) {
    return 'MODBUS_CONFIG_INVALID';
  }
  if (!validatePositiveInt(limits.maxProcessingMilliseconds, 1, MODBUS_PRODUCTION_LIMIT_CAPS.maxProcessingMilliseconds)) {
    return 'MODBUS_CONFIG_INVALID';
  }
  return null;
}

export function maxQuantityForFunctionCode(functionCode: number): number {
  return functionCode === 1 || functionCode === 2
    ? MODBUS_PRODUCTION_COIL_MAX_QUANTITY
    : MODBUS_PRODUCTION_REGISTER_MAX_QUANTITY;
}
