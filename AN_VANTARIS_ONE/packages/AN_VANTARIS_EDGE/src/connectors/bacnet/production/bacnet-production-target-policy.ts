import { createHash } from 'node:crypto';

import { evaluateBacnetTargetRisk, normalizeBacnetTarget, validateBacnetTarget } from '../bacnet-target-validator.js';
import type { BacnetIpReadOnlyPolicy, BacnetObjectType, BacnetPropertyId } from '../bacnet-readonly-types.js';

import type {
  BacnetProductionAdapterConfig,
  BacnetProductionErrorCode,
  BacnetProductionResolvedTarget,
  BacnetProductionResourceLimits,
} from './bacnet-production-adapter.types.js';
import { BACNET_PRODUCTION_LIMIT_CAPS, BACNET_PRODUCTION_METADATA_HOSTS } from './bacnet-production-adapter.types.js';

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

export function createTargetReferenceId(targetReferenceId: string, service: string, objectType: string): string {
  const digest = createHash('sha256')
    .update(`${targetReferenceId}\0${service}\0${objectType}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `bacnet-target:${targetReferenceId}:${digest}`;
}

export function createTargetHash(hostname: string, port: number): string {
  return createHash('sha256').update(`${hostname}\0${port}`, 'utf8').digest('hex').slice(0, 16);
}

export function createObjectPropertyReferenceHash(objectType: string, propertyId: string): string {
  return createHash('sha256').update(`${objectType}\0${propertyId}`, 'utf8').digest('hex').slice(0, 16);
}

export function isMetadataHost(hostname: string): boolean {
  const normalized = normalizeHostname(hostname);
  return BACNET_PRODUCTION_METADATA_HOSTS.some((host) => normalized === normalizeHostname(host));
}

export function validateResolvedIpAddress(
  ip: string,
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): BacnetProductionErrorCode | null {
  const normalized = ip.trim().toLowerCase();
  if (isMetadataHost(normalized)) return 'BACNET_METADATA_TARGET_REJECTED';
  if (normalized === '169.254.169.254' || normalized === '100.100.100.200') return 'BACNET_METADATA_TARGET_REJECTED';
  if (normalized === '0.0.0.0') return 'BACNET_TARGET_NOT_ALLOWLISTED';
  if (LOOPBACK_HOSTS.has(normalized)) {
    return testMode ? null : 'BACNET_TARGET_NOT_ALLOWLISTED';
  }
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(normalized)) {
    if (testMode || allowPrivateNetworkReference) return null;
    return 'BACNET_TARGET_NOT_ALLOWLISTED';
  }
  if (normalized.startsWith('169.254.') || normalized.startsWith('fe80:') || normalized === '::1') {
    return testMode ? null : 'BACNET_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateAllResolvedIps(
  ips: readonly string[],
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): BacnetProductionErrorCode | null {
  if (ips.length === 0) return 'BACNET_DNS_RESULT_REJECTED';
  for (const ip of ips) {
    const err = validateResolvedIpAddress(ip, testMode, allowPrivateNetworkReference);
    if (err) return err;
  }
  return null;
}

export function buildFoundationPolicyForProduction(
  target: BacnetProductionResolvedTarget,
  config: BacnetProductionAdapterConfig,
  objectTypes: readonly BacnetObjectType[],
  properties: readonly BacnetPropertyId[],
  testMode: boolean,
): BacnetIpReadOnlyPolicy {
  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-05',
    classification: 'CONTROLLED_BACNET_IP_READ_ONLY_FOUNDATION',
    allowedTransports: ['BACNET_IP'],
    allowedTargets: testMode ? [normalizeHostname(target.hostname)] : [],
    deniedTargets: [...BACNET_PRODUCTION_METADATA_HOSTS],
    allowedPorts: testMode ? [target.port] : [config.targetPort],
    allowedDeviceInstances: [config.deviceInstance],
    allowedServices: ['READ_PROPERTY', 'READ_PROPERTY_MULTIPLE'],
    deniedServices: [
      'WRITE_PROPERTY',
      'WRITE_PROPERTY_MULTIPLE',
      'SUBSCRIBE_COV',
      'SUBSCRIBE_COV_PROPERTY',
      'DEVICE_COMMUNICATION_CONTROL',
      'REINITIALIZE_DEVICE',
      'ATOMIC_WRITE_FILE',
      'ADD_LIST_ELEMENT',
      'REMOVE_LIST_ELEMENT',
      'CREATE_OBJECT',
      'DELETE_OBJECT',
    ],
    allowedObjectTypes: [...objectTypes],
    allowedObjectInstanceRanges: objectTypes.map((objectType) => ({
      objectType,
      start: 0,
      end: 4194302,
    })),
    allowedProperties: [...properties],
    deniedProperties: ['RECIPIENT_LIST', 'PRIORITY_ARRAY'],
    discoveryMode: 'MODELED_ONLY',
    broadcastAllowed: false,
    bbmdAllowed: false,
    foreignDeviceRegistrationAllowed: false,
    covSubscriptionAllowed: false,
    maxObjectsPerRequest: Math.min(config.maxObjects, BACNET_PRODUCTION_LIMIT_CAPS.maxObjects),
    maxPropertiesPerRequest: Math.min(config.maxProperties, BACNET_PRODUCTION_LIMIT_CAPS.maxProperties),
    maxResponseBytes: Math.min(config.maxResponseBytes, BACNET_PRODUCTION_LIMIT_CAPS.maxResponseBytes),
    maxApduBytes: Math.min(config.maxApduBytes, BACNET_PRODUCTION_LIMIT_CAPS.maxApduBytes),
    maxArrayIndex: 65535,
    maxInvokeId: 255,
    segmentationAllowed: false,
    timeoutMs: Math.min(config.responseTimeoutMs, BACNET_PRODUCTION_LIMIT_CAPS.responseTimeoutMs),
    maxRetryAttempts: 0,
    retryableErrors: [],
    nonRetryableErrors: [],
    backoffBaseMs: 100,
    backoffMultiplier: 2,
    backoffMaxMs: 5000,
    networkAccessAllowed: false,
    dnsResolutionMode: 'MODELED_ONLY',
    syntheticTransportOnly: false,
    writeOperationsAllowed: false,
    allowedValueTypes: [
      'NULL',
      'BOOLEAN',
      'UNSIGNED',
      'SIGNED',
      'REAL',
      'DOUBLE',
      'CHARACTER_STRING',
      'ENUMERATED',
      'OBJECT_IDENTIFIER',
    ],
    candidateStatus: 'CONTROLLED_BACNET_IP_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_05_BACNET_IP_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  } as unknown as BacnetIpReadOnlyPolicy;
}

export function validateProductionTarget(
  target: BacnetProductionResolvedTarget,
  config: BacnetProductionAdapterConfig,
  testMode: boolean,
): BacnetProductionErrorCode | null {
  if (!(target.port >= 1 && target.port <= 65535)) return 'BACNET_PORT_NOT_ALLOWED';
  if (isMetadataHost(target.hostname)) return 'BACNET_METADATA_TARGET_REJECTED';

  if (testMode && config.udpMode === 'LOOPBACK_TEST') {
    if (!LOOPBACK_HOSTS.has(normalizeHostname(target.hostname))) return 'BACNET_TARGET_NOT_ALLOWLISTED';
    if (target.port !== config.targetPort) return 'BACNET_PORT_NOT_ALLOWED';
    return null;
  }

  const policy = buildFoundationPolicyForProduction(target, config, ['DEVICE'], ['PRESENT_VALUE'], false);
  const validation = validateBacnetTarget(target.hostname, target.port, policy, { broadcast: false });
  if (!validation.ok) {
    if (validation.errors.some((e) => e.includes('METADATA'))) return 'BACNET_METADATA_TARGET_REJECTED';
    if (validation.errors.some((e) => e.includes('PORT'))) return 'BACNET_PORT_NOT_ALLOWED';
    return 'BACNET_TARGET_NOT_ALLOWLISTED';
  }

  const normalized = normalizeBacnetTarget(target.hostname, target.port, policy);
  if (!normalized) return 'BACNET_TARGET_NOT_ALLOWLISTED';
  const risk = evaluateBacnetTargetRisk(normalized, policy);
  if (!risk.ok) {
    if (risk.errors.some((e) => e.includes('METADATA'))) return 'BACNET_METADATA_TARGET_REJECTED';
    return 'BACNET_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validatePositiveInt(value: unknown, min: number, max: number): boolean {
  return typeof value === 'number' && Number.isInteger(value) && Number.isFinite(value) && value >= min && value <= max;
}

export function validateProductionResourceLimits(limits: BacnetProductionResourceLimits): BacnetProductionErrorCode | null {
  if (!validatePositiveInt(limits.invokeTimeoutMs, 1, BACNET_PRODUCTION_LIMIT_CAPS.invokeTimeoutMs)) return 'BACNET_CONFIG_INVALID';
  if (!validatePositiveInt(limits.responseTimeoutMs, 1, BACNET_PRODUCTION_LIMIT_CAPS.responseTimeoutMs)) return 'BACNET_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxResponseBytes, 1, BACNET_PRODUCTION_LIMIT_CAPS.maxResponseBytes)) return 'BACNET_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxApduBytes, 1, BACNET_PRODUCTION_LIMIT_CAPS.maxApduBytes)) return 'BACNET_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxProperties, 1, BACNET_PRODUCTION_LIMIT_CAPS.maxProperties)) return 'BACNET_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxObjects, 1, BACNET_PRODUCTION_LIMIT_CAPS.maxObjects)) return 'BACNET_CONFIG_INVALID';
  if (!Number.isInteger(limits.maxSegments) || limits.maxSegments !== 0) return 'BACNET_CONFIG_INVALID';
  if (!Number.isInteger(limits.maxRetries) || limits.maxRetries < 0 || limits.maxRetries > BACNET_PRODUCTION_LIMIT_CAPS.maxRetries) {
    return 'BACNET_CONFIG_INVALID';
  }
  if (!validatePositiveInt(limits.maxProcessingMilliseconds, 1, BACNET_PRODUCTION_LIMIT_CAPS.maxProcessingMilliseconds)) {
    return 'BACNET_CONFIG_INVALID';
  }
  return null;
}
