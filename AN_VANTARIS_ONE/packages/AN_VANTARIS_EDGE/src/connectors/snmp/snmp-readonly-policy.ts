import type { SnmpReadOnlyPolicy, ValidationResult } from './snmp-readonly-types.js';

const READ_OPERATIONS = new Set(['GET', 'GETNEXT', 'GETBULK']);
const WRITE_OPERATIONS = new Set(['SET', 'INFORM', 'TRAP_SEND']);

export function normalizeSnmpVersionToken(version: string): string {
  const v = version.trim().toLowerCase();
  if (v === 'v1' || v === '1') return '1';
  if (v === 'v2c' || v === '2c') return '2c';
  if (v === 'v3' || v === '3') return '3';
  return v;
}

export function validateSnmpReadOnlyPolicy(policy: SnmpReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-03') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_SNMP_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (policy.preferredVersion !== '3') errors.push('preferredVersion must be 3');
  if (!policy.allowedVersions.includes('3')) errors.push('allowedVersions must include 3');
  if (!policy.productionAllowedVersions.every((v) => v === '3')) errors.push('productionAllowedVersions must be v3 only');
  if (!Array.isArray(policy.deniedOperations) || !policy.deniedOperations.includes('SET')) errors.push('deniedOperations must include SET');
  if (!policy.allowedOperations.every((op) => READ_OPERATIONS.has(op))) errors.push('allowedOperations must be read-only');
  if (!Array.isArray(policy.allowedTargets) || policy.allowedTargets.length === 0) errors.push('allowedTargets required');
  if (!Array.isArray(policy.allowedOidPrefixes) || policy.allowedOidPrefixes.length === 0) errors.push('allowedOidPrefixes required');
  if (policy.writeOperationsAllowed) errors.push('writeOperationsAllowed must be false');
  if (!(policy.maxVarbinds > 0)) errors.push('maxVarbinds must be positive');
  if (!(policy.maxResponseBytes > 0)) errors.push('maxResponseBytes must be positive');
  if (!(policy.maxWalkDepth > 0)) errors.push('maxWalkDepth must be positive');
  if (!(policy.maxWalkRows > 0)) errors.push('maxWalkRows must be positive');
  if (!(policy.timeoutMs > 0)) errors.push('timeoutMs must be positive');
  if (policy.credentialMode !== 'REFERENCE_ONLY') errors.push('credentialMode must be REFERENCE_ONLY');
  if (policy.plaintextCommunityAllowed) errors.push('plaintextCommunityAllowed must be false');
  if (policy.plaintextAuthSecretAllowed) errors.push('plaintextAuthSecretAllowed must be false');
  if (policy.plaintextPrivacySecretAllowed) errors.push('plaintextPrivacySecretAllowed must be false');
  if (policy.networkAccessAllowed) errors.push('networkAccessAllowed must be false');
  if (!policy.syntheticTransportOnly) errors.push('syntheticTransportOnly must be true');
  if (policy.dnsResolutionMode !== 'MODELED_ONLY') errors.push('dnsResolutionMode must be MODELED_ONLY');
  return { ok: errors.length === 0, errors };
}

export function validateSnmpVersion(version: string, policy: SnmpReadOnlyPolicy): ValidationResult & { version: string } {
  const normalized = normalizeSnmpVersionToken(version);
  if (policy.allowedVersions.includes(normalized)) {
    return { ok: true, version: normalized, errors: [] };
  }
  if (normalized === '1' || normalized === '2c') {
    return { ok: false, version: normalized, errors: ['SNMP_LEGACY_VERSION_PRODUCTION_BLOCKED'] };
  }
  return { ok: false, version: normalized, errors: ['SNMP_VERSION_NOT_ALLOWED'] };
}

export function validateSnmpOperation(operation: string, policy: SnmpReadOnlyPolicy): ValidationResult & { operation: string } {
  const normalized = operation.trim().toUpperCase();
  if (normalized === 'SET') {
    return { ok: false, operation: normalized, errors: ['SNMP_SET_NOT_ALLOWED'] };
  }
  if (policy.deniedOperations.map((op) => op.toUpperCase()).includes(normalized) || WRITE_OPERATIONS.has(normalized)) {
    return { ok: false, operation: normalized, errors: ['SNMP_OPERATION_NOT_ALLOWED'] };
  }
  const allowed = policy.allowedOperations.map((op) => op.toUpperCase());
  if (!allowed.includes(normalized)) {
    return { ok: false, operation: normalized, errors: ['SNMP_OPERATION_NOT_ALLOWED'] };
  }
  return { ok: true, operation: normalized, errors: [] };
}
