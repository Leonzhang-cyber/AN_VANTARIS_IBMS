import { validateOpcUaReadOnlyPolicy } from './opcua-readonly-policy.js';
import {
  validateOpcUaEndpoint,
  normalizeOpcUaEndpoint,
  evaluateOpcUaEndpointRisk,
} from './opcua-endpoint-validator.js';
import {
  validateOpcUaSecurityProfile,
  validateOpcUaIdentityModel,
  validateOpcUaServerIdentityModel,
} from './opcua-security-validator.js';
import { validateOpcUaService } from './opcua-service-validator.js';
import {
  normalizeOpcUaNodeId,
  validateOpcUaNodeId,
  validateOpcUaAttribute,
  validateOpcUaReadRequest,
  validateOpcUaBrowseRequest,
  stringNodeIdHasPrefix,
} from './opcua-nodeid-validator.js';
import { validateOpcUaResponse, normalizeOpcUaVariant } from './opcua-response-validator.js';
import { calculateOpcUaRetryBackoff, evaluateOpcUaRetryDecision } from './opcua-retry-policy.js';
import type {
  OpcUaAcceptanceResult,
  OpcUaReadOnlyPolicy,
  OpcUaSyntheticFixture,
  OpcUaSyntheticTransportResult,
  ValidationResult,
} from './opcua-readonly-types.js';

function normalizeRequestHandle(value: number | string | undefined): number {
  if (typeof value === 'number' && Number.isFinite(value)) return value;
  if (typeof value === 'string' && /^\d+$/.test(value)) return Number(value);
  return 1;
}

export function executeSyntheticOpcUaFixture(
  fixture: OpcUaSyntheticFixture,
  policy: OpcUaReadOnlyPolicy,
): OpcUaSyntheticTransportResult {
  const errors: string[] = [];
  const request = fixture.request;
  const response = fixture.response;

  const endpointResult = validateOpcUaEndpoint(request.endpointUrl, policy, {
    endpointDiscovery: request.endpointDiscovery,
  });
  if (!endpointResult.ok) errors.push(...endpointResult.errors);

  const securityResult = validateOpcUaSecurityProfile(
    {
      securityPolicy: request.securityPolicy,
      messageSecurityMode: request.messageSecurityMode,
    },
    policy,
  );
  if (!securityResult.ok) errors.push(...securityResult.errors);

  const identityResult = validateOpcUaIdentityModel(request, policy);
  if (!identityResult.ok) errors.push(...identityResult.errors);

  const serverIdentityResult = validateOpcUaServerIdentityModel(
    {
      serverFingerprintRef: request.serverFingerprintRef,
      endpointHostname: endpointResult.endpoint?.hostname,
      expectedHostname: endpointResult.endpoint?.hostname,
      applicationUri: request.applicationUri ?? 'urn:opcua:fixture:client',
      serverApplicationUri: request.serverApplicationUri ?? 'urn:opcua:fixture:client',
      trustEstablished: request.serverFingerprintRef ? true : false,
      certificateMismatch: false,
      autoTrust: false,
    },
    policy,
  );
  if (!serverIdentityResult.ok) errors.push(...serverIdentityResult.errors);

  const serviceResult = validateOpcUaService(request.service, policy);
  if (!serviceResult.ok) errors.push(...serviceResult.errors);

  const requestHandle = normalizeRequestHandle(request.requestHandle);
  const service = request.service.trim().toUpperCase().replace(/[\s-]+/g, '_');
  const endpointUrl = request.endpointUrl;

  if (service === 'READ') {
    const readResult = validateOpcUaReadRequest({ reads: request.reads }, policy);
    if (!readResult.ok) errors.push(...readResult.errors);
  }

  if (service === 'BROWSE' || service === 'BROWSE_NEXT') {
    if (request.browse) {
      const browseResult = validateOpcUaBrowseRequest(request.browse, policy);
      if (!browseResult.ok) errors.push(...browseResult.errors);
    } else {
      errors.push('OPCUA_BROWSE_REQUEST_MALFORMED');
    }
  }

  if (response.simulatedTimeout) {
    const retry = evaluateOpcUaRetryDecision({ attempt: 1, errorClass: 'TIMEOUT' }, policy);
    const backoff = calculateOpcUaRetryBackoff(retry.attempt, policy);
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      service,
      endpointUrl,
      requestHandle,
      retryDecision: retry,
      backoffMs: backoff.delayMs,
      errors: [...new Set([...errors, 'OPCUA_TIMEOUT_MODELED'])],
    };
  }

  if (response.malformed) {
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      service,
      endpointUrl,
      requestHandle,
      errors: [...new Set([...errors, 'OPCUA_RESPONSE_MALFORMED'])],
    };
  }

  const responseResult = validateOpcUaResponse(
    {
      requestHandle,
      service,
      reads: request.reads,
    },
    response,
    policy,
  );
  if (!responseResult.ok) errors.push(...responseResult.errors);

  const retryDecision = response.simulatedErrorClass
    ? evaluateOpcUaRetryDecision({ attempt: 1, errorClass: response.simulatedErrorClass }, policy)
    : undefined;
  const backoffMs = retryDecision?.shouldRetry
    ? calculateOpcUaRetryBackoff(retryDecision.attempt, policy).delayMs
    : undefined;

  return {
    accepted: errors.length === 0,
    transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
    service,
    endpointUrl,
    requestHandle,
    retryDecision,
    backoffMs,
    errors: [...new Set(errors)],
  };
}

export function evaluateOpcUaAcceptance(
  policy: OpcUaReadOnlyPolicy,
  fixture: OpcUaSyntheticFixture,
): {
  readonly policyValidation: ValidationResult;
  readonly transport: OpcUaSyntheticTransportResult;
  readonly acceptanceResult: OpcUaAcceptanceResult;
} {
  const policyValidation = validateOpcUaReadOnlyPolicy(policy);
  const transport = executeSyntheticOpcUaFixture(fixture, policy);
  const accepted =
    policyValidation.ok &&
    transport.accepted &&
    policy.syntheticTransportOnly &&
    !policy.networkAccessAllowed &&
    !policy.writeOperationsAllowed;

  return {
    policyValidation,
    transport,
    acceptanceResult: accepted ? 'OPC_UA_READ_ONLY_FOUNDATION_ACCEPTED' : 'OPC_UA_READ_ONLY_FOUNDATION_REJECTED',
  };
}

export { validateOpcUaReadOnlyPolicy } from './opcua-readonly-policy.js';
export { normalizeOpcUaEndpoint, validateOpcUaEndpoint, evaluateOpcUaEndpointRisk } from './opcua-endpoint-validator.js';
export {
  validateOpcUaSecurityProfile,
  validateOpcUaIdentityModel,
  validateOpcUaServerIdentityModel,
} from './opcua-security-validator.js';
export { validateOpcUaService } from './opcua-service-validator.js';
export {
  normalizeOpcUaNodeId,
  validateOpcUaNodeId,
  validateOpcUaAttribute,
  validateOpcUaReadRequest,
  validateOpcUaBrowseRequest,
  stringNodeIdHasPrefix,
} from './opcua-nodeid-validator.js';
export { validateOpcUaResponse, normalizeOpcUaVariant } from './opcua-response-validator.js';
export { calculateOpcUaRetryBackoff, evaluateOpcUaRetryDecision } from './opcua-retry-policy.js';
