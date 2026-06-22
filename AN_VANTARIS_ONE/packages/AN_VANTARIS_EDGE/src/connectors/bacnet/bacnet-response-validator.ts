import type {
  BacnetIpReadOnlyPolicy,
  BacnetPropertyRead,
  BacnetResponsePayload,
  BacnetResponseValidation,
  BacnetValueType,
} from './bacnet-readonly-types.js';
import { normalizeBacnetPropertyId } from './bacnet-property-validator.js';
import { normalizeBacnetObjectType } from './bacnet-object-validator.js';

function estimateResponseBytes(response: BacnetResponsePayload): number {
  if (typeof response.responseBytes === 'number') return response.responseBytes;
  if (typeof response.apduBytes === 'number') return response.apduBytes;
  const results = response.results ?? [];
  return results.reduce((sum, entry) => sum + JSON.stringify(entry.value ?? '').length + 64, 64);
}

export function normalizeBacnetValue(
  valueType: string,
  value: unknown,
): { ok: boolean; valueType: BacnetValueType | string; value?: unknown; errors: string[] } {
  const normalizedType = valueType.trim().toUpperCase().replace(/[\s-]+/g, '_') as BacnetValueType;
  const errors: string[] = [];

  switch (normalizedType) {
    case 'NULL':
      return { ok: value === null || value === undefined, valueType: normalizedType, value: null, errors: value === null || value === undefined ? [] : ['BACNET_RESPONSE_MALFORMED'] };
    case 'BOOLEAN':
      return { ok: typeof value === 'boolean', valueType: normalizedType, value, errors: typeof value === 'boolean' ? [] : ['BACNET_RESPONSE_MALFORMED'] };
    case 'UNSIGNED':
    case 'SIGNED':
    case 'REAL':
    case 'DOUBLE':
    case 'ENUMERATED':
      return { ok: typeof value === 'number' && Number.isFinite(value), valueType: normalizedType, value, errors: typeof value === 'number' && Number.isFinite(value) ? [] : ['BACNET_RESPONSE_MALFORMED'] };
    case 'CHARACTER_STRING':
    case 'OCTET_STRING':
    case 'BIT_STRING':
      return { ok: typeof value === 'string', valueType: normalizedType, value, errors: typeof value === 'string' ? [] : ['BACNET_RESPONSE_MALFORMED'] };
    case 'DATE':
    case 'TIME':
      return { ok: typeof value === 'object' && value !== null && !Array.isArray(value), valueType: normalizedType, value, errors: typeof value === 'object' && value !== null && !Array.isArray(value) ? [] : ['BACNET_RESPONSE_MALFORMED'] };
    case 'OBJECT_IDENTIFIER':
      return {
        ok: typeof value === 'object' && value !== null && 'objectType' in (value as object) && 'objectInstance' in (value as object),
        valueType: normalizedType,
        value,
        errors:
          typeof value === 'object' && value !== null && 'objectType' in (value as object) && 'objectInstance' in (value as object)
            ? []
            : ['BACNET_RESPONSE_MALFORMED'],
      };
    default:
      return { ok: false, valueType: normalizedType, errors: ['BACNET_VALUE_TYPE_NOT_ALLOWED'] };
  }
}

export function validateBacnetResponse(
  request: {
    readonly invokeId: number;
    readonly service: string;
    readonly deviceInstance: number;
    readonly reads: readonly BacnetPropertyRead[];
  },
  response: BacnetResponsePayload,
  policy: BacnetIpReadOnlyPolicy,
): BacnetResponseValidation {
  const errors: string[] = [];

  if (response.segmented && !policy.segmentationAllowed) {
    errors.push('BACNET_SEGMENTATION_NOT_ALLOWED');
  }

  if (response.invokeId !== request.invokeId) {
    errors.push('BACNET_INVOKE_ID_MISMATCH');
  }

  const normalizedService = request.service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  const responseService = String(response.service).trim().toUpperCase().replace(/[\s-]+/g, '_');
  if (responseService !== normalizedService) {
    errors.push('BACNET_SERVICE_MISMATCH');
  }

  if (response.deviceInstance !== request.deviceInstance) {
    errors.push('BACNET_DEVICE_MISMATCH');
  }

  if (response.errorClass === 'ERROR') {
    errors.push('BACNET_ERROR_RESPONSE');
    return { ok: false, response, errors: [...new Set(errors)] };
  }
  if (response.errorClass === 'REJECT') {
    errors.push('BACNET_REJECT_RESPONSE');
    return { ok: false, response, errors: [...new Set(errors)] };
  }
  if (response.errorClass === 'ABORT') {
    errors.push('BACNET_ABORT_RESPONSE');
    return { ok: false, response, errors: [...new Set(errors)] };
  }

  const responseBytes = estimateResponseBytes(response);
  if (responseBytes > policy.maxResponseBytes) {
    errors.push('BACNET_RESPONSE_TOO_LARGE');
  }
  const apduBytes = response.apduBytes ?? responseBytes;
  if (apduBytes > policy.maxApduBytes) {
    errors.push('BACNET_APDU_LIMIT_EXCEEDED');
  }

  const seen = new Set<string>();
  for (const [index, expected] of request.reads.entries()) {
    const actual = response.results?.[index];
    if (!actual) {
      errors.push('BACNET_RESPONSE_MALFORMED');
      continue;
    }
    const key = `${actual.objectType}:${actual.objectInstance}:${actual.propertyId}:${actual.arrayIndex ?? 'all'}`;
    if (seen.has(key)) errors.push('BACNET_RESPONSE_MALFORMED');
    seen.add(key);

    if (normalizeBacnetObjectType(actual.objectType) !== normalizeBacnetObjectType(expected.objectType)) {
      errors.push('BACNET_OBJECT_MISMATCH');
    }
    if (Number(actual.objectInstance) !== Number(expected.objectInstance)) {
      errors.push('BACNET_OBJECT_MISMATCH');
    }
    if (normalizeBacnetPropertyId(actual.propertyId) !== normalizeBacnetPropertyId(expected.propertyId)) {
      errors.push('BACNET_PROPERTY_MISMATCH');
    }
    if (expected.arrayIndex !== undefined) {
      if (actual.arrayIndex !== Number(expected.arrayIndex)) {
        errors.push('BACNET_PROPERTY_MISMATCH');
      }
    }

    if (actual.valueType) {
      const normalized = normalizeBacnetValue(String(actual.valueType), actual.value);
      if (!normalized.ok) errors.push(...normalized.errors);
      else if (!policy.allowedValueTypes.includes(normalized.valueType as BacnetValueType)) {
        errors.push('BACNET_VALUE_TYPE_NOT_ALLOWED');
      }
    }
  }

  if ((response.results?.length ?? 0) !== request.reads.length) {
    errors.push('BACNET_RESPONSE_MALFORMED');
  }

  return { ok: errors.length === 0, response, errors: [...new Set(errors)] };
}
