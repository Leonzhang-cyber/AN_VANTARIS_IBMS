import type {
  BacnetIpReadOnlyPolicy,
  BacnetObjectIdentifier,
  BacnetObjectType,
  ValidationResult,
} from './bacnet-readonly-types.js';

export const BACNET_WILDCARD_INSTANCE = 4194303;

const KNOWN_OBJECT_TYPES = new Set<BacnetObjectType>([
  'DEVICE',
  'ANALOG_INPUT',
  'ANALOG_OUTPUT',
  'ANALOG_VALUE',
  'BINARY_INPUT',
  'BINARY_OUTPUT',
  'BINARY_VALUE',
  'MULTI_STATE_INPUT',
  'MULTI_STATE_OUTPUT',
  'MULTI_STATE_VALUE',
]);

function parseInteger(value: number | string): number | null {
  const num = typeof value === 'string' ? Number(value.trim()) : value;
  if (!Number.isInteger(num)) return null;
  return num;
}

export function normalizeBacnetObjectType(objectType: string): BacnetObjectType | null {
  const normalized = objectType.trim().toUpperCase().replace(/[\s-]+/g, '_') as BacnetObjectType;
  return KNOWN_OBJECT_TYPES.has(normalized) ? normalized : null;
}

export function validateBacnetDeviceInstance(
  deviceInstance: number | string,
  policy: BacnetIpReadOnlyPolicy,
): ValidationResult & { deviceInstance?: number } {
  const num = parseInteger(deviceInstance);
  if (num === null || num < 0 || num > 4194302 || num === BACNET_WILDCARD_INSTANCE) {
    return { ok: false, errors: ['BACNET_DEVICE_INSTANCE_INVALID'] };
  }
  if (!policy.allowedDeviceInstances.includes(num)) {
    return { ok: false, deviceInstance: num, errors: ['BACNET_DEVICE_INSTANCE_NOT_ALLOWED'] };
  }
  return { ok: true, deviceInstance: num, errors: [] };
}

export function validateBacnetObjectIdentifier(
  objectType: string,
  objectInstance: number | string,
  policy: BacnetIpReadOnlyPolicy,
): ValidationResult & BacnetObjectIdentifier {
  const normalizedType = normalizeBacnetObjectType(objectType);
  const errors: string[] = [];
  if (!normalizedType) {
    return { ok: false, objectType: 'DEVICE', objectInstance: 0, errors: ['BACNET_OBJECT_TYPE_NOT_ALLOWED'] };
  }
  if (!policy.allowedObjectTypes.includes(normalizedType)) {
    errors.push('BACNET_OBJECT_TYPE_NOT_ALLOWED');
  }

  const instance = parseInteger(objectInstance);
  if (instance === null || instance < 0 || instance > 4194302 || instance === BACNET_WILDCARD_INSTANCE) {
    errors.push('BACNET_OBJECT_INSTANCE_INVALID');
  } else {
    const range = policy.allowedObjectInstanceRanges.find((r) => r.objectType === normalizedType);
    if (!range || instance < range.start || instance > range.end) {
      errors.push('BACNET_OBJECT_INSTANCE_NOT_ALLOWED');
    }
  }

  return {
    ok: errors.length === 0,
    objectType: normalizedType,
    objectInstance: instance ?? 0,
    errors: [...new Set(errors)],
  };
}
