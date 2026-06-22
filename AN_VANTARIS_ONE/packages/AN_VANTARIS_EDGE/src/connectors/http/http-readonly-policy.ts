import type { HttpPollingReadOnlyPolicy, ValidationResult } from './http-readonly-types.js';

const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE', 'CONNECT', 'TRACE']);
const FOUNDATION_METHODS = new Set(['GET']);

export function validateHttpPollingPolicy(policy: HttpPollingReadOnlyPolicy): ValidationResult {
  const errors: string[] = [];
  if (policy.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (policy.taskId !== 'UFMS-EDGE-C5-02') errors.push('taskId mismatch');
  if (policy.classification !== 'CONTROLLED_HTTP_POLLING_READ_ONLY_FOUNDATION') errors.push('classification mismatch');
  if (!Array.isArray(policy.allowedSchemes) || policy.allowedSchemes.length === 0) errors.push('allowedSchemes required');
  if (!Array.isArray(policy.allowedMethods) || policy.allowedMethods.length === 0) errors.push('allowedMethods required');
  if (!policy.allowedMethods.every((method) => FOUNDATION_METHODS.has(method.toUpperCase()))) {
    errors.push('allowedMethods must be GET-only in foundation');
  }
  if (!Array.isArray(policy.allowedHosts) || policy.allowedHosts.length === 0) errors.push('allowedHosts required');
  if (!Array.isArray(policy.deniedHosts)) errors.push('deniedHosts required');
  if (!Array.isArray(policy.deniedCidrs) || policy.deniedCidrs.length === 0) errors.push('deniedCidrs required');
  if (policy.redirectPolicy !== 'REJECT') errors.push('redirectPolicy must be REJECT in foundation');
  if (policy.maxRedirects !== 0) errors.push('maxRedirects must be 0 in foundation');
  if (!(policy.requestTimeoutMs > 0)) errors.push('requestTimeoutMs must be positive');
  if (!(policy.maxRetryAttempts >= 0)) errors.push('maxRetryAttempts invalid');
  if (!(policy.maxResponseBytes > 0)) errors.push('maxResponseBytes must be positive');
  if (!Array.isArray(policy.allowedContentTypes) || policy.allowedContentTypes.length === 0) {
    errors.push('allowedContentTypes required');
  }
  if (policy.credentialMode !== 'REFERENCE_ONLY') errors.push('credentialMode must be REFERENCE_ONLY');
  if (policy.plaintextCredentialsAllowed) errors.push('plaintextCredentialsAllowed must be false');
  if (policy.dnsResolutionMode !== 'MODELED_ONLY') errors.push('dnsResolutionMode must be MODELED_ONLY');
  if (policy.networkAccessAllowed) errors.push('networkAccessAllowed must be false');
  if (!policy.syntheticTransportOnly) errors.push('syntheticTransportOnly must be true');
  if (policy.writeMethodsAllowed) errors.push('writeMethodsAllowed must be false');
  if (policy.responseParsingMode !== 'FOUNDATION_JSON_CSV') errors.push('responseParsingMode mismatch');
  if (!policy.jsonAllowObject && !policy.jsonAllowArray) errors.push('json must allow object or array');
  if (policy.jsonAllowScalar) errors.push('jsonAllowScalar must be false in foundation');
  if (policy.jsonMaxDepth < 1) errors.push('jsonMaxDepth must be >=1');
  if (!policy.csvHeaderRequired) errors.push('csvHeaderRequired must be true');
  if (policy.csvDelimiter !== ',') errors.push('csvDelimiter must be comma');
  if (policy.csvMaxRows < 1) errors.push('csvMaxRows must be >=1');
  if (!(policy.backoffBaseMs > 0)) errors.push('backoffBaseMs must be positive');
  if (!(policy.backoffMultiplier >= 1)) errors.push('backoffMultiplier must be >=1');
  if (!(policy.backoffMaxMs >= policy.backoffBaseMs)) errors.push('backoffMaxMs must be >= backoffBaseMs');
  for (const method of WRITE_METHODS) {
    if (policy.allowedMethods.map((x) => x.toUpperCase()).includes(method)) {
      errors.push(`write method ${method} must not be allowed`);
    }
  }
  return { ok: errors.length === 0, errors };
}
