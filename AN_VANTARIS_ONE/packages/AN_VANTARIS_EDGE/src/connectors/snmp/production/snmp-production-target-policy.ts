import { createHash } from 'node:crypto';

import { evaluateSnmpTargetRisk, normalizeSnmpTarget, validateSnmpTarget } from '../snmp-target-validator.js';
import type { SnmpReadOnlyPolicy } from '../snmp-readonly-types.js';

import type {
  SnmpProductionAdapterConfig,
  SnmpProductionErrorCode,
  SnmpProductionResolvedTarget,
  SnmpProductionResourceLimits,
} from './snmp-production-adapter.types.js';
import {
  SNMP_PRODUCTION_LIMIT_CAPS,
  SNMP_PRODUCTION_METADATA_HOSTS,
} from './snmp-production-adapter.types.js';

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

export function createTargetReferenceId(targetReferenceId: string, operation: string, oid: string): string {
  const digest = createHash('sha256')
    .update(`${targetReferenceId}\0${operation}\0${oid}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `snmp-target:${targetReferenceId}:${digest}`;
}

export function createTargetHash(hostname: string, port: number): string {
  return createHash('sha256').update(`${hostname}\0${port}`, 'utf8').digest('hex').slice(0, 16);
}

export function createOidReferenceHash(oid: string): string {
  return createHash('sha256').update(oid, 'utf8').digest('hex').slice(0, 16);
}

export function isMetadataHost(hostname: string): boolean {
  const normalized = normalizeHostname(hostname);
  return SNMP_PRODUCTION_METADATA_HOSTS.some((host) => normalized === normalizeHostname(host));
}

export function validateResolvedIpAddress(
  ip: string,
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): SnmpProductionErrorCode | null {
  const normalized = ip.trim().toLowerCase();
  if (isMetadataHost(normalized)) return 'SNMP_METADATA_TARGET_REJECTED';
  if (normalized === '169.254.169.254' || normalized === '100.100.100.200') return 'SNMP_METADATA_TARGET_REJECTED';
  if (normalized === '0.0.0.0') return 'SNMP_TARGET_NOT_ALLOWLISTED';
  if (LOOPBACK_HOSTS.has(normalized)) {
    return testMode ? null : 'SNMP_TARGET_NOT_ALLOWLISTED';
  }
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(normalized)) {
    if (testMode || allowPrivateNetworkReference) return null;
    return 'SNMP_TARGET_NOT_ALLOWLISTED';
  }
  if (normalized.startsWith('169.254.') || normalized.startsWith('fe80:') || normalized === '::1') {
    return testMode ? null : 'SNMP_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateAllResolvedIps(
  ips: readonly string[],
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): SnmpProductionErrorCode | null {
  if (ips.length === 0) return 'SNMP_DNS_RESULT_REJECTED';
  for (const ip of ips) {
    const err = validateResolvedIpAddress(ip, testMode, allowPrivateNetworkReference);
    if (err) return err;
  }
  return null;
}

export function buildFoundationPolicyForProduction(
  target: SnmpProductionResolvedTarget,
  config: SnmpProductionAdapterConfig,
  oidPrefixes: readonly string[],
  testMode: boolean,
): SnmpReadOnlyPolicy {
  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-03',
    classification: 'CONTROLLED_SNMP_READ_ONLY_FOUNDATION',
    allowedVersions: ['3'],
    preferredVersion: '3',
    productionAllowedVersions: ['3'],
    allowedOperations: ['GET', 'GETNEXT', 'GETBULK'],
    deniedOperations: ['SET', 'INFORM', 'TRAP_SEND'],
    allowedTargets: testMode ? [normalizeHostname(target.hostname)] : [],
    deniedTargets: [...SNMP_PRODUCTION_METADATA_HOSTS],
    defaultPort: target.port,
    allowedOidPrefixes: [...oidPrefixes],
    deniedOidPrefixes: ['1.3.6.1.6.3.15'],
    credentialMode: 'REFERENCE_ONLY',
    plaintextCommunityAllowed: false,
    plaintextAuthSecretAllowed: false,
    plaintextPrivacySecretAllowed: false,
    timeoutMs: Math.min(config.responseTimeoutMs, SNMP_PRODUCTION_LIMIT_CAPS.responseTimeoutMs),
    maxRetryAttempts: 0,
    retryableErrors: [],
    nonRetryableErrors: [],
    backoffBaseMs: 100,
    backoffMultiplier: 2,
    backoffMaxMs: 5000,
    maxVarbinds: Math.min(config.maxVarbinds, SNMP_PRODUCTION_LIMIT_CAPS.maxVarbinds),
    maxResponseBytes: Math.min(config.maxResponseBytes, SNMP_PRODUCTION_LIMIT_CAPS.maxResponseBytes),
    maxWalkRows: Math.min(config.maxWalkRows, SNMP_PRODUCTION_LIMIT_CAPS.maxWalkRows),
    maxWalkDepth: Math.min(config.maxWalkDepth, SNMP_PRODUCTION_LIMIT_CAPS.maxWalkDepth),
    maxOidComponents: Math.min(config.maxOidLength, SNMP_PRODUCTION_LIMIT_CAPS.maxOidLength),
    maxOidComponentValue: 4294967295,
    networkAccessAllowed: false,
    dnsResolutionMode: 'MODELED_ONLY',
    syntheticTransportOnly: false,
    writeOperationsAllowed: false,
    allowedVarbindTypes: [
      'INTEGER',
      'OCTET_STRING',
      'OBJECT_IDENTIFIER',
      'IP_ADDRESS',
      'COUNTER32',
      'GAUGE32',
      'TIMETICKS',
      'COUNTER64',
      'NULL',
    ],
    candidateStatus: 'CONTROLLED_SNMP_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_03_SNMP_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  } as unknown as SnmpReadOnlyPolicy;
}

export function validateProductionTarget(
  target: SnmpProductionResolvedTarget,
  config: SnmpProductionAdapterConfig,
  testMode: boolean,
): SnmpProductionErrorCode | null {
  if (!(target.port >= 1 && target.port <= 65535)) return 'SNMP_PORT_NOT_ALLOWED';
  if (isMetadataHost(target.hostname)) return 'SNMP_METADATA_TARGET_REJECTED';

  if (testMode && config.udpMode === 'LOOPBACK_TEST') {
    if (!LOOPBACK_HOSTS.has(normalizeHostname(target.hostname))) return 'SNMP_TARGET_NOT_ALLOWLISTED';
    if (target.port !== config.targetPort) return 'SNMP_PORT_NOT_ALLOWED';
    return null;
  }

  const policy = buildFoundationPolicyForProduction(target, config, ['1.3.6.1.2.1'], false);
  const validation = validateSnmpTarget(target.hostname, target.port, policy);
  if (!validation.ok) {
    if (validation.errors.some((e) => e.includes('METADATA'))) return 'SNMP_METADATA_TARGET_REJECTED';
    if (validation.errors.some((e) => e.includes('PORT'))) return 'SNMP_PORT_NOT_ALLOWED';
    return 'SNMP_TARGET_NOT_ALLOWLISTED';
  }

  const normalized = normalizeSnmpTarget(target.hostname, target.port, policy);
  if (!normalized) return 'SNMP_TARGET_NOT_ALLOWLISTED';
  const risk = evaluateSnmpTargetRisk(normalized, policy);
  if (!risk.ok) {
    if (risk.errors.some((e) => e.includes('METADATA'))) return 'SNMP_METADATA_TARGET_REJECTED';
    return 'SNMP_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validatePositiveInt(value: unknown, min: number, max: number): boolean {
  return typeof value === 'number' && Number.isInteger(value) && Number.isFinite(value) && value >= min && value <= max;
}

export function validateProductionResourceLimits(limits: SnmpProductionResourceLimits): SnmpProductionErrorCode | null {
  if (!validatePositiveInt(limits.connectTimeoutMs, 1, SNMP_PRODUCTION_LIMIT_CAPS.connectTimeoutMs)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.responseTimeoutMs, 1, SNMP_PRODUCTION_LIMIT_CAPS.responseTimeoutMs)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxResponseBytes, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxResponseBytes)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxOids, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxOids)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxVarbinds, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxVarbinds)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxWalkDepth, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxWalkDepth)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxWalkRows, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxWalkRows)) return 'SNMP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxBulkRepetitions, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxBulkRepetitions)) {
    return 'SNMP_CONFIG_INVALID';
  }
  if (!validatePositiveInt(limits.maxOidLength, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxOidLength)) return 'SNMP_CONFIG_INVALID';
  if (!Number.isInteger(limits.maxRetries) || limits.maxRetries < 0 || limits.maxRetries > SNMP_PRODUCTION_LIMIT_CAPS.maxRetries) {
    return 'SNMP_CONFIG_INVALID';
  }
  if (!validatePositiveInt(limits.maxProcessingMilliseconds, 1, SNMP_PRODUCTION_LIMIT_CAPS.maxProcessingMilliseconds)) {
    return 'SNMP_CONFIG_INVALID';
  }
  return null;
}
