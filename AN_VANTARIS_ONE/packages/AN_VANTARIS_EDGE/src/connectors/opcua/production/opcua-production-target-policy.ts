import { createHash } from 'node:crypto';

import { evaluateOpcUaEndpointRisk, validateOpcUaEndpoint } from '../opcua-endpoint-validator.js';
import type { OpcUaReadOnlyPolicy } from '../opcua-readonly-types.js';

import type {
  OpcuaProductionAdapterConfig,
  OpcuaProductionErrorCode,
  OpcuaProductionResolvedEndpoint,
  OpcuaProductionResourceLimits,
} from './opcua-production-adapter.types.js';
import { OPCUA_PRODUCTION_LIMIT_CAPS, OPCUA_PRODUCTION_METADATA_HOSTS } from './opcua-production-adapter.types.js';

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

export function createEndpointReferenceId(endpointReferenceId: string, service: string, nodeId: string): string {
  const digest = createHash('sha256')
    .update(`${endpointReferenceId}\0${service}\0${nodeId}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `opcua-endpoint:${endpointReferenceId}:${digest}`;
}

export function createEndpointHash(hostname: string, port: number): string {
  return createHash('sha256').update(`${hostname}\0${port}`, 'utf8').digest('hex').slice(0, 16);
}

export function createNodeReferenceHash(nodeId: string, attributeId: string): string {
  return createHash('sha256').update(`${nodeId}\0${attributeId}`, 'utf8').digest('hex').slice(0, 16);
}

export function isMetadataHost(hostname: string): boolean {
  const normalized = normalizeHostname(hostname);
  return OPCUA_PRODUCTION_METADATA_HOSTS.some((host) => normalized === normalizeHostname(host));
}

export function validateResolvedIpAddress(
  ip: string,
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): OpcuaProductionErrorCode | null {
  const normalized = ip.trim().toLowerCase();
  if (isMetadataHost(normalized)) return 'OPCUA_METADATA_ENDPOINT_REJECTED';
  if (normalized === '169.254.169.254' || normalized === '100.100.100.200') return 'OPCUA_METADATA_ENDPOINT_REJECTED';
  if (normalized === '0.0.0.0') return 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  if (LOOPBACK_HOSTS.has(normalized)) {
    return testMode ? null : 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  }
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(normalized)) {
    if (testMode || allowPrivateNetworkReference) return null;
    return 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  }
  if (normalized.startsWith('169.254.') || normalized.startsWith('fe80:') || normalized === '::1') {
    return testMode ? null : 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateAllResolvedIps(
  ips: readonly string[],
  testMode: boolean,
  allowPrivateNetworkReference: boolean,
): OpcuaProductionErrorCode | null {
  if (ips.length === 0) return 'OPCUA_DNS_RESULT_REJECTED';
  for (const ip of ips) {
    const err = validateResolvedIpAddress(ip, testMode, allowPrivateNetworkReference);
    if (err) return err;
  }
  return null;
}

export function buildFoundationPolicyForProduction(
  endpoint: OpcuaProductionResolvedEndpoint,
  config: OpcuaProductionAdapterConfig,
  nodeAllowlist: readonly string[],
  testMode: boolean,
): OpcUaReadOnlyPolicy {
  const numericAllows = nodeAllowlist
    .filter((nodeId) => /^ns=\d+;i=\d+$/.test(nodeId))
    .map((nodeId) => {
      const match = /^ns=(\d+);i=(\d+)$/.exec(nodeId);
      return match ? { namespaceIndex: Number(match[1]), identifier: Number(match[2]) } : null;
    })
    .filter((entry): entry is { namespaceIndex: number; identifier: number } => entry !== null);

  const stringPrefixes = nodeAllowlist
    .filter((nodeId) => nodeId.startsWith('ns=') && nodeId.includes(';s='))
    .map((nodeId) => {
      const match = /^ns=(\d+);s=(.+)$/.exec(nodeId);
      return match ? { namespaceIndex: Number(match[1]), prefix: match[2] } : null;
    })
    .filter((entry): entry is { namespaceIndex: number; prefix: string } => entry !== null);

  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-06',
    classification: 'CONTROLLED_OPC_UA_READ_ONLY_FOUNDATION',
    allowedTransports: ['OPC_TCP'],
    allowedEndpointUrls: testMode ? [`opc.tcp://${endpoint.hostname}:${endpoint.port}`] : [],
    allowedHosts: testMode ? [normalizeHostname(endpoint.hostname)] : [],
    allowedPorts: testMode ? [endpoint.port] : [config.endpointPort],
    allowedSecurityPolicies: ['Basic256Sha256', 'Aes128_Sha256_RsaOaep', 'Aes256_Sha256_RsaPss'],
    allowedMessageSecurityModes: ['SIGN', 'SIGN_AND_ENCRYPT'],
    anonymousAllowed: false,
    credentialMode: 'REFERENCE_ONLY',
    certificateMode: 'REFERENCE_ONLY',
    trustedServerFingerprintRefs: config.serverFingerprintReferenceId ? [config.serverFingerprintReferenceId] : [],
    hostnameVerificationRequired: true,
    applicationUriVerificationRequired: true,
    allowedServices: ['READ', 'BROWSE', 'BROWSE_NEXT', 'TRANSLATE_BROWSE_PATHS_TO_NODE_IDS'],
    deniedServices: [
      'WRITE',
      'CALL',
      'ADD_NODES',
      'DELETE_NODES',
      'ADD_REFERENCES',
      'DELETE_REFERENCES',
      'CREATE_SUBSCRIPTION',
      'CREATE_MONITORED_ITEMS',
      'MODIFY_MONITORED_ITEMS',
      'DELETE_MONITORED_ITEMS',
      'HISTORY_UPDATE',
    ],
    subscriptionsAllowed: false,
    monitoredItemsAllowed: false,
    historyReadAllowed: false,
    allowedNamespaceIndexes: [0, 1, 2],
    allowedNamespaceUris: [],
    allowedNodeIdTypes: ['NUMERIC', 'STRING'],
    allowedNumericNodeIds: numericAllows.length > 0 ? numericAllows : [{ namespaceIndex: 0, identifier: 2258 }],
    allowedStringNodeIdPrefixes: stringPrefixes.length > 0 ? stringPrefixes : [{ namespaceIndex: 1, prefix: 'UFMS.' }],
    deniedStringNodeIdPrefixes: [],
    allowedAttributes: [
      'VALUE',
      'DISPLAY_NAME',
      'BROWSE_NAME',
      'DESCRIPTION',
      'DATA_TYPE',
      'STATUS_CODE',
      'SOURCE_TIMESTAMP',
      'SERVER_TIMESTAMP',
    ],
    allowedVariantTypes: ['NULL', 'BOOLEAN', 'INT32', 'UINT32', 'DOUBLE', 'STRING', 'DATETIME'],
    rejectUncertainStatusCodes: true,
    maxNodesPerRead: Math.min(config.maxNodes, OPCUA_PRODUCTION_LIMIT_CAPS.maxNodes),
    maxNodesPerBrowse: Math.min(config.maxBrowseNodes, OPCUA_PRODUCTION_LIMIT_CAPS.maxBrowseNodes),
    maxBrowseDepth: Math.min(config.maxBrowseDepth, OPCUA_PRODUCTION_LIMIT_CAPS.maxBrowseDepth),
    maxResponseBytes: Math.min(config.maxResponseBytes, OPCUA_PRODUCTION_LIMIT_CAPS.maxResponseBytes),
    maxArrayLength: 64,
    maxStringLength: 8192,
    maxContinuationPointLength: 128,
    timeoutMs: Math.min(config.responseTimeoutMs, OPCUA_PRODUCTION_LIMIT_CAPS.responseTimeoutMs),
    maxRetryAttempts: 0,
    retryableErrors: [],
    nonRetryableErrors: [],
    backoffBaseMs: 100,
    backoffMultiplier: 2,
    backoffMaxMs: 5000,
    endpointDiscoveryMode: 'MODELED_ONLY',
    networkAccessAllowed: false,
    dnsResolutionMode: 'MODELED_ONLY',
    syntheticTransportOnly: false,
    writeOperationsAllowed: false,
    candidateStatus: 'CONTROLLED_OPC_UA_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_06_OPC_UA_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  } as unknown as OpcUaReadOnlyPolicy;
}

export function validateProductionEndpoint(
  endpoint: OpcuaProductionResolvedEndpoint,
  config: OpcuaProductionAdapterConfig,
  testMode: boolean,
): OpcuaProductionErrorCode | null {
  if (!(endpoint.port >= 1 && endpoint.port <= 65535)) return 'OPCUA_PORT_NOT_ALLOWED';
  if (isMetadataHost(endpoint.hostname)) return 'OPCUA_METADATA_ENDPOINT_REJECTED';

  if (testMode && config.tcpMode === 'LOOPBACK_TEST') {
    if (!LOOPBACK_HOSTS.has(normalizeHostname(endpoint.hostname))) return 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
    if (endpoint.port !== config.endpointPort) return 'OPCUA_PORT_NOT_ALLOWED';
    return null;
  }

  const endpointUrl = `opc.tcp://${endpoint.hostname}:${endpoint.port}`;
  const policy = buildFoundationPolicyForProduction(endpoint, config, ['ns=0;i=2258'], false);
  const validation = validateOpcUaEndpoint(endpointUrl, policy);
  if (!validation.ok) {
    if (validation.errors.some((e) => e.includes('METADATA'))) return 'OPCUA_METADATA_ENDPOINT_REJECTED';
    if (validation.errors.some((e) => e.includes('PORT'))) return 'OPCUA_PORT_NOT_ALLOWED';
    return 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  }

  const risk = evaluateOpcUaEndpointRisk(validation.endpoint!, policy);
  if (!risk.ok) {
    if (risk.errors.some((e) => e.includes('METADATA'))) return 'OPCUA_METADATA_ENDPOINT_REJECTED';
    return 'OPCUA_ENDPOINT_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateProductionResourceLimits(limits: OpcuaProductionResourceLimits): OpcuaProductionErrorCode | null {
  if (!Number.isInteger(limits.maxNodes) || limits.maxNodes < 1 || limits.maxNodes > OPCUA_PRODUCTION_LIMIT_CAPS.maxNodes) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.maxBrowseNodes) || limits.maxBrowseNodes < 1 || limits.maxBrowseNodes > OPCUA_PRODUCTION_LIMIT_CAPS.maxBrowseNodes) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.maxNodeIdLength) || limits.maxNodeIdLength < 1 || limits.maxNodeIdLength > OPCUA_PRODUCTION_LIMIT_CAPS.maxNodeIdLength) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.maxValueBytes) || limits.maxValueBytes < 1 || limits.maxValueBytes > OPCUA_PRODUCTION_LIMIT_CAPS.maxValueBytes) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.maxResponseBytes) || limits.maxResponseBytes < 1 || limits.maxResponseBytes > OPCUA_PRODUCTION_LIMIT_CAPS.maxResponseBytes) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.responseTimeoutMs) || limits.responseTimeoutMs < 1 || limits.responseTimeoutMs > OPCUA_PRODUCTION_LIMIT_CAPS.responseTimeoutMs) {
    return 'OPCUA_CONFIG_INVALID';
  }
  if (!Number.isInteger(limits.maxRetries) || limits.maxRetries !== 0) return 'OPCUA_CONFIG_INVALID';
  if (!Number.isInteger(limits.maxProcessingMilliseconds) || limits.maxProcessingMilliseconds < 1 || limits.maxProcessingMilliseconds > OPCUA_PRODUCTION_LIMIT_CAPS.maxProcessingMilliseconds) {
    return 'OPCUA_CONFIG_INVALID';
  }
  return null;
}
