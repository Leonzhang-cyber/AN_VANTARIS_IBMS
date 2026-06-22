import { validateOpcUaReadOnlyPolicy } from '../opcua-readonly-policy.js';
import { validateOpcUaBrowseRequest, validateOpcUaReadRequest } from '../opcua-nodeid-validator.js';
import { validateOpcUaResponse, normalizeOpcUaVariant } from '../opcua-response-validator.js';
import { validateOpcUaService } from '../opcua-service-validator.js';
import {
  validateOpcUaIdentityModel,
  validateOpcUaSecurityProfile,
} from '../opcua-security-validator.js';
import type { OpcUaReadOnlyPolicy, OpcUaReadResult, OpcUaRequestInput, OpcUaResponsePayload } from '../opcua-readonly-types.js';

import type {
  OpcuaProductionAdapterConfig,
  OpcuaProductionErrorCode,
  OpcuaProductionNormalizedRecord,
  OpcuaProductionReadService,
} from './opcua-production-adapter.types.js';
import {
  OPCUA_PRODUCTION_ALLOWED_ATTRIBUTES,
  OPCUA_PRODUCTION_DANGEROUS_KEYS,
  OPCUA_PRODUCTION_DENIED_SERVICES,
  OPCUA_PRODUCTION_FORMULA_PREFIXES,
  OPCUA_PRODUCTION_READ_SERVICES,
} from './opcua-production-adapter.types.js';
import {
  buildFoundationPolicyForProduction,
  createNodeReferenceHash,
  validateProductionResourceLimits,
} from './opcua-production-target-policy.js';

export function validateProductionService(service: string): OpcuaProductionErrorCode | null {
  const normalized = service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  if ((OPCUA_PRODUCTION_DENIED_SERVICES as readonly string[]).includes(normalized)) {
    if (normalized === 'CALL') return 'OPCUA_CALL_METHOD_REJECTED';
    if (normalized.includes('SUBSCRIPTION') || normalized.includes('MONITORED')) return 'OPCUA_SUBSCRIPTION_REJECTED';
    return 'OPCUA_WRITE_SERVICE_REJECTED';
  }
  if (!OPCUA_PRODUCTION_READ_SERVICES.includes(normalized as OpcuaProductionReadService)) {
    return 'OPCUA_SERVICE_NOT_ALLOWED';
  }
  return null;
}

export function validateProductionAdapterConfig(config: OpcuaProductionAdapterConfig): OpcuaProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_OPC_UA_READONLY') return 'OPCUA_CONFIG_INVALID';
  if (config.enabled !== true) return 'OPCUA_ADAPTER_DISABLED';
  if (!config.endpointReferenceId || !config.nodeAllowlistReferenceId) return 'OPCUA_CONFIG_INVALID';
  if (!config.credentialReferenceId || !/^secret:\/\/edge\/opcua\//.test(config.credentialReferenceId)) {
    return 'OPCUA_CREDENTIAL_REFERENCE_INVALID';
  }
  if (!(config.endpointPort >= 1 && config.endpointPort <= 65535)) return 'OPCUA_PORT_NOT_ALLOWED';
  if (config.tcpMode !== 'PRODUCTION_OPC_TCP' && config.tcpMode !== 'LOOPBACK_TEST') return 'OPCUA_CONFIG_INVALID';
  if (config.dnsMode !== 'DENY' && config.dnsMode !== 'INJECTED_TEST') return 'OPCUA_CONFIG_INVALID';
  if (config.maxRetries !== 0) return 'OPCUA_CONFIG_INVALID';
  const serviceError = validateProductionService(config.service);
  if (serviceError) return serviceError;
  if (!Array.isArray(config.reads) || config.reads.length === 0) return 'OPCUA_CONFIG_INVALID';
  if (config.reads.length > config.maxNodes) return 'OPCUA_NODE_LIMIT_EXCEEDED';
  for (const read of config.reads) {
    if (read.nodeId.length > config.maxNodeIdLength) return 'OPCUA_NODE_NOT_ALLOWLISTED';
    if (!OPCUA_PRODUCTION_ALLOWED_ATTRIBUTES.includes(read.attributeId.toUpperCase() as typeof OPCUA_PRODUCTION_ALLOWED_ATTRIBUTES[number])) {
      return 'OPCUA_ATTRIBUTE_NOT_ALLOWLISTED';
    }
  }
  return validateProductionResourceLimits(config);
}

export function mapFoundationRequestError(errors: readonly string[]): OpcuaProductionErrorCode {
  if (errors.includes('OPCUA_WRITE_SERVICE_PROHIBITED')) return 'OPCUA_WRITE_SERVICE_REJECTED';
  if (errors.includes('OPCUA_SUBSCRIPTION_DISABLED')) return 'OPCUA_SUBSCRIPTION_REJECTED';
  if (errors.some((e) => e.includes('CALL'))) return 'OPCUA_CALL_METHOD_REJECTED';
  if (errors.includes('OPCUA_SERVICE_NOT_ALLOWED')) return 'OPCUA_SERVICE_NOT_ALLOWED';
  if (errors.some((e) => e.includes('NODE_ID'))) return 'OPCUA_NODE_NOT_ALLOWLISTED';
  if (errors.includes('OPCUA_ATTRIBUTE_NOT_ALLOWED')) return 'OPCUA_ATTRIBUTE_NOT_ALLOWLISTED';
  if (errors.includes('OPCUA_READ_LIMIT_EXCEEDED') || errors.includes('OPCUA_BROWSE_LIMIT_EXCEEDED')) {
    return 'OPCUA_NODE_LIMIT_EXCEEDED';
  }
  if (errors.includes('PLAINTEXT_CREDENTIAL_PROHIBITED') || errors.includes('INLINE_CERTIFICATE_PROHIBITED')) {
    return 'OPCUA_CREDENTIAL_REFERENCE_INVALID';
  }
  if (errors.includes('OPCUA_INSECURE_ENDPOINT_REJECTED')) return 'OPCUA_INSECURE_ENDPOINT_REJECTED';
  return 'OPCUA_FOUNDATION_VALIDATION_FAILED';
}

export function runFoundationRequestValidation(
  endpoint: { hostname: string; port: number },
  config: OpcuaProductionAdapterConfig,
  nodeAllowlist: readonly string[],
  testMode: boolean,
  serviceOverride?: string,
): OpcuaProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(endpoint, config, nodeAllowlist, testMode);
  const service = serviceOverride ?? (config.service === 'HEALTH_PROBE' ? 'READ' : config.service);
  const endpointUrl = `opc.tcp://${endpoint.hostname}:${endpoint.port}`;

  const requestInput: OpcUaRequestInput = {
    endpointUrl,
    securityPolicy: config.securityPolicy,
    messageSecurityMode: config.messageSecurityMode,
    credentialRef: config.credentialReferenceId,
    clientCertificateRef: config.clientCertificateReferenceId,
    clientPrivateKeyRef: config.clientPrivateKeyReferenceId,
    serverFingerprintRef: config.serverFingerprintReferenceId,
    service,
    reads: config.reads.map((read) => ({
      nodeId: read.nodeId,
      attributeId: read.attributeId,
      indexRange: read.indexRange,
    })),
    browse: config.browse,
  };

  const serviceValidation = validateOpcUaService(service, policy);
  if (!serviceValidation.ok) return mapFoundationRequestError(serviceValidation.errors);

  const securityValidation = validateOpcUaSecurityProfile(requestInput, policy);
  if (!securityValidation.ok) return mapFoundationRequestError(securityValidation.errors);

  const identityValidation = validateOpcUaIdentityModel(requestInput, policy);
  if (!identityValidation.ok) return mapFoundationRequestError(identityValidation.errors);

  if (service === 'READ' || config.service === 'HEALTH_PROBE') {
    const readValidation = validateOpcUaReadRequest(requestInput, policy);
    if (!readValidation.ok) return mapFoundationRequestError(readValidation.errors);
  }

  if (service === 'BROWSE' && config.browse) {
    const browseValidation = validateOpcUaBrowseRequest(config.browse, policy);
    if (!browseValidation.ok) return mapFoundationRequestError(browseValidation.errors);
  }

  if (testMode && config.tcpMode === 'LOOPBACK_TEST') {
    return null;
  }

  const policyValidation = validateOpcUaReadOnlyPolicy({
    ...policy,
    syntheticTransportOnly: false,
  } as unknown as OpcUaReadOnlyPolicy);
  if (!policyValidation.ok) return 'OPCUA_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function mapFoundationResponseError(errors: readonly string[]): OpcuaProductionErrorCode {
  if (errors.includes('OPCUA_REQUEST_HANDLE_MISMATCH')) return 'OPCUA_REQUEST_ID_MISMATCH';
  if (errors.includes('OPCUA_SERVICE_MISMATCH')) return 'OPCUA_SERVICE_MISMATCH';
  if (errors.includes('OPCUA_BAD_STATUS_CODE')) return 'OPCUA_BAD_STATUS_RESPONSE';
  if (errors.includes('OPCUA_UNCERTAIN_STATUS_CODE')) return 'OPCUA_BAD_STATUS_RESPONSE';
  if (errors.includes('OPCUA_RESPONSE_TOO_LARGE')) return 'OPCUA_RESPONSE_SIZE_LIMIT_EXCEEDED';
  if (errors.includes('OPCUA_STRING_LIMIT_EXCEEDED') || errors.includes('OPCUA_VALUE_LIMIT_EXCEEDED')) {
    return 'OPCUA_VALUE_SIZE_LIMIT_EXCEEDED';
  }
  if (errors.includes('OPCUA_NODE_ID_NOT_ALLOWED') || errors.includes('OPCUA_ATTRIBUTE_MISMATCH')) {
    return 'OPCUA_NODE_NOT_ALLOWLISTED';
  }
  return 'OPCUA_FOUNDATION_VALIDATION_FAILED';
}

export function validateFoundationResponse(
  request: {
    requestHandle: number;
    service: string;
    reads: readonly { nodeId: string; attributeId: string }[];
  },
  response: OpcUaResponsePayload,
  endpoint: { hostname: string; port: number },
  config: OpcuaProductionAdapterConfig,
  nodeAllowlist: readonly string[],
  testMode: boolean,
): OpcuaProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(endpoint, config, nodeAllowlist, testMode);
  const validation = validateOpcUaResponse(request, response, policy);
  if (!validation.ok) return mapFoundationResponseError(validation.errors);
  return null;
}

export function normalizeReadResults(
  results: readonly OpcUaReadResult[],
  config: OpcuaProductionAdapterConfig,
  service: string,
  policy: OpcUaReadOnlyPolicy,
): { ok: true; records: OpcuaProductionNormalizedRecord[] } | { ok: false; errorCode: OpcuaProductionErrorCode } {
  const records: OpcuaProductionNormalizedRecord[] = [];
  for (let index = 0; index < results.length; index += 1) {
    const result = results[index];
    const valueText = result.value === null || result.value === undefined ? '' : String(result.value);
    if (valueText.length > config.maxValueBytes) return { ok: false, errorCode: 'OPCUA_VALUE_SIZE_LIMIT_EXCEEDED' };
    const valueTypeUpper = String(result.valueType ?? '').toUpperCase();
    const formulaSensitive = valueTypeUpper === 'STRING' || valueTypeUpper === '';
    if (formulaSensitive) {
      for (const prefix of OPCUA_PRODUCTION_FORMULA_PREFIXES) {
        if (valueText.trimStart().startsWith(prefix) && config.formulaPrefixPolicy === 'REJECT') {
          return { ok: false, errorCode: 'OPCUA_DECODE_FAILED' };
        }
      }
    }
    const fields: Record<string, string> = {
      index: String(index),
      connectorType: 'OPCUA',
      sourceSystem: 'EDGE',
      nodeId: String(result.nodeId),
      attributeId: String(result.attributeId),
      nodeReference: createNodeReferenceHash(String(result.nodeId), String(result.attributeId)),
      statusCode: String(result.statusCode ?? 'Good'),
      valueType: String(result.valueType ?? 'NULL'),
      value: valueText,
      service,
    };
    if (result.sourceTimestamp) fields.sourceTimestamp = String(result.sourceTimestamp);
    if (result.serverTimestamp) fields.serverTimestamp = String(result.serverTimestamp);
    for (const key of OPCUA_PRODUCTION_DANGEROUS_KEYS) {
      if (Object.prototype.hasOwnProperty.call(fields, key)) {
        return { ok: false, errorCode: 'OPCUA_DECODE_FAILED' };
      }
    }
    if (result.valueType) {
      const normalized = normalizeOpcUaVariant(String(result.valueType), result.value, policy);
      if (!normalized.ok) return { ok: false, errorCode: 'OPCUA_DECODE_FAILED' };
    }
    records.push({ fields });
  }
  return { ok: true, records };
}

export function decodeAndNormalizeResponse(
  response: OpcUaResponsePayload & { results: OpcUaReadResult[] },
  endpoint: { hostname: string; port: number },
  config: OpcuaProductionAdapterConfig,
  nodeAllowlist: readonly string[],
  testMode: boolean,
  service: string,
): { ok: true; records: OpcuaProductionNormalizedRecord[] } | { ok: false; errorCode: OpcuaProductionErrorCode } {
  const policy = buildFoundationPolicyForProduction(endpoint, config, nodeAllowlist, testMode);
  const foundationError = validateFoundationResponse(
    {
      requestHandle: response.requestHandle,
      service: service === 'HEALTH_PROBE' ? 'READ' : service,
      reads: config.reads,
    },
    response,
    endpoint,
    config,
    nodeAllowlist,
    testMode,
  );
  if (foundationError) return { ok: false, errorCode: foundationError };
  if ((response.results?.length ?? 0) === 0) return { ok: false, errorCode: 'OPCUA_DECODE_FAILED' };
  return normalizeReadResults(response.results ?? [], config, service, policy);
}

export type { OpcUaReadResult, OpcUaResponsePayload };
