import type {
  OpcUaReadOnlyPolicy,
  OpcUaReadResult,
  OpcUaReadTarget,
  OpcUaResponsePayload,
  OpcUaVariantType,
  ValidationResult,
} from './opcua-readonly-types.js';
import { normalizeOpcUaNodeId, validateOpcUaNodeId } from './opcua-nodeid-validator.js';

function estimateResponseBytes(response: OpcUaResponsePayload): number {
  if (typeof response.responseBytes === 'number') return response.responseBytes;
  return JSON.stringify(response.results ?? []).length + 128;
}

function classifyStatusCode(statusCode: string): 'GOOD' | 'BAD' | 'UNCERTAIN' | 'UNKNOWN' {
  const normalized = statusCode.trim();
  if (/^good$/i.test(normalized) || normalized === '0x00000000') return 'GOOD';
  if (/^bad/i.test(normalized) || /^0x8/i.test(normalized)) return 'BAD';
  if (/^uncertain/i.test(normalized) || /^0x4/i.test(normalized)) return 'UNCERTAIN';
  return 'UNKNOWN';
}

function isValidIsoTimestamp(value: string): boolean {
  return !Number.isNaN(Date.parse(value));
}

export function normalizeOpcUaVariant(
  valueType: string,
  value: unknown,
  policy: OpcUaReadOnlyPolicy,
): { ok: boolean; valueType: OpcUaVariantType | string; value?: unknown; errors: string[] } {
  const normalizedType = valueType.trim().toUpperCase().replace(/[\s-]+/g, '_') as OpcUaVariantType;
  const errors: string[] = [];

  if (!policy.allowedVariantTypes.includes(normalizedType)) {
    return { ok: false, valueType: normalizedType, errors: ['OPCUA_VARIANT_TYPE_NOT_ALLOWED'] };
  }

  switch (normalizedType) {
    case 'NULL':
      return { ok: value === null || value === undefined, valueType: normalizedType, value: null, errors: value === null || value === undefined ? [] : ['OPCUA_RESPONSE_MALFORMED'] };
    case 'BOOLEAN':
      return { ok: typeof value === 'boolean', valueType: normalizedType, value, errors: typeof value === 'boolean' ? [] : ['OPCUA_RESPONSE_MALFORMED'] };
    case 'SBYTE':
      if (typeof value !== 'number' || !Number.isInteger(value) || value < -128 || value > 127) {
        errors.push('OPCUA_RESPONSE_MALFORMED');
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'BYTE':
    case 'UINT16':
      if (typeof value !== 'number' || !Number.isInteger(value) || value < 0 || value > 65535) {
        errors.push('OPCUA_RESPONSE_MALFORMED');
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'INT16':
      if (typeof value !== 'number' || !Number.isInteger(value) || value < -32768 || value > 32767) {
        errors.push('OPCUA_RESPONSE_MALFORMED');
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'INT32':
      if (typeof value !== 'number' || !Number.isInteger(value) || value < -2147483648 || value > 2147483647) {
        errors.push('OPCUA_RESPONSE_MALFORMED');
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'UINT32':
      if (typeof value !== 'number' || !Number.isInteger(value) || value < 0 || value > 4294967295) {
        errors.push('OPCUA_RESPONSE_MALFORMED');
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'INT64':
    case 'UINT64':
      if (typeof value !== 'number' || !Number.isInteger(value)) errors.push('OPCUA_RESPONSE_MALFORMED');
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'FLOAT':
    case 'DOUBLE':
      if (typeof value !== 'number' || !Number.isFinite(value)) errors.push('OPCUA_RESPONSE_MALFORMED');
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'STRING':
      if (typeof value !== 'string') errors.push('OPCUA_RESPONSE_MALFORMED');
      else if (value.length > policy.maxStringLength) errors.push('OPCUA_STRING_LIMIT_EXCEEDED');
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'DATETIME':
      if (typeof value !== 'string' || !isValidIsoTimestamp(value)) errors.push('OPCUA_TIMESTAMP_INVALID');
      return { ok: errors.length === 0, valueType: normalizedType, value, errors };
    case 'NODE_ID':
      if (typeof value !== 'string') errors.push('OPCUA_RESPONSE_MALFORMED');
      else {
        const nodeResult = validateOpcUaNodeId(value, policy);
        if (!nodeResult.ok) errors.push(...nodeResult.errors);
      }
      return { ok: errors.length === 0, valueType: normalizedType, value, errors: [...new Set(errors)] };
    case 'GUID':
    case 'BYTESTRING':
      return { ok: typeof value === 'string' && value.length > 0, valueType: normalizedType, value, errors: typeof value === 'string' && value.length > 0 ? [] : ['OPCUA_RESPONSE_MALFORMED'] };
    default:
      return { ok: false, valueType: normalizedType, errors: ['OPCUA_VARIANT_TYPE_NOT_ALLOWED'] };
  }
}

function validateVariantValue(
  valueType: string | undefined,
  value: unknown,
  policy: OpcUaReadOnlyPolicy,
): string[] {
  if (!valueType) return [];
  if (Array.isArray(value)) {
    if (value.length > policy.maxArrayLength) return ['OPCUA_ARRAY_LIMIT_EXCEEDED'];
    const errors: string[] = [];
    for (const item of value) {
      const normalized = normalizeOpcUaVariant(valueType, item, policy);
      if (!normalized.ok) errors.push(...normalized.errors);
    }
    return [...new Set(errors)];
  }
  const normalized = normalizeOpcUaVariant(valueType, value, policy);
  return normalized.ok ? [] : normalized.errors;
}

export function validateOpcUaResponse(
  request: {
    readonly requestHandle: number;
    readonly service: string;
    readonly reads?: readonly OpcUaReadTarget[];
  },
  response: OpcUaResponsePayload,
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];

  if (response.malformed) {
    return { ok: false, errors: ['OPCUA_RESPONSE_MALFORMED'] };
  }

  if (Number(response.requestHandle) !== Number(request.requestHandle)) {
    errors.push('OPCUA_REQUEST_HANDLE_MISMATCH');
  }

  const requestService = request.service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  const responseService = String(response.service).trim().toUpperCase().replace(/[\s-]+/g, '_');
  if (responseService !== requestService) {
    errors.push('OPCUA_SERVICE_MISMATCH');
  }

  const responseBytes = estimateResponseBytes(response);
  if (responseBytes > policy.maxResponseBytes) {
    errors.push('OPCUA_RESPONSE_TOO_LARGE');
  }

  const reads = request.reads ?? [];
  const results = response.results ?? [];

  if (results.length !== reads.length) {
    errors.push('OPCUA_RESPONSE_MALFORMED');
  }

  const seen = new Set<string>();
  for (const [index, expected] of reads.entries()) {
    const actual = results[index];
    if (!actual) {
      errors.push('OPCUA_RESPONSE_MALFORMED');
      continue;
    }

    const key = `${actual.nodeId}:${actual.attributeId}`;
    if (seen.has(key)) errors.push('OPCUA_RESPONSE_MALFORMED');
    seen.add(key);

    const expectedNode = normalizeOpcUaNodeId(expected.nodeId);
    const actualNode = normalizeOpcUaNodeId(actual.nodeId);
    if (!expectedNode || !actualNode || expectedNode.canonical !== actualNode.canonical) {
      errors.push('OPCUA_NODE_RESULT_MISMATCH');
    }

    if (expected.attributeId.trim().toUpperCase() !== actual.attributeId.trim().toUpperCase()) {
      errors.push('OPCUA_NODE_RESULT_MISMATCH');
    }

    const statusClass = classifyStatusCode(actual.statusCode);
    if (statusClass === 'BAD') errors.push('OPCUA_STATUS_CODE_BAD');
    if (statusClass === 'UNCERTAIN' && policy.rejectUncertainStatusCodes) {
      errors.push('OPCUA_STATUS_CODE_UNCERTAIN');
    }
    if (statusClass === 'UNKNOWN') errors.push('OPCUA_RESPONSE_MALFORMED');

    if (statusClass === 'GOOD' && actual.valueType) {
      errors.push(...validateVariantValue(actual.valueType, actual.value, policy));
    }

    if (actual.sourceTimestamp && !isValidIsoTimestamp(actual.sourceTimestamp)) {
      errors.push('OPCUA_TIMESTAMP_INVALID');
    }
    if (actual.serverTimestamp && !isValidIsoTimestamp(actual.serverTimestamp)) {
      errors.push('OPCUA_TIMESTAMP_INVALID');
    }
  }

  if (results.length > reads.length) {
    errors.push('OPCUA_RESPONSE_MALFORMED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}

export function validateOpcUaResponseStandalone(
  response: OpcUaResponsePayload,
  policy: OpcUaReadOnlyPolicy,
  reads: readonly OpcUaReadTarget[],
): ValidationResult {
  return validateOpcUaResponse(
    {
      requestHandle: response.requestHandle,
      service: response.service,
      reads,
    },
    response,
    policy,
  );
}
