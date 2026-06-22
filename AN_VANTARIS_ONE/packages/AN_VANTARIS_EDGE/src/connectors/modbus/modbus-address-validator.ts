import type {
  ModbusRegisterSpace,
  ModbusRequestValidation,
  ModbusTcpReadOnlyPolicy,
  ValidationResult,
} from './modbus-readonly-types.js';
import { registerSpaceForFunctionCode, validateModbusFunctionCode } from './modbus-function-validator.js';

const COIL_SPACES = new Set<ModbusRegisterSpace>(['COIL', 'DISCRETE_INPUT']);
const REGISTER_SPACES = new Set<ModbusRegisterSpace>(['HOLDING_REGISTER', 'INPUT_REGISTER']);

function parseInteger(value: number | string, field: string): number | null {
  const num = typeof value === 'string' ? Number(value.trim()) : value;
  if (!Number.isInteger(num)) return null;
  return num;
}

export function validateModbusUnitId(
  unitId: number | string,
  policy: ModbusTcpReadOnlyPolicy,
): ValidationResult & { unitId?: number } {
  const num = parseInteger(unitId, 'unitId');
  if (num === null || num < 0 || num > 247) {
    return { ok: false, errors: ['MODBUS_UNIT_ID_INVALID'] };
  }
  if (!policy.allowedUnitIds.includes(num)) {
    return { ok: false, unitId: num, errors: ['MODBUS_UNIT_ID_NOT_ALLOWED'] };
  }
  return { ok: true, unitId: num, errors: [] };
}

function addressInRange(
  space: ModbusRegisterSpace,
  startAddress: number,
  endAddress: number,
  policy: ModbusTcpReadOnlyPolicy,
): boolean {
  return policy.allowedAddressRanges.some(
    (range) => range.space === space && startAddress >= range.start && endAddress <= range.end,
  );
}

export function validateModbusAddressRange(
  input: {
    functionCode: number;
    registerSpace: ModbusRegisterSpace;
    startAddress: number | string;
    quantity: number | string;
  },
  policy: ModbusTcpReadOnlyPolicy,
): ValidationResult & { startAddress?: number; quantity?: number; endAddress?: number } {
  const expectedSpace = registerSpaceForFunctionCode(input.functionCode);
  if (!expectedSpace || expectedSpace !== input.registerSpace) {
    return { ok: false, errors: ['MODBUS_REGISTER_SPACE_MISMATCH'] };
  }

  const startAddress = parseInteger(input.startAddress, 'startAddress');
  const quantity = parseInteger(input.quantity, 'quantity');

  if (startAddress === null || startAddress < 0 || startAddress > 65535) {
    return { ok: false, errors: ['MODBUS_ADDRESS_INVALID'] };
  }
  if (quantity === null || quantity <= 0) {
    return { ok: false, errors: ['MODBUS_QUANTITY_INVALID'] };
  }

  const endAddress = startAddress + quantity - 1;
  if (endAddress > 65535 || endAddress < startAddress) {
    return { ok: false, startAddress, quantity, errors: ['MODBUS_ADDRESS_OVERFLOW'] };
  }

  const isCoilSpace = COIL_SPACES.has(input.registerSpace);
  const maxQuantity = isCoilSpace ? policy.maxCoilsPerRequest : policy.maxRegistersPerRequest;
  if (quantity > maxQuantity) {
    return { ok: false, startAddress, quantity, endAddress, errors: ['MODBUS_REQUEST_LIMIT_EXCEEDED'] };
  }

  if (!addressInRange(input.registerSpace, startAddress, endAddress, policy)) {
    return { ok: false, startAddress, quantity, endAddress, errors: ['MODBUS_ADDRESS_RANGE_NOT_ALLOWED'] };
  }

  return { ok: true, startAddress, quantity, endAddress, errors: [] };
}

export function validateModbusRequest(
  input: {
    target: string;
    port?: number;
    unitId: number | string;
    functionCode: number | string;
    registerSpace: ModbusRegisterSpace;
    startAddress: number | string;
    quantity: number | string;
    credentialRef?: string;
    username?: string;
    password?: string;
    token?: string;
  },
  policy: ModbusTcpReadOnlyPolicy,
): ModbusRequestValidation {
  const errors: string[] = [];

  const functionResult = validateModbusFunctionCode(input.functionCode, policy);
  if (!functionResult.ok || functionResult.functionCode === undefined) {
    errors.push(...functionResult.errors);
  }

  const unitResult = validateModbusUnitId(input.unitId, policy);
  if (!unitResult.ok) errors.push(...unitResult.errors);

  if (functionResult.functionCode !== undefined) {
    const addressResult = validateModbusAddressRange(
      {
        functionCode: functionResult.functionCode,
        registerSpace: input.registerSpace,
        startAddress: input.startAddress,
        quantity: input.quantity,
      },
      policy,
    );
    if (!addressResult.ok) errors.push(...addressResult.errors);
  }

  return {
    ok: errors.length === 0,
    functionCode: functionResult.functionCode,
    unitId: unitResult.unitId,
    startAddress: parseInteger(input.startAddress, 'startAddress') ?? undefined,
    quantity: parseInteger(input.quantity, 'quantity') ?? undefined,
    registerSpace: input.registerSpace,
    errors: [...new Set(errors)],
  };
}

export function decodeModbusRegisters(
  input: {
    registers: readonly number[];
    dataType: 'UInt16' | 'Int16' | 'UInt32' | 'Int32' | 'Float32' | 'Boolean' | 'RAW';
    byteOrder?: 'BIG_ENDIAN' | 'LITTLE_ENDIAN';
    wordOrder?: 'BIG_ENDIAN' | 'LITTLE_ENDIAN';
  },
  policy: ModbusTcpReadOnlyPolicy,
): { ok: boolean; values?: readonly number[] | readonly boolean[]; errors: string[] } {
  const byteOrder = input.byteOrder ?? policy.byteOrder;
  const wordOrder = input.wordOrder ?? policy.wordOrder;
  const errors: string[] = [];

  if (input.dataType === 'RAW') {
    return { ok: true, values: [...input.registers], errors: [] };
  }

  if (input.dataType === 'Boolean') {
    if (input.registers.length === 0) errors.push('MODBUS_DECODE_INVALID');
    return { ok: errors.length === 0, values: input.registers.map((r) => r !== 0), errors };
  }

  const registerCountRequired =
    input.dataType === 'UInt16' || input.dataType === 'Int16' ? 1 : 2;
  if (input.registers.length < registerCountRequired) {
    return { ok: false, errors: ['MODBUS_DECODE_INVALID'] };
  }

  const readRegisterBytes = (register: number): [number, number] => {
    const high = (register >> 8) & 0xff;
    const low = register & 0xff;
    return byteOrder === 'BIG_ENDIAN' ? [high, low] : [low, high];
  };

  const combineWords = (wordA: number, wordB: number): number => {
    const [aHigh, aLow] = readRegisterBytes(wordA);
    const [bHigh, bLow] = readRegisterBytes(wordB);
    const first = wordOrder === 'BIG_ENDIAN' ? [aHigh, aLow, bHigh, bLow] : [bHigh, bLow, aHigh, aLow];
    return ((first[0] << 24) | (first[1] << 16) | (first[2] << 8) | first[3]) >>> 0;
  };

  const values: number[] = [];
  if (input.dataType === 'UInt16' || input.dataType === 'Int16') {
    const [high, low] = readRegisterBytes(input.registers[0]);
    const raw = (high << 8) | low;
    values.push(input.dataType === 'Int16' ? ((raw << 16) >> 16) : raw);
  } else {
    const combined = combineWords(input.registers[0], input.registers[1]);
    if (input.dataType === 'UInt32') values.push(combined);
    else if (input.dataType === 'Int32') values.push(combined | 0);
    else {
      const buffer = Buffer.alloc(4);
      buffer.writeUInt32BE(combined, 0);
      values.push(buffer.readFloatBE(0));
    }
  }

  return { ok: true, values, errors: [] };
}
