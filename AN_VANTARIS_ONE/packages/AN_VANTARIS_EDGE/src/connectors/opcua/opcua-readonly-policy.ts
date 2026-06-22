import type { OpcUaReadOnlyPolicy, ValidationResult } from './opcua-readonly-types.js';

const READ_SERVICES = new Set(['BROWSE', 'BROWSE_NEXT', 'READ', 'TRANSLATE_BROWSE_PATHS_TO_NODE_IDS']);

export function validateOpcUaReadOnlyPolicy(policy: OpcUaReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-06') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_OPC_UA_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (!policy.allowedTransports.includes('OPC_TCP')) errors.push('allowedTransports must include OPC_TCP');
  if (!policy.allowedServices.every((s) => READ_SERVICES.has(s))) errors.push('allowedServices must be read-only');
  if (!policy.deniedServices.includes('WRITE')) errors.push('deniedServices must include WRITE');
  if (policy.anonymousAllowed) errors.push('anonymousAllowed must be false');
  if (policy.subscriptionsAllowed) errors.push('subscriptionsAllowed must be false');
  if (policy.monitoredItemsAllowed) errors.push('monitoredItemsAllowed must be false');
  if (policy.historyReadAllowed) errors.push('historyReadAllowed must be false');
  if (policy.writeOperationsAllowed) errors.push('writeOperationsAllowed must be false');
  if (policy.networkAccessAllowed) errors.push('networkAccessAllowed must be false');
  if (!policy.syntheticTransportOnly) errors.push('syntheticTransportOnly must be true');
  if (policy.endpointDiscoveryMode !== 'MODELED_ONLY') errors.push('endpointDiscoveryMode must be MODELED_ONLY');
  if (policy.dnsResolutionMode !== 'MODELED_ONLY') errors.push('dnsResolutionMode must be MODELED_ONLY');
  if (!policy.allowedSecurityPolicies.includes('Basic256Sha256')) errors.push('secure policies required');
  if (policy.allowedMessageSecurityModes.includes('NONE')) errors.push('NONE security mode must not be allowed');
  return { ok: errors.length === 0, errors };
}
