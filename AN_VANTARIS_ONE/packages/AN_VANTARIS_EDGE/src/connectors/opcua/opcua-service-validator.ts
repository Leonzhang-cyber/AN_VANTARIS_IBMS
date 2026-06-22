import type { OpcUaReadOnlyPolicy, OpcUaService, ValidationResult } from './opcua-readonly-types.js';

const WRITE_SERVICES = new Set<OpcUaService>([
  'WRITE',
  'CALL',
  'ADD_NODES',
  'DELETE_NODES',
  'ADD_REFERENCES',
  'DELETE_REFERENCES',
  'HISTORY_UPDATE',
]);

const SUBSCRIPTION_SERVICES = new Set<OpcUaService>([
  'CREATE_SUBSCRIPTION',
  'CREATE_MONITORED_ITEMS',
  'MODIFY_MONITORED_ITEMS',
  'DELETE_MONITORED_ITEMS',
]);

function normalizeService(service: string): OpcUaService {
  return service.trim().toUpperCase().replace(/[\s-]+/g, '_') as OpcUaService;
}

export function validateOpcUaService(service: string, policy: OpcUaReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  const normalized = normalizeService(service);

  if (policy.deniedServices.includes(normalized)) {
    if (WRITE_SERVICES.has(normalized)) errors.push('OPCUA_WRITE_SERVICE_PROHIBITED');
    else if (SUBSCRIPTION_SERVICES.has(normalized)) errors.push('OPCUA_SUBSCRIPTION_DISABLED');
    else errors.push('OPCUA_SERVICE_NOT_ALLOWED');
  }

  if (normalized === 'HISTORY_READ' && !policy.historyReadAllowed) {
    errors.push('OPCUA_HISTORY_READ_DISABLED');
  }

  if (!policy.allowedServices.includes(normalized)) {
    if (errors.length === 0) errors.push('OPCUA_SERVICE_NOT_ALLOWED');
  }

  if (policy.writeOperationsAllowed && WRITE_SERVICES.has(normalized)) {
    errors.push('OPCUA_WRITE_SERVICE_PROHIBITED');
  }

  if (!policy.subscriptionsAllowed && SUBSCRIPTION_SERVICES.has(normalized)) {
    errors.push('OPCUA_SUBSCRIPTION_DISABLED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}

export { normalizeService as normalizeOpcUaService };
