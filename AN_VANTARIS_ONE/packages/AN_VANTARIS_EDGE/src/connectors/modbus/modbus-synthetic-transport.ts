import { validateModbusReadOnlyPolicy } from './modbus-readonly-policy.js';
import { validateModbusRequest, decodeModbusRegisters } from './modbus-address-validator.js';
import { validateModbusTarget, validateModbusCredentialModel } from './modbus-target-validator.js';
import { calculateModbusRetryBackoff, evaluateModbusRetryDecision } from './modbus-retry-policy.js';
import { calculateModbusResponseBytes, validateModbusResponse } from './modbus-response-validator.js';
import type {
  ModbusAcceptanceResult,
  ModbusRegisterDecodeInput,
  ModbusRegisterDecodeResult,
  ModbusSyntheticFixture,
  ModbusSyntheticTransportResult,
  ModbusTcpReadOnlyPolicy,
  ValidationResult,
} from './modbus-readonly-types.js';

export function executeSyntheticModbusFixture(
  fixture: ModbusSyntheticFixture,
  policy: ModbusTcpReadOnlyPolicy,
): ModbusSyntheticTransportResult {
  const errors: string[] = [];
  const request = fixture.request;
  const response = fixture.response;

  const targetResult = validateModbusTarget(request.target, request.port, policy);
  if (!targetResult.ok) errors.push(...targetResult.errors);

  const credentialResult = validateModbusCredentialModel({
    credentialRef: request.credentialRef,
    username: request.username,
    password: request.password,
    token: request.token,
  });
  if (!credentialResult.ok) errors.push(...credentialResult.errors);

  const requestResult = validateModbusRequest(request, policy);
  if (!requestResult.ok) errors.push(...requestResult.errors);

  const port = targetResult.target?.port ?? request.port ?? policy.allowedPorts[0] ?? 502;
  const functionCode = requestResult.functionCode ?? 0;
  const unitId = requestResult.unitId ?? 0;
  const quantity = requestResult.quantity ?? 0;

  if (response.simulatedTimeout) {
    const retry = evaluateModbusRetryDecision({ attempt: 1, errorClass: 'TIMEOUT' }, policy);
    const backoff = calculateModbusRetryBackoff(retry.attempt, policy);
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      functionCode,
      target: request.target,
      port,
      unitId,
      retryDecision: retry,
      backoffMs: backoff.delayMs,
      errors: [...new Set([...errors, 'MODBUS_TIMEOUT_MODELED'])],
    };
  }

  if (response.malformed) {
    return {
      accepted: false,
      transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
      functionCode,
      target: request.target,
      port,
      unitId,
      errors: [...new Set([...errors, 'MODBUS_RESPONSE_MALFORMED'])],
    };
  }

  const responseResult = validateModbusResponse(
    {
      transactionId: request.transactionId ?? response.transactionId,
      unitId,
      functionCode,
      quantity,
    },
    response,
    policy,
  );
  if (!responseResult.ok) errors.push(...responseResult.errors);

  const retryDecision = response.simulatedErrorClass
    ? evaluateModbusRetryDecision({ attempt: 1, errorClass: response.simulatedErrorClass }, policy)
    : undefined;
  const backoffMs = retryDecision?.shouldRetry
    ? calculateModbusRetryBackoff(retryDecision.attempt, policy).delayMs
    : undefined;

  if (calculateModbusResponseBytes(response) > policy.maxResponseBytes) {
    errors.push('MODBUS_RESPONSE_TOO_LARGE');
  }

  return {
    accepted: errors.length === 0,
    transportMode: 'SYNTHETIC_TRANSPORT_ONLY',
    functionCode,
    target: request.target,
    port,
    unitId,
    retryDecision,
    backoffMs,
    errors: [...new Set(errors)],
  };
}

export function evaluateModbusAcceptance(
  policy: ModbusTcpReadOnlyPolicy,
  fixture: ModbusSyntheticFixture,
): {
  readonly policyValidation: ValidationResult;
  readonly transport: ModbusSyntheticTransportResult;
  readonly acceptanceResult: ModbusAcceptanceResult;
} {
  const policyValidation = validateModbusReadOnlyPolicy(policy);
  const transport = executeSyntheticModbusFixture(fixture, policy);
  const accepted =
    policyValidation.ok &&
    transport.accepted &&
    policy.syntheticTransportOnly &&
    !policy.networkAccessAllowed &&
    !policy.writeOperationsAllowed;

  return {
    policyValidation,
    transport,
    acceptanceResult: accepted ? 'MODBUS_TCP_READ_ONLY_FOUNDATION_ACCEPTED' : 'MODBUS_TCP_READ_ONLY_FOUNDATION_REJECTED',
  };
}

export { validateModbusReadOnlyPolicy } from './modbus-readonly-policy.js';
export { normalizeModbusTarget, validateModbusTarget, evaluateModbusTargetRisk, validateModbusCredentialModel } from './modbus-target-validator.js';
export { validateModbusFunctionCode, registerSpaceForFunctionCode } from './modbus-function-validator.js';
export { validateModbusUnitId, validateModbusAddressRange, validateModbusRequest, decodeModbusRegisters } from './modbus-address-validator.js';
export { validateModbusResponse, calculateModbusResponseBytes } from './modbus-response-validator.js';
export { calculateModbusRetryBackoff, evaluateModbusRetryDecision } from './modbus-retry-policy.js';
