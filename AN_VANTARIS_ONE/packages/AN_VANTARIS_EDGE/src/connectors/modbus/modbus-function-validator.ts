import type { ModbusRegisterSpace, ModbusTcpReadOnlyPolicy, ValidationResult } from './modbus-readonly-types.js';

const WRITE_FUNCTION_CODES = new Set([5, 6, 15, 16, 22, 23]);

export const FUNCTION_CODE_TO_REGISTER_SPACE: Readonly<Record<number, ModbusRegisterSpace>> = {
  1: 'COIL',
  2: 'DISCRETE_INPUT',
  3: 'HOLDING_REGISTER',
  4: 'INPUT_REGISTER',
};

export function normalizeModbusFunctionCode(functionCode: number | string): number | null {
  const num = typeof functionCode === 'string' ? Number(functionCode.trim()) : functionCode;
  if (!Number.isInteger(num)) return null;
  return num;
}

export function validateModbusFunctionCode(
  functionCode: number | string,
  policy: ModbusTcpReadOnlyPolicy,
): ValidationResult & { functionCode?: number } {
  const num = normalizeModbusFunctionCode(functionCode);
  if (num === null || num < 0 || num > 127 || num === 0) {
    return { ok: false, errors: ['MODBUS_FUNCTION_INVALID'] };
  }
  if (WRITE_FUNCTION_CODES.has(num) || policy.deniedFunctionCodes.includes(num)) {
    return { ok: false, functionCode: num, errors: ['MODBUS_WRITE_FUNCTION_PROHIBITED'] };
  }
  if (!policy.allowedFunctionCodes.includes(num)) {
    return { ok: false, functionCode: num, errors: ['MODBUS_FUNCTION_NOT_ALLOWED'] };
  }
  return { ok: true, functionCode: num, errors: [] };
}

export function registerSpaceForFunctionCode(functionCode: number): ModbusRegisterSpace | null {
  return FUNCTION_CODE_TO_REGISTER_SPACE[functionCode] ?? null;
}
