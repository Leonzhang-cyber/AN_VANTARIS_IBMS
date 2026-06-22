import { registerSpaceForFunctionCode } from '../modbus-function-validator.js';
import { validateModbusReadOnlyPolicy } from '../modbus-readonly-policy.js';
import { decodeModbusRegisters, validateModbusAddressRange, validateModbusRequest, validateModbusUnitId } from '../modbus-address-validator.js';
import { validateModbusFunctionCode } from '../modbus-function-validator.js';
import { validateModbusResponse } from '../modbus-response-validator.js';
import type { ModbusDecodeType, ModbusRegisterSpace, ModbusResponseFrame, ModbusTcpReadOnlyPolicy } from '../modbus-readonly-types.js';

import type {
  ModbusProductionAdapterConfig,
  ModbusProductionErrorCode,
  ModbusProductionNormalizedRecord,
  ModbusProductionFunctionCode,
  ModbusProductionResolvedTarget,
} from './modbus-production-adapter.types.js';
import {
  MODBUS_PRODUCTION_DANGEROUS_KEYS,
  MODBUS_PRODUCTION_FORMULA_PREFIXES,
  MODBUS_PRODUCTION_READ_FUNCTION_CODES,
  MODBUS_PRODUCTION_WRITE_FUNCTION_CODES,
} from './modbus-production-adapter.types.js';
import {
  buildFoundationPolicyForProduction,
  maxQuantityForFunctionCode,
  validateProductionResourceLimits,
} from './modbus-production-target-policy.js';

export function mapProductionDataType(dataType: ModbusProductionAdapterConfig['dataType']): ModbusDecodeType | null {
  switch (dataType) {
    case 'uint16': return 'UInt16';
    case 'int16': return 'Int16';
    case 'uint32': return 'UInt32';
    case 'int32': return 'Int32';
    case 'float32': return 'Float32';
    case 'boolean': return 'Boolean';
    case 'raw': return 'RAW';
    default: return null;
  }
}

export function validateProductionAdapterConfig(config: ModbusProductionAdapterConfig): ModbusProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_MODBUS_TCP_READONLY') return 'MODBUS_CONFIG_INVALID';
  if (config.enabled !== true) return 'MODBUS_ADAPTER_DISABLED';
  if (!config.targetReferenceId) return 'MODBUS_CONFIG_INVALID';
  if (!MODBUS_PRODUCTION_READ_FUNCTION_CODES.includes(config.functionCode as ModbusProductionFunctionCode)) {
    return 'MODBUS_FUNCTION_NOT_ALLOWED';
  }
  if ((MODBUS_PRODUCTION_WRITE_FUNCTION_CODES as readonly number[]).includes(config.functionCode)) {
    return 'MODBUS_FUNCTION_NOT_ALLOWED';
  }
  if (!Number.isInteger(config.unitId) || config.unitId < 0 || config.unitId > 247) return 'MODBUS_UNIT_ID_INVALID';
  if (!Number.isInteger(config.startAddress) || config.startAddress < 0 || config.startAddress > config.maxRegisterAddress) {
    return 'MODBUS_ADDRESS_INVALID';
  }
  if (!Number.isInteger(config.quantity) || config.quantity <= 0) return 'MODBUS_QUANTITY_INVALID';
  if (config.quantity > maxQuantityForFunctionCode(config.functionCode)) return 'MODBUS_QUANTITY_INVALID';
  if (config.quantity > config.maxQuantity) return 'MODBUS_QUANTITY_INVALID';
  if (config.startAddress + config.quantity - 1 > 65535) return 'MODBUS_ADDRESS_INVALID';
  if (!(config.targetPort >= 1 && config.targetPort <= 65535)) return 'MODBUS_PORT_NOT_ALLOWED';
  if (config.tcpMode !== 'PRODUCTION_TCP' && config.tcpMode !== 'LOOPBACK_TEST') return 'MODBUS_CONFIG_INVALID';
  if (config.dnsMode !== 'DENY' && config.dnsMode !== 'INJECTED_TEST') return 'MODBUS_CONFIG_INVALID';
  if (config.formulaPrefixPolicy !== 'REJECT' && config.formulaPrefixPolicy !== 'MARK') return 'MODBUS_CONFIG_INVALID';
  if (config.dangerousKeyPolicy !== 'REJECT') return 'MODBUS_CONFIG_INVALID';
  if (!mapProductionDataType(config.dataType)) return 'MODBUS_DATA_TYPE_UNSUPPORTED';
  return validateProductionResourceLimits(config);
}

export function runFoundationRequestValidation(
  target: ModbusProductionResolvedTarget,
  config: ModbusProductionAdapterConfig,
  testMode: boolean,
): ModbusProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(target, config, testMode);
  const registerSpace = registerSpaceForFunctionCode(config.functionCode);
  if (!registerSpace) return 'MODBUS_FUNCTION_NOT_ALLOWED';

  const requestValidation = validateModbusRequest(
    {
      target: target.hostname,
      port: target.port,
      unitId: config.unitId,
      functionCode: config.functionCode,
      registerSpace,
      startAddress: config.startAddress,
      quantity: config.quantity,
    },
    policy,
  );
  if (!requestValidation.ok) {
    if (requestValidation.errors.includes('MODBUS_WRITE_FUNCTION_PROHIBITED')) return 'MODBUS_FUNCTION_NOT_ALLOWED';
    if (requestValidation.errors.includes('MODBUS_UNIT_ID_INVALID')) return 'MODBUS_UNIT_ID_INVALID';
    if (requestValidation.errors.includes('MODBUS_ADDRESS_INVALID') || requestValidation.errors.includes('MODBUS_ADDRESS_OVERFLOW')) {
      return 'MODBUS_ADDRESS_INVALID';
    }
    if (requestValidation.errors.includes('MODBUS_QUANTITY_INVALID') || requestValidation.errors.includes('MODBUS_REQUEST_LIMIT_EXCEEDED')) {
      return 'MODBUS_QUANTITY_INVALID';
    }
    return 'MODBUS_FOUNDATION_VALIDATION_FAILED';
  }

  if (testMode && config.tcpMode === 'LOOPBACK_TEST') {
    return null;
  }

  const policyValidation = validateModbusReadOnlyPolicy({
    ...policy,
    syntheticTransportOnly: false,
  } as unknown as ModbusTcpReadOnlyPolicy);
  if (!policyValidation.ok) return 'MODBUS_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function mapFoundationResponseError(errors: readonly string[]): ModbusProductionErrorCode {
  if (errors.includes('MODBUS_TRANSACTION_ID_MISMATCH')) return 'MODBUS_TRANSACTION_MISMATCH';
  if (errors.includes('MODBUS_UNIT_ID_MISMATCH')) return 'MODBUS_UNIT_ID_MISMATCH';
  if (errors.includes('MODBUS_FUNCTION_MISMATCH')) return 'MODBUS_FUNCTION_MISMATCH';
  if (errors.includes('MODBUS_EXCEPTION_RESPONSE')) return 'MODBUS_EXCEPTION_RESPONSE';
  if (errors.includes('MODBUS_PROTOCOL_ID_INVALID') || errors.includes('MODBUS_RESPONSE_MALFORMED')) return 'MODBUS_MBAP_INVALID';
  if (errors.includes('MODBUS_BYTE_COUNT_MISMATCH')) return 'MODBUS_BYTE_COUNT_INVALID';
  if (errors.includes('MODBUS_RESPONSE_TOO_LARGE')) return 'MODBUS_FRAME_SIZE_LIMIT_EXCEEDED';
  return 'MODBUS_PDU_INVALID';
}

export function validateFoundationResponse(
  request: {
    transactionId: number;
    unitId: number;
    functionCode: number;
    quantity: number;
  },
  frame: ModbusResponseFrame,
  target: ModbusProductionResolvedTarget,
  config: ModbusProductionAdapterConfig,
  testMode: boolean,
): ModbusProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(target, config, testMode);
  const validation = validateModbusResponse(request, frame, policy);
  if (!validation.ok) return mapFoundationResponseError(validation.errors);
  return null;
}

function registersFromFrame(frame: ModbusResponseFrame, functionCode: number): number[] {
  const payload = frame.payload ?? [];
  if (functionCode === 1 || functionCode === 2) {
    const values: number[] = [];
    for (let i = 0; i < payload.length; i += 1) {
      values.push(payload[i]);
    }
    return values;
  }
  const registers: number[] = [];
  for (let i = 0; i < payload.length; i += 2) {
    if (i + 1 >= payload.length) break;
    registers.push((payload[i] << 8) | payload[i + 1]);
  }
  return registers;
}

export function normalizeDecodedValues(
  values: readonly number[] | readonly boolean[],
  config: ModbusProductionAdapterConfig,
): { ok: true; records: ModbusProductionNormalizedRecord[] } | { ok: false; errorCode: ModbusProductionErrorCode } {
  const records: ModbusProductionNormalizedRecord[] = [];
  for (let index = 0; index < values.length; index += 1) {
    const value = values[index];
    const fields: Record<string, string> = {
      index: String(index),
      value: String(value),
      functionCode: String(config.functionCode),
      startAddress: String(config.startAddress + index),
    };
    for (const prefix of MODBUS_PRODUCTION_FORMULA_PREFIXES) {
      if (String(fields.value).trimStart().startsWith(prefix) && config.formulaPrefixPolicy === 'REJECT') {
        return { ok: false, errorCode: 'MODBUS_DECODE_FAILED' };
      }
    }
    for (const key of MODBUS_PRODUCTION_DANGEROUS_KEYS) {
      if (Object.prototype.hasOwnProperty.call(fields, key)) {
        return { ok: false, errorCode: 'MODBUS_DECODE_FAILED' };
      }
    }
    records.push({ fields });
  }
  return { ok: true, records };
}

export function decodeAndNormalizeResponse(
  frame: ModbusResponseFrame,
  target: ModbusProductionResolvedTarget,
  config: ModbusProductionAdapterConfig,
  testMode: boolean,
): { ok: true; records: ModbusProductionNormalizedRecord[] } | { ok: false; errorCode: ModbusProductionErrorCode } {
  const foundationError = validateFoundationResponse(
    {
      transactionId: frame.transactionId,
      unitId: config.unitId,
      functionCode: config.functionCode,
      quantity: config.quantity,
    },
    frame,
    target,
    config,
    testMode,
  );
  if (foundationError) return { ok: false, errorCode: foundationError };

  const policy = buildFoundationPolicyForProduction(target, config, testMode);
  const decodeType = mapProductionDataType(config.dataType);
  if (!decodeType) return { ok: false, errorCode: 'MODBUS_DATA_TYPE_UNSUPPORTED' };

  if (config.functionCode === 1 || config.functionCode === 2) {
    if (config.dataType !== 'boolean' && config.dataType !== 'raw') {
      return { ok: false, errorCode: 'MODBUS_DATA_TYPE_UNSUPPORTED' };
    }
    const bits: boolean[] = [];
    const payload = frame.payload ?? [];
    for (let i = 0; i < config.quantity; i += 1) {
      const byteIndex = Math.floor(i / 8);
      const bitIndex = i % 8;
      const byte = payload[byteIndex] ?? 0;
      bits.push(((byte >> bitIndex) & 1) === 1);
    }
    return normalizeDecodedValues(bits, config);
  }

  const registers = registersFromFrame(frame, config.functionCode);
  if (decodeType === 'UInt16' || decodeType === 'Int16') {
    const values = registers.slice(0, config.quantity).map((register) =>
      decodeType === 'Int16' ? ((register << 16) >> 16) : register,
    );
    return normalizeDecodedValues(values, config);
  }

  if (decodeType === 'RAW') {
    return normalizeDecodedValues(registers.slice(0, config.quantity), config);
  }

  const values: number[] = [];
  const registersPerValue = decodeType === 'UInt32' || decodeType === 'Int32' || decodeType === 'Float32' ? 2 : 1;
  for (let index = 0; index + registersPerValue <= registers.length && values.length < config.quantity; index += registersPerValue) {
    const decoded = decodeModbusRegisters(
      {
        registers: registers.slice(index, index + registersPerValue),
        dataType: decodeType,
        byteOrder: config.byteOrder,
        wordOrder: config.wordOrder,
      },
      policy,
    );
    if (!decoded.ok || !decoded.values || decoded.values.length === 0) {
      return { ok: false, errorCode: 'MODBUS_DECODE_FAILED' };
    }
    values.push(decoded.values[0] as number);
  }
  if (values.length === 0) return { ok: false, errorCode: 'MODBUS_DECODE_FAILED' };
  return normalizeDecodedValues(values, config);
}

export type { ModbusResponseFrame, ModbusTcpReadOnlyPolicy, ModbusRegisterSpace };
