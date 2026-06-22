import type {
  ModbusResponseFrame,
  ModbusResponseValidation,
  ModbusTcpReadOnlyPolicy,
} from './modbus-readonly-types.js';

const MODELED_EXCEPTION_CODES = new Set([1, 2, 3, 4, 6, 0x10, 0x11]);

export function calculateModbusResponseBytes(frame: ModbusResponseFrame): number {
  const payload = frame.payload ?? [];
  const raw = frame.rawBytes ?? [];
  return Math.max(raw.length, 7 + payload.length + (frame.exceptionCode !== undefined ? 1 : 0));
}

export function validateModbusResponse(
  request: {
    readonly transactionId: number;
    readonly unitId: number;
    readonly functionCode: number;
    readonly quantity: number;
  },
  frame: ModbusResponseFrame,
  policy: ModbusTcpReadOnlyPolicy,
): ModbusResponseValidation {
  const errors: string[] = [];

  if (!Number.isInteger(frame.transactionId) || frame.transactionId < 0 || frame.transactionId > 65535) {
    errors.push('MODBUS_RESPONSE_MALFORMED');
  } else if (frame.transactionId !== request.transactionId) {
    errors.push('MODBUS_TRANSACTION_ID_MISMATCH');
  }

  if (frame.protocolId !== 0) {
    errors.push('MODBUS_PROTOCOL_ID_INVALID');
  }

  if (frame.unitId !== request.unitId) {
    errors.push('MODBUS_UNIT_ID_MISMATCH');
  }

  const isException = (frame.functionCode & 0x80) !== 0;
  const baseFunctionCode = isException ? frame.functionCode & 0x7f : frame.functionCode;

  if (baseFunctionCode !== request.functionCode) {
    errors.push('MODBUS_FUNCTION_MISMATCH');
  }

  if (isException) {
    if (frame.exceptionCode === undefined || !MODELED_EXCEPTION_CODES.has(frame.exceptionCode)) {
      errors.push('MODBUS_RESPONSE_MALFORMED');
    } else {
      errors.push('MODBUS_EXCEPTION_RESPONSE');
    }
    return { ok: false, frame, errors: [...new Set(errors)] };
  }

  if (frame.functionCode !== request.functionCode) {
    errors.push('MODBUS_FUNCTION_MISMATCH');
  }

  const payload = frame.payload ?? [];
  const responseBytes = calculateModbusResponseBytes(frame);
  if (responseBytes > policy.maxResponseBytes) {
    errors.push('MODBUS_RESPONSE_TOO_LARGE');
  }

  if (frame.byteCount === undefined) {
    errors.push('MODBUS_RESPONSE_MALFORMED');
  } else if (frame.byteCount !== payload.length) {
    errors.push('MODBUS_BYTE_COUNT_MISMATCH');
  }

  if (payload.length === 0 && request.quantity > 0) {
    errors.push('MODBUS_RESPONSE_MALFORMED');
  }

  const expectedRegisterBytes = request.functionCode === 3 || request.functionCode === 4 ? request.quantity * 2 : null;
  const expectedCoilBytes =
    request.functionCode === 1 || request.functionCode === 2 ? Math.ceil(request.quantity / 8) : null;
  const expected = expectedRegisterBytes ?? expectedCoilBytes;
  if (expected !== null && frame.byteCount !== undefined && frame.byteCount !== expected) {
    errors.push('MODBUS_BYTE_COUNT_MISMATCH');
  }

  if (frame.rawBytes && frame.rawBytes.length > 0) {
    const minimumLength = 7 + (frame.byteCount ?? 0);
    if (frame.rawBytes.length < minimumLength) {
      errors.push('MODBUS_RESPONSE_MALFORMED');
    }
    if (frame.rawBytes.length > minimumLength) {
      errors.push('MODBUS_RESPONSE_MALFORMED');
    }
  }

  return { ok: errors.length === 0, frame, errors: [...new Set(errors)] };
}
