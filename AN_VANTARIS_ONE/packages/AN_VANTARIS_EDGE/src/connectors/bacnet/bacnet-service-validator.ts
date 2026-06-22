import type { BacnetIpReadOnlyPolicy, BacnetService, ValidationResult } from './bacnet-readonly-types.js';

const WRITE_SERVICES = new Set<BacnetService>([
  'WRITE_PROPERTY',
  'WRITE_PROPERTY_MULTIPLE',
  'ATOMIC_WRITE_FILE',
  'ADD_LIST_ELEMENT',
  'REMOVE_LIST_ELEMENT',
  'CREATE_OBJECT',
  'DELETE_OBJECT',
]);

const DISCOVERY_SERVICES = new Set<BacnetService>(['WHO_IS', 'I_AM']);

export function normalizeBacnetService(service: string): BacnetService | null {
  const normalized = service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  return normalized as BacnetService;
}

export function validateBacnetService(
  service: string,
  policy: BacnetIpReadOnlyPolicy,
): ValidationResult & { service?: BacnetService } {
  const normalized = normalizeBacnetService(service);
  if (!normalized) {
    return { ok: false, errors: ['BACNET_SERVICE_NOT_ALLOWED'] };
  }

  if (DISCOVERY_SERVICES.has(normalized)) {
    return { ok: false, service: normalized, errors: ['BACNET_DISCOVERY_DISABLED'] };
  }

  if (WRITE_SERVICES.has(normalized) || policy.deniedServices.includes(normalized)) {
    return { ok: false, service: normalized, errors: ['BACNET_WRITE_SERVICE_PROHIBITED'] };
  }

  if (normalized === 'SUBSCRIBE_COV' || normalized === 'SUBSCRIBE_COV_PROPERTY') {
    if (!policy.covSubscriptionAllowed) {
      return { ok: false, service: normalized, errors: ['BACNET_SERVICE_NOT_ALLOWED'] };
    }
  }

  if (!policy.allowedServices.includes(normalized)) {
    return { ok: false, service: normalized, errors: ['BACNET_SERVICE_NOT_ALLOWED'] };
  }

  return { ok: true, service: normalized, errors: [] };
}
