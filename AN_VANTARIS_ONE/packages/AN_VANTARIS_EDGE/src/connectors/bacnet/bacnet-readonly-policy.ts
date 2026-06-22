import type { BacnetIpReadOnlyPolicy, ValidationResult } from './bacnet-readonly-types.js';

const READ_SERVICES = new Set(['READ_PROPERTY', 'READ_PROPERTY_MULTIPLE']);

export function validateBacnetReadOnlyPolicy(policy: BacnetIpReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-05') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_BACNET_IP_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (!policy.allowedTransports.includes('BACNET_IP')) errors.push('allowedTransports must include BACNET_IP');
  if (!policy.allowedServices.every((s) => READ_SERVICES.has(s))) errors.push('allowedServices must be read-only');
  if (!policy.deniedServices.includes('WRITE_PROPERTY')) errors.push('deniedServices must include write services');
  if (!Array.isArray(policy.allowedTargets) || policy.allowedTargets.length === 0) errors.push('allowedTargets required');
  if (!Array.isArray(policy.allowedPorts) || !policy.allowedPorts.includes(47808)) errors.push('allowedPorts must include 47808');
  if (!Array.isArray(policy.allowedDeviceInstances) || policy.allowedDeviceInstances.length === 0) {
    errors.push('allowedDeviceInstances required');
  }
  if (policy.broadcastAllowed) errors.push('broadcastAllowed must be false');
  if (policy.bbmdAllowed) errors.push('bbmdAllowed must be false');
  if (policy.foreignDeviceRegistrationAllowed) errors.push('foreignDeviceRegistrationAllowed must be false');
  if (policy.covSubscriptionAllowed) errors.push('covSubscriptionAllowed must be false');
  if (policy.segmentationAllowed) errors.push('segmentationAllowed must be false');
  if (policy.writeOperationsAllowed) errors.push('writeOperationsAllowed must be false');
  if (policy.networkAccessAllowed) errors.push('networkAccessAllowed must be false');
  if (!policy.syntheticTransportOnly) errors.push('syntheticTransportOnly must be true');
  if (policy.discoveryMode !== 'MODELED_ONLY') errors.push('discoveryMode must be MODELED_ONLY');
  if (policy.dnsResolutionMode !== 'MODELED_ONLY') errors.push('dnsResolutionMode must be MODELED_ONLY');
  return { ok: errors.length === 0, errors };
}
