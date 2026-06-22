import { validateBacnetReadOnlyPolicy } from '../bacnet-readonly-policy.js';
import { validateBacnetRequest } from '../bacnet-property-validator.js';
import { validateBacnetResponse, normalizeBacnetValue } from '../bacnet-response-validator.js';
import type {
  BacnetIpReadOnlyPolicy,
  BacnetObjectType,
  BacnetPropertyId,
  BacnetPropertyRead,
  BacnetPropertyResult,
  BacnetRequestInput,
  BacnetResponsePayload,
  BacnetService,
} from '../bacnet-readonly-types.js';

import type {
  BacnetProductionAdapterConfig,
  BacnetProductionErrorCode,
  BacnetProductionNormalizedRecord,
  BacnetProductionPropertyRead,
  BacnetProductionReadService,
  BacnetProductionResolvedTarget,
} from './bacnet-production-adapter.types.js';
import {
  BACNET_PRODUCTION_DENIED_SERVICES,
  BACNET_PRODUCTION_DANGEROUS_KEYS,
  BACNET_PRODUCTION_FORMULA_PREFIXES,
  BACNET_PRODUCTION_READ_SERVICES,
} from './bacnet-production-adapter.types.js';
import {
  buildFoundationPolicyForProduction,
  createObjectPropertyReferenceHash,
  validateProductionResourceLimits,
} from './bacnet-production-target-policy.js';

export function validateProductionService(service: string): BacnetProductionErrorCode | null {
  const normalized = service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  if ((BACNET_PRODUCTION_DENIED_SERVICES as readonly string[]).includes(normalized)) {
    return 'BACNET_WRITE_SERVICE_REJECTED';
  }
  if (!BACNET_PRODUCTION_READ_SERVICES.includes(normalized as BacnetProductionReadService)) {
    return 'BACNET_SERVICE_NOT_ALLOWED';
  }
  return null;
}

export function validateProductionAdapterConfig(config: BacnetProductionAdapterConfig): BacnetProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_BACNET_IP_READONLY') return 'BACNET_CONFIG_INVALID';
  if (config.enabled !== true) return 'BACNET_ADAPTER_DISABLED';
  if (!config.targetReferenceId || !config.deviceInstanceReferenceId) return 'BACNET_CONFIG_INVALID';
  if (!config.objectReferenceId || !config.propertyReferenceId) return 'BACNET_CONFIG_INVALID';
  if (!(config.targetPort >= 1 && config.targetPort <= 65535)) return 'BACNET_PORT_NOT_ALLOWED';
  if (config.udpMode !== 'PRODUCTION_UDP' && config.udpMode !== 'LOOPBACK_TEST') return 'BACNET_CONFIG_INVALID';
  if (config.dnsMode !== 'DENY' && config.dnsMode !== 'INJECTED_TEST') return 'BACNET_CONFIG_INVALID';
  if (config.broadcastMode !== 'DENY' && config.broadcastMode !== 'TEST_DISCOVERY_ONLY') return 'BACNET_CONFIG_INVALID';
  if (config.segmentationMode !== 'DENY') return 'BACNET_CONFIG_INVALID';
  if (config.maxRetries !== 0) return 'BACNET_CONFIG_INVALID';
  const serviceError = validateProductionService(config.service);
  if (serviceError) return serviceError;
  if (!Array.isArray(config.reads) || config.reads.length === 0) return 'BACNET_CONFIG_INVALID';
  if (config.reads.length > config.maxProperties) return 'BACNET_PROPERTY_LIMIT_EXCEEDED';
  const objectTypes = new Set(config.reads.map((read) => String(read.objectType)));
  if (objectTypes.size > config.maxObjects) return 'BACNET_PROPERTY_LIMIT_EXCEEDED';
  if (!Number.isInteger(config.deviceInstance) || config.deviceInstance < 0) return 'BACNET_CONFIG_INVALID';
  return validateProductionResourceLimits(config);
}

export function mapFoundationRequestError(errors: readonly string[]): BacnetProductionErrorCode {
  if (errors.includes('BACNET_WRITE_SERVICE_PROHIBITED')) return 'BACNET_WRITE_SERVICE_REJECTED';
  if (errors.includes('BACNET_SERVICE_NOT_ALLOWED') || errors.includes('BACNET_DISCOVERY_DISABLED')) {
    return 'BACNET_SERVICE_NOT_ALLOWED';
  }
  if (errors.includes('BACNET_OBJECT_TYPE_NOT_ALLOWED') || errors.includes('BACNET_OBJECT_INSTANCE_NOT_ALLOWED')) {
    return 'BACNET_OBJECT_NOT_ALLOWLISTED';
  }
  if (errors.includes('BACNET_PROPERTY_NOT_ALLOWED') || errors.includes('BACNET_PROPERTY_INVALID')) {
    return 'BACNET_PROPERTY_NOT_ALLOWLISTED';
  }
  if (errors.includes('BACNET_REQUEST_LIMIT_EXCEEDED') || errors.includes('BACNET_APDU_LIMIT_EXCEEDED')) {
    return 'BACNET_PROPERTY_LIMIT_EXCEEDED';
  }
  return 'BACNET_FOUNDATION_VALIDATION_FAILED';
}

export function runFoundationRequestValidation(
  target: BacnetProductionResolvedTarget,
  config: BacnetProductionAdapterConfig,
  objectTypes: readonly BacnetObjectType[],
  properties: readonly BacnetPropertyId[],
  testMode: boolean,
): BacnetProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(target, config, objectTypes, properties, testMode);
  const reads: BacnetPropertyRead[] = config.reads.map((read) => ({
    objectType: read.objectType as BacnetPropertyRead['objectType'],
    objectInstance: read.objectInstance,
    propertyId: String(read.propertyIdentifier),
    arrayIndex: read.arrayIndex,
  }));

  const requestInput: BacnetRequestInput = {
    target: target.hostname,
    port: target.port,
    deviceInstance: config.deviceInstance,
    service: config.service,
    reads,
    broadcast: false,
  };

  const requestValidation = validateBacnetRequest(requestInput, policy);
  if (!requestValidation.ok) return mapFoundationRequestError(requestValidation.errors);

  if (testMode && config.udpMode === 'LOOPBACK_TEST') {
    return null;
  }

  const policyValidation = validateBacnetReadOnlyPolicy({
    ...policy,
    syntheticTransportOnly: false,
  } as unknown as BacnetIpReadOnlyPolicy);
  if (!policyValidation.ok) return 'BACNET_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function mapFoundationResponseError(errors: readonly string[]): BacnetProductionErrorCode {
  if (errors.includes('BACNET_INVOKE_ID_MISMATCH')) return 'BACNET_INVOKE_ID_MISMATCH';
  if (errors.includes('BACNET_SERVICE_MISMATCH')) return 'BACNET_SERVICE_MISMATCH';
  if (errors.includes('BACNET_ERROR_RESPONSE')) return 'BACNET_ERROR_RESPONSE';
  if (errors.includes('BACNET_REJECT_RESPONSE') || errors.includes('BACNET_ABORT_RESPONSE')) {
    return 'BACNET_ABORT_REJECT_RESPONSE';
  }
  if (errors.includes('BACNET_SEGMENTATION_NOT_ALLOWED')) return 'BACNET_SEGMENTATION_NOT_ALLOWED';
  if (errors.includes('BACNET_RESPONSE_TOO_LARGE')) return 'BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED';
  if (errors.includes('BACNET_APDU_LIMIT_EXCEEDED')) return 'BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED';
  if (errors.includes('BACNET_OBJECT_MISMATCH') || errors.includes('BACNET_PROPERTY_MISMATCH')) {
    return 'BACNET_PROPERTY_NOT_ALLOWLISTED';
  }
  if (errors.includes('BACNET_VALUE_TYPE_NOT_ALLOWED')) return 'BACNET_DECODE_FAILED';
  return 'BACNET_FOUNDATION_VALIDATION_FAILED';
}

export function validateFoundationResponse(
  request: {
    invokeId: number;
    service: string;
    deviceInstance: number;
    reads: readonly BacnetPropertyRead[];
  },
  response: BacnetResponsePayload,
  target: BacnetProductionResolvedTarget,
  config: BacnetProductionAdapterConfig,
  objectTypes: readonly BacnetObjectType[],
  properties: readonly BacnetPropertyId[],
  testMode: boolean,
): BacnetProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(target, config, objectTypes, properties, testMode);
  const responseForValidation =
    request.service === 'WHO_IS' && String(response.service).toUpperCase() === 'I_AM'
      ? { ...response, service: 'WHO_IS' }
      : response;
  const validation = validateBacnetResponse(request, responseForValidation, policy);
  if (!validation.ok) return mapFoundationResponseError(validation.errors);
  return null;
}

export function normalizePropertyResults(
  results: readonly BacnetPropertyResult[],
  config: BacnetProductionAdapterConfig,
  service: string,
): { ok: true; records: BacnetProductionNormalizedRecord[] } | { ok: false; errorCode: BacnetProductionErrorCode } {
  const records: BacnetProductionNormalizedRecord[] = [];
  for (let index = 0; index < results.length; index += 1) {
    const result = results[index];
    const valueText = result.value === null || result.value === undefined ? '' : String(result.value);
    if (valueText.length > 8192) return { ok: false, errorCode: 'BACNET_DECODE_FAILED' };
    const valueTypeUpper = String(result.valueType ?? '').toUpperCase();
    const formulaSensitive =
      valueTypeUpper === 'CHARACTER_STRING'
      || valueTypeUpper === 'OCTET_STRING'
      || valueTypeUpper === 'BIT_STRING'
      || valueTypeUpper === '';
    if (formulaSensitive) {
      for (const prefix of BACNET_PRODUCTION_FORMULA_PREFIXES) {
        if (valueText.trimStart().startsWith(prefix) && config.formulaPrefixPolicy === 'REJECT') {
          return { ok: false, errorCode: 'BACNET_DECODE_FAILED' };
        }
      }
    }
    const fields: Record<string, string> = {
      index: String(index),
      objectType: String(result.objectType),
      objectInstance: String(result.objectInstance),
      propertyIdentifier: String(result.propertyId),
      objectReference: createObjectPropertyReferenceHash(String(result.objectType), String(result.propertyId)),
      valueType: String(result.valueType ?? 'NULL'),
      value: valueText,
      service,
    };
    if (result.arrayIndex !== undefined) fields.arrayIndex = String(result.arrayIndex);
    for (const key of BACNET_PRODUCTION_DANGEROUS_KEYS) {
      if (Object.prototype.hasOwnProperty.call(fields, key)) {
        return { ok: false, errorCode: 'BACNET_DECODE_FAILED' };
      }
    }
    if (result.valueType) {
      const normalized = normalizeBacnetValue(String(result.valueType), result.value);
      if (!normalized.ok) return { ok: false, errorCode: 'BACNET_DECODE_FAILED' };
    }
    records.push({ fields });
  }
  return { ok: true, records };
}

export function decodeAndNormalizeResponse(
  response: BacnetResponsePayload,
  target: BacnetProductionResolvedTarget,
  config: BacnetProductionAdapterConfig,
  objectTypes: readonly BacnetObjectType[],
  properties: readonly BacnetPropertyId[],
  testMode: boolean,
  service: BacnetService | string,
): { ok: true; records: BacnetProductionNormalizedRecord[] } | { ok: false; errorCode: BacnetProductionErrorCode } {
  const reads: BacnetPropertyRead[] = config.reads.map((read: BacnetProductionPropertyRead) => ({
    objectType: read.objectType as BacnetPropertyRead['objectType'],
    objectInstance: read.objectInstance,
    propertyId: String(read.propertyIdentifier),
    arrayIndex: read.arrayIndex,
  }));

  const foundationError = validateFoundationResponse(
    {
      invokeId: response.invokeId,
      service,
      deviceInstance: config.deviceInstance,
      reads,
    },
    response,
    target,
    config,
    objectTypes,
    properties,
    testMode,
  );
  if (foundationError) return { ok: false, errorCode: foundationError };

  if ((response.results?.length ?? 0) === 0) return { ok: false, errorCode: 'BACNET_DECODE_FAILED' };
  return normalizePropertyResults(response.results ?? [], config, String(service));
}

export type { BacnetResponsePayload, BacnetPropertyResult, BacnetPropertyRead };
