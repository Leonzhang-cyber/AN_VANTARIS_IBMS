import { validateBacnetReadOnlyPolicy } from './bacnet-readonly-policy.js';
import { validateBacnetRequest } from './bacnet-property-validator.js';
import { validateBacnetTarget, validateBacnetCredentialModel } from './bacnet-target-validator.js';
import { calculateBacnetRetryBackoff, evaluateBacnetRetryDecision } from './bacnet-retry-policy.js';
import { validateBacnetResponse } from './bacnet-response-validator.js';
import type {
  BacnetAcceptanceResult,
  BacnetIpReadOnlyPolicy,
  BacnetSyntheticFixture,
  BacnetSyntheticTransportResult,
  ValidationResult,
} from './bacnet-readonly-types.js';

export function executeSyntheticBacnetFixture(
  fixture: BacnetSyntheticFixture,
  policy: BacnetIpReadOnlyPolicy,
): BacnetSyntheticTransportResult {
  const errors: string[] = [];
  const request = fixture.request;
  const response = fixture.response;

  const targetResult = validateBacnetTarget(request.target, request.port, policy, {
    broadcast: request.broadcast,
    bbmd: request.bbmd,
    foreignDeviceRegistration: request.foreignDeviceRegistration,
  });
  if (!targetResult.ok) errors.push(...targetResult.errors);

  const credentialResult = validateBacnetCredentialModel({
    credentialRef: request.credentialRef,
    username: request.username,
    password: request.password,
    token: request.token,
  });
  if (!credentialResult.ok) errors.push(...credentialResult.errors);

  const requestResult = validateBacnetRequest(request, policy);
  if (!requestResult.ok) errors.push(...requestResult.errors);

  const port = targetResult.target?.port ?? request.port ?? policy.allowedPorts[0] ?? 47808;
  const service = requestResult.service ?? request.service;
  const deviceInstance = requestResult.deviceInstance ?? 0;
  const invokeId = requestResult.invokeId ?? Number(request.invokeId ?? 1);

  if (response.simulatedTimeout) {
    const retry = evaluateBacnetRetryDecision({ attempt: 1, errorClass: 'TIMEOUT' }, policy);
    const backoff = calculateBacnetRetryBackoff(retry.attempt, policy);
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      service,
      target: request.target,
      port,
      deviceInstance,
      retryDecision: retry,
      backoffMs: backoff.delayMs,
      errors: [...new Set([...errors, 'BACNET_TIMEOUT_MODELED'])],
    };
  }

  if (response.malformed) {
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      service,
      target: request.target,
      port,
      deviceInstance,
      errors: [...new Set([...errors, 'BACNET_RESPONSE_MALFORMED'])],
    };
  }

  const responseResult = validateBacnetResponse(
    {
      invokeId,
      service,
      deviceInstance,
      reads: request.reads,
    },
    response,
    policy,
  );
  if (!responseResult.ok) errors.push(...responseResult.errors);

  const retryDecision = response.simulatedErrorClass
    ? evaluateBacnetRetryDecision({ attempt: 1, errorClass: response.simulatedErrorClass }, policy)
    : undefined;
  const backoffMs = retryDecision?.shouldRetry
    ? calculateBacnetRetryBackoff(retryDecision.attempt, policy).delayMs
    : undefined;

  return {
    accepted: errors.length === 0,
    transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
    service,
    target: request.target,
    port,
    deviceInstance,
    retryDecision,
    backoffMs,
    errors: [...new Set(errors)],
  };
}

export function evaluateBacnetAcceptance(
  policy: BacnetIpReadOnlyPolicy,
  fixture: BacnetSyntheticFixture,
): {
  readonly policyValidation: ValidationResult;
  readonly transport: BacnetSyntheticTransportResult;
  readonly acceptanceResult: BacnetAcceptanceResult;
} {
  const policyValidation = validateBacnetReadOnlyPolicy(policy);
  const transport = executeSyntheticBacnetFixture(fixture, policy);
  const accepted =
    policyValidation.ok &&
    transport.accepted &&
    policy.syntheticTransportOnly &&
    !policy.networkAccessAllowed &&
    !policy.writeOperationsAllowed;

  return {
    policyValidation,
    transport,
    acceptanceResult: accepted ? 'BACNET_IP_READ_ONLY_FOUNDATION_ACCEPTED' : 'BACNET_IP_READ_ONLY_FOUNDATION_REJECTED',
  };
}

export { validateBacnetReadOnlyPolicy } from './bacnet-readonly-policy.js';
export { normalizeBacnetTarget, validateBacnetTarget, evaluateBacnetTargetRisk, validateBacnetCredentialModel } from './bacnet-target-validator.js';
export { validateBacnetService } from './bacnet-service-validator.js';
export { validateBacnetDeviceInstance, validateBacnetObjectIdentifier } from './bacnet-object-validator.js';
export { validateBacnetProperty, validateBacnetArrayIndex, validateBacnetRequest } from './bacnet-property-validator.js';
export { validateBacnetResponse, normalizeBacnetValue } from './bacnet-response-validator.js';
export { calculateBacnetRetryBackoff, evaluateBacnetRetryDecision } from './bacnet-retry-policy.js';
