import { validateSnmpReadOnlyPolicy, validateSnmpOperation, validateSnmpVersion } from './snmp-readonly-policy.js';
import { validateSnmpCredentialModel, validateSnmpTarget } from './snmp-target-validator.js';
import { validateSnmpOid } from './snmp-oid-validator.js';
import { calculateSnmpRetryBackoff, evaluateSnmpRetryDecision } from './snmp-retry-policy.js';
import { calculateResponseBytes, validateSnmpResponse } from './snmp-response-validator.js';
import type {
  SnmpAcceptanceResult,
  SnmpReadOnlyPolicy,
  SnmpSyntheticFixture,
  SnmpSyntheticTransportResult,
  SnmpVarbind,
  ValidationResult,
} from './snmp-readonly-types.js';

export function executeSyntheticSnmpFixture(
  fixture: SnmpSyntheticFixture,
  policy: SnmpReadOnlyPolicy,
): SnmpSyntheticTransportResult {
  const errors: string[] = [];
  const request = fixture.request;
  const response = fixture.response;

  const versionResult = validateSnmpVersion(String(request.version), policy);
  if (!versionResult.ok) errors.push(...versionResult.errors);

  const operationResult = validateSnmpOperation(String(request.operation), policy);
  if (!operationResult.ok) errors.push(...operationResult.errors);

  const targetResult = validateSnmpTarget(request.target, request.port, policy);
  if (!targetResult.ok) errors.push(...targetResult.errors);

  const credentialResult = validateSnmpCredentialModel(
    {
      credentialRef: request.credentialRef,
      community: request.community,
      authPassword: request.authPassword,
      privPassword: request.privPassword,
      username: request.username,
    },
    policy,
  );
  if (!credentialResult.ok) errors.push(...credentialResult.errors);

  for (const oid of request.oids ?? []) {
    const oidResult = validateSnmpOid(oid, policy);
    if (!oidResult.ok) errors.push(...oidResult.errors);
  }

  if (response.simulatedTimeout) {
    const retry = evaluateSnmpRetryDecision({ attempt: 1, errorClass: 'TIMEOUT' }, policy);
    const backoff = calculateSnmpRetryBackoff(retry.attempt, policy);
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      version: versionResult.version,
      operation: operationResult.operation,
      target: request.target,
      varbindCount: 0,
      retryDecision: retry,
      backoffMs: backoff.delayMs,
      errors: [...new Set([...errors, 'SNMP_TIMEOUT_MODELED'])],
    };
  }

  if (response.malformed) {
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      version: versionResult.version,
      operation: operationResult.operation,
      target: request.target,
      varbindCount: 0,
      errors: [...new Set([...errors, 'SNMP_RESPONSE_MALFORMED'])],
    };
  }

  const varbinds: SnmpVarbind[] = (response.varbinds ?? []).map((vb) => ({
    oid: vb.oid,
    type: vb.type,
    value: vb.value,
  }));

  const responseBytes = calculateResponseBytes(varbinds);
  const metadata = {
    errorStatus: response.errorStatus ?? 0,
    errorIndex: response.errorIndex ?? 0,
    varbinds,
    responseBytes,
    walkDepth: Math.max(...varbinds.map((vb) => vb.oid.split('.').length), 0),
    walkRows: varbinds.length,
    operation: operationResult.operation,
  };

  const responseResult = validateSnmpResponse(metadata, policy);
  if (!responseResult.ok) errors.push(...responseResult.errors);

  const retryDecision = response.simulatedErrorClass
    ? evaluateSnmpRetryDecision({ attempt: 1, errorClass: response.simulatedErrorClass }, policy)
    : undefined;
  const backoffMs = retryDecision?.shouldRetry ? calculateSnmpRetryBackoff(retryDecision.attempt, policy).delayMs : undefined;

  return {
    accepted: errors.length === 0,
    transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
    version: versionResult.version,
    operation: operationResult.operation,
    target: request.target,
    varbindCount: varbinds.length,
    retryDecision,
    backoffMs,
    errors: [...new Set(errors)],
  };
}

export function evaluateSnmpAcceptance(
  policy: SnmpReadOnlyPolicy,
  fixture: SnmpSyntheticFixture,
): {
  readonly policyValidation: ValidationResult;
  readonly transport: SnmpSyntheticTransportResult;
  readonly acceptanceResult: SnmpAcceptanceResult;
} {
  const policyValidation = validateSnmpReadOnlyPolicy(policy);
  const transport = executeSyntheticSnmpFixture(fixture, policy);
  const accepted =
    policyValidation.ok &&
    transport.accepted &&
    policy.syntheticTransportOnly &&
    !policy.networkAccessAllowed &&
    !policy.writeOperationsAllowed;

  return {
    policyValidation,
    transport,
    acceptanceResult: accepted ? 'SNMP_READ_ONLY_FOUNDATION_ACCEPTED' : 'SNMP_READ_ONLY_FOUNDATION_REJECTED',
  };
}

export { validateSnmpReadOnlyPolicy, validateSnmpVersion, validateSnmpOperation } from './snmp-readonly-policy.js';
export { normalizeSnmpTarget, validateSnmpTarget, evaluateSnmpTargetRisk, validateSnmpCredentialModel } from './snmp-target-validator.js';
export { normalizeSnmpOid, validateSnmpOid, oidHasPrefix } from './snmp-oid-validator.js';
export { validateSnmpResponse, calculateResponseBytes } from './snmp-response-validator.js';
export { calculateSnmpRetryBackoff, evaluateSnmpRetryDecision } from './snmp-retry-policy.js';
