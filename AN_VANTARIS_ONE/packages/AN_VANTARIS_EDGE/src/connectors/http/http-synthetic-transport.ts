import { validateHttpPollingPolicy } from './http-readonly-policy.js';
import {
  normalizeHttpDestination,
  validateHttpCredentialModel,
  validateHttpDestination,
  validateHttpMethod,
} from './http-destination-validator.js';
import { calculateHttpRetryBackoff, evaluateHttpRetryDecision } from './http-retry-policy.js';
import {
  parseHttpCsvResponse,
  parseHttpJsonResponse,
  validateHttpResponseMetadata,
} from './http-response-validator.js';
import type {
  HttpPollingAcceptanceResult,
  HttpPollingReadOnlyPolicy,
  HttpSyntheticFixture,
  HttpSyntheticTransportResult,
  ValidationResult,
} from './http-readonly-types.js';

function normalizeContentType(value: string | undefined): string {
  return (value ?? '').split(';')[0].trim().toLowerCase();
}

export function executeSyntheticHttpPollingFixture(
  fixture: HttpSyntheticFixture,
  policy: HttpPollingReadOnlyPolicy,
): HttpSyntheticTransportResult {
  const errors: string[] = [];
  const request = fixture.request;
  const response = fixture.response;

  const methodResult = validateHttpMethod(request.method, policy);
  if (!methodResult.ok) errors.push(...methodResult.errors);

  const destinationResult = validateHttpDestination(request.url, policy);
  if (!destinationResult.ok) errors.push(...destinationResult.errors);

  const credentialResult = validateHttpCredentialModel(
    {
      credentialRef: request.credentialRef,
      url: request.url,
      authorizationHeader: request.headers?.Authorization ?? request.headers?.authorization,
      bearerToken: request.headers?.Authorization?.startsWith('Bearer ') ? request.headers.Authorization.slice(7) : undefined,
      apiKey: request.headers?.['X-API-Key'] ?? request.headers?.['x-api-key'],
    },
    policy,
  );
  if (!credentialResult.ok) errors.push(...credentialResult.errors);

  if (response.simulatedTimeout) {
    const retry = evaluateHttpRetryDecision({ attempt: 1, errorClass: 'TIMEOUT' }, policy);
    const backoff = calculateHttpRetryBackoff(retry.attempt, policy);
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      method: methodResult.method,
      url: request.url,
      retryDecision: retry,
      backoffMs: backoff.delayMs,
      redirectRejected: false,
      errors: [...errors, 'HTTP_TIMEOUT_MODELED'],
    };
  }

  const body = response.body ?? '';
  const bodyBytes = Buffer.byteLength(body, 'utf8');
  const metadata = {
    statusCode: response.statusCode,
    contentType: response.headers?.['content-type'] ?? response.headers?.['Content-Type'],
    contentLength: response.headers?.['content-length']
      ? Number(response.headers['content-length'])
      : bodyBytes,
    bodyBytes,
    redirectLocation: response.headers?.location ?? response.headers?.Location,
    encoding: response.headers?.['content-encoding'] ?? response.headers?.['Content-Encoding'],
  };

  const metadataResult = validateHttpResponseMetadata(metadata, policy);
  if (!metadataResult.ok) errors.push(...metadataResult.errors);

  let parsed;
  const contentType = normalizeContentType(metadata.contentType);
  if (errors.length === 0 && metadata.statusCode >= 200 && metadata.statusCode < 300) {
    if (contentType === 'application/json') {
      const jsonResult = parseHttpJsonResponse(body, policy);
      if ('ok' in jsonResult && jsonResult.ok === false) errors.push(...jsonResult.errors);
      else parsed = jsonResult;
    } else if (contentType === 'text/csv') {
      const csvResult = parseHttpCsvResponse(body, policy);
      if ('ok' in csvResult && csvResult.ok === false) errors.push(...csvResult.errors);
      else parsed = csvResult;
    }
  }

  const retryDecision =
    metadata.statusCode >= 400
      ? evaluateHttpRetryDecision({ attempt: 1, statusCode: metadata.statusCode }, policy)
      : undefined;
  const backoffMs = retryDecision?.shouldRetry ? calculateHttpRetryBackoff(retryDecision.attempt, policy).delayMs : undefined;

  return {
    accepted: errors.length === 0,
    transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
    method: methodResult.method,
    url: request.url,
    statusCode: metadata.statusCode,
    parsed: parsed as HttpSyntheticTransportResult['parsed'],
    retryDecision,
    backoffMs,
    redirectRejected: errors.includes('HTTP_REDIRECT_REJECTED'),
    errors: [...new Set(errors)],
  };
}

export function evaluateHttpPollingAcceptance(
  policy: HttpPollingReadOnlyPolicy,
  fixture: HttpSyntheticFixture,
): {
  readonly policyValidation: ValidationResult;
  readonly transport: HttpSyntheticTransportResult;
  readonly acceptanceResult: HttpPollingAcceptanceResult;
} {
  const policyValidation = validateHttpPollingPolicy(policy);
  const transport = executeSyntheticHttpPollingFixture(fixture, policy);
  const accepted =
    policyValidation.ok &&
    transport.accepted &&
    policy.syntheticTransportOnly &&
    !policy.networkAccessAllowed &&
    !policy.writeMethodsAllowed;

  return {
    policyValidation,
    transport,
    acceptanceResult: accepted
      ? 'HTTP_POLLING_READ_ONLY_FOUNDATION_ACCEPTED'
      : 'HTTP_POLLING_READ_ONLY_FOUNDATION_REJECTED',
  };
}

export { validateHttpPollingPolicy } from './http-readonly-policy.js';
export {
  normalizeHttpDestination,
  validateHttpDestination,
  evaluateSsrfRisk,
  validateHttpMethod,
  validateHttpCredentialModel,
} from './http-destination-validator.js';
export {
  validateHttpResponseMetadata,
  parseHttpJsonResponse,
  parseHttpCsvResponse,
} from './http-response-validator.js';
export { calculateHttpRetryBackoff, evaluateHttpRetryDecision } from './http-retry-policy.js';
