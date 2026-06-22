import type { ModbusTcpReadOnlyPolicy, ValidationResult } from './modbus-readonly-types.js';

const READ_FUNCTION_CODES = new Set([1, 2, 3, 4]);

export function validateModbusReadOnlyPolicy(policy: ModbusTcpReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-04') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_MODBUS_TCP_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (!policy.allowedTransports.includes('MODBUS_TCP')) errors.push('allowedTransports must include MODBUS_TCP');
  if (!policy.allowedFunctionCodes.every((fc) => READ_FUNCTION_CODES.has(fc))) errors.push('allowedFunctionCodes must be read-only');
  if (!policy.deniedFunctionCodes.includes(16)) errors.push('deniedFunctionCodes must include write codes');
  if (!Array.isArray(policy.allowedTargets) || policy.allowedTargets.length === 0) errors.push('allowedTargets required');
  if (!Array.isArray(policy.allowedPorts) || !policy.allowedPorts.includes(502)) errors.push('allowedPorts must include 502');
  if (!Array.isArray(policy.allowedUnitIds) || policy.allowedUnitIds.length === 0) errors.push('allowedUnitIds required');
  if (!Array.isArray(policy.allowedAddressRanges) || policy.allowedAddressRanges.length === 0) {
    errors.push('allowedAddressRanges required');
  }
  if (policy.writeOperationsAllowed) errors.push('writeOperationsAllowed must be false');
  if (!(policy.maxRegistersPerRequest > 0)) errors.push('maxRegistersPerRequest must be positive');
  if (!(policy.maxCoilsPerRequest > 0)) errors.push('maxCoilsPerRequest must be positive');
  if (!(policy.maxResponseBytes > 0)) errors.push('maxResponseBytes must be positive');
  if (!(policy.timeoutMs > 0)) errors.push('timeoutMs must be positive');
  if (policy.networkAccessAllowed) errors.push('networkAccessAllowed must be false');
  if (!policy.syntheticTransportOnly) errors.push('syntheticTransportOnly must be true');
  if (policy.dnsResolutionMode !== 'MODELED_ONLY') errors.push('dnsResolutionMode must be MODELED_ONLY');
  return { ok: errors.length === 0, errors };
}
