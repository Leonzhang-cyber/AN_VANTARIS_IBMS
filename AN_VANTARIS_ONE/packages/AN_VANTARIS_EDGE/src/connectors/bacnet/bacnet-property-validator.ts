import type {
  BacnetIpReadOnlyPolicy,
  BacnetPropertyId,
  BacnetRequestInput,
  BacnetRequestValidation,
  ValidationResult,
} from './bacnet-readonly-types.js';
import { validateBacnetDeviceInstance, validateBacnetObjectIdentifier } from './bacnet-object-validator.js';
import { validateBacnetService } from './bacnet-service-validator.js';

function parseInteger(value: number | string | undefined): number | null {
  if (value === undefined) return null;
  const num = typeof value === 'string' ? Number(value.trim()) : value;
  if (!Number.isInteger(num)) return null;
  return num;
}

export function normalizeBacnetPropertyId(propertyId: string): string {
  return propertyId.trim().toUpperCase().replace(/[\s-]+/g, '_');
}

export function validateBacnetProperty(
  propertyId: string,
  policy: BacnetIpReadOnlyPolicy,
): ValidationResult & { propertyId?: string } {
  const normalized = normalizeBacnetPropertyId(propertyId);
  if (!normalized) {
    return { ok: false, errors: ['BACNET_PROPERTY_INVALID'] };
  }
  if (policy.deniedProperties.includes(normalized as BacnetPropertyId)) {
    return { ok: false, propertyId: normalized, errors: ['BACNET_PROPERTY_NOT_ALLOWED'] };
  }
  if (!policy.allowedProperties.includes(normalized as BacnetPropertyId)) {
    return { ok: false, propertyId: normalized, errors: ['BACNET_PROPERTY_NOT_ALLOWED'] };
  }
  return { ok: true, propertyId: normalized, errors: [] };
}

export function validateBacnetArrayIndex(
  arrayIndex: number | string | undefined,
  policy: BacnetIpReadOnlyPolicy,
): ValidationResult & { arrayIndex?: number } {
  if (arrayIndex === undefined) {
    return { ok: true, errors: [] };
  }
  const num = parseInteger(arrayIndex);
  if (num === null || num < 0) {
    return { ok: false, errors: ['BACNET_ARRAY_INDEX_INVALID'] };
  }
  if (num > policy.maxArrayIndex) {
    return { ok: false, arrayIndex: num, errors: ['BACNET_ARRAY_LIMIT_EXCEEDED'] };
  }
  return { ok: true, arrayIndex: num, errors: [] };
}

function estimateRequestBytes(readCount: number): number {
  return readCount * 32;
}

export function validateBacnetRequest(
  input: BacnetRequestInput,
  policy: BacnetIpReadOnlyPolicy,
): BacnetRequestValidation {
  const errors: string[] = [];

  const serviceResult = validateBacnetService(input.service, policy);
  if (!serviceResult.ok || !serviceResult.service) errors.push(...serviceResult.errors);

  const deviceResult = validateBacnetDeviceInstance(input.deviceInstance, policy);
  if (!deviceResult.ok) errors.push(...deviceResult.errors);

  const invokeId = parseInteger(input.invokeId ?? 1);
  if (invokeId === null || invokeId < 0 || invokeId > policy.maxInvokeId) {
    errors.push('BACNET_REQUEST_MALFORMED');
  }

  if (!Array.isArray(input.reads) || input.reads.length === 0) {
    errors.push('BACNET_REQUEST_MALFORMED');
  }

  const objectKeys = new Set<string>();
  const propertyKeys = new Set<string>();
  let propertyCount = 0;

  for (const read of input.reads ?? []) {
    const objectResult = validateBacnetObjectIdentifier(read.objectType, read.objectInstance, policy);
    if (!objectResult.ok) errors.push(...objectResult.errors);

    const propertyResult = validateBacnetProperty(read.propertyId, policy);
    if (!propertyResult.ok) errors.push(...propertyResult.errors);

    const arrayResult = validateBacnetArrayIndex(read.arrayIndex, policy);
    if (!arrayResult.ok) errors.push(...arrayResult.errors);

    const objectKey = `${objectResult.objectType}:${objectResult.objectInstance}`;
    const propertyKey = `${objectKey}:${propertyResult.propertyId ?? read.propertyId}:${arrayResult.arrayIndex ?? 'all'}`;
    if (propertyKeys.has(propertyKey)) errors.push('BACNET_REQUEST_MALFORMED');
    objectKeys.add(objectKey);
    propertyKeys.add(propertyKey);
    propertyCount += 1;
  }

  if (objectKeys.size > policy.maxObjectsPerRequest) {
    errors.push('BACNET_REQUEST_LIMIT_EXCEEDED');
  }
  if (propertyCount > policy.maxPropertiesPerRequest) {
    errors.push('BACNET_REQUEST_LIMIT_EXCEEDED');
  }

  const estimatedBytes = estimateRequestBytes(propertyCount);
  if (estimatedBytes > policy.maxApduBytes) {
    errors.push('BACNET_APDU_LIMIT_EXCEEDED');
  }

  if (policy.segmentationAllowed === false) {
    // modeled gate only; synthetic transport does not segment
  }

  return {
    ok: errors.length === 0,
    service: serviceResult.service,
    deviceInstance: deviceResult.deviceInstance,
    invokeId: invokeId ?? undefined,
    errors: [...new Set(errors)],
  };
}
