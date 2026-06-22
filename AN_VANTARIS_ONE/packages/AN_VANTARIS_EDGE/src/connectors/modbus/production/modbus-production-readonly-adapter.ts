import { randomInt } from 'node:crypto';
import net from 'node:net';

import type {
  ModbusProductionAdapterConfig,
  ModbusProductionErrorCode,
  ModbusProductionReadFailure,
  ModbusProductionReadOnlyAdapter,
  ModbusProductionReadRequest,
  ModbusProductionReadResult,
  ModbusProductionResolvedTarget,
} from './modbus-production-adapter.types.js';
import {
  decodeAndNormalizeResponse,
  runFoundationRequestValidation,
  validateProductionAdapterConfig,
} from './modbus-production-response-normalizer.js';
import type { ModbusResponseFrame } from './modbus-production-response-normalizer.js';
import {
  createTargetHash,
  createTargetReferenceId,
  validateAllResolvedIps,
  validateProductionTarget,
} from './modbus-production-target-policy.js';

const IPV4_PATTERN = /^(?:\d{1,3}\.){3}\d{1,3}$/;

function failure(
  errorCode: ModbusProductionErrorCode,
  config: ModbusProductionAdapterConfig,
  target?: ModbusProductionResolvedTarget,
  extra?: Partial<ModbusProductionReadFailure>,
): ModbusProductionReadFailure {
  return {
    ok: false,
    errorCode,
    targetReferenceId: createTargetReferenceId(
      config.targetReferenceId,
      config.functionCode,
      config.startAddress,
    ),
    targetHash: target ? createTargetHash(target.hostname, target.port) : undefined,
    functionCode: config.functionCode,
    unitId: config.unitId,
    ...extra,
  };
}

function isIpAddress(hostname: string): boolean {
  return IPV4_PATTERN.test(hostname.trim()) || hostname.includes(':');
}

function resolveConnectHost(
  target: ModbusProductionResolvedTarget,
  request: ModbusProductionReadRequest,
): { ok: true; host: string } | { ok: false; errorCode: ModbusProductionErrorCode } {
  const { config, resolveDns, testMode = false } = request;
  const hostname = target.hostname.trim();

  if (isIpAddress(hostname)) {
    const ipError = validateAllResolvedIps([hostname], testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: hostname };
  }

  if (config.dnsMode === 'DENY' && !resolveDns) {
    return { ok: false, errorCode: 'MODBUS_DNS_NOT_ALLOWED' };
  }

  if (resolveDns) {
    const injected = resolveDns(hostname);
    if (!injected || injected.length === 0) return { ok: false, errorCode: 'MODBUS_DNS_RESULT_REJECTED' };
    const ipError = validateAllResolvedIps(injected, testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: injected[0] };
  }

  return { ok: false, errorCode: 'MODBUS_DNS_NOT_ALLOWED' };
}

function buildReadRequestFrame(
  transactionId: number,
  unitId: number,
  functionCode: number,
  startAddress: number,
  quantity: number,
): Buffer {
  const pdu = Buffer.alloc(5);
  pdu[0] = functionCode & 0xff;
  pdu.writeUInt16BE(startAddress, 1);
  pdu.writeUInt16BE(quantity, 3);
  const length = 1 + pdu.length;
  const frame = Buffer.alloc(6 + length);
  frame.writeUInt16BE(transactionId, 0);
  frame.writeUInt16BE(0, 2);
  frame.writeUInt16BE(length, 4);
  frame[6] = unitId & 0xff;
  pdu.copy(frame, 7);
  return frame;
}

function parseResponseFrame(
  buffer: Buffer,
  maxFrameBytes: number,
): { ok: true; frame: ModbusResponseFrame } | { ok: false; errorCode: ModbusProductionErrorCode } {
  if (buffer.length < 8) return { ok: false, errorCode: 'MODBUS_MBAP_INVALID' };
  if (buffer.length > maxFrameBytes) return { ok: false, errorCode: 'MODBUS_FRAME_SIZE_LIMIT_EXCEEDED' };

  const transactionId = buffer.readUInt16BE(0);
  const protocolId = buffer.readUInt16BE(2);
  const length = buffer.readUInt16BE(4);
  if (protocolId !== 0) return { ok: false, errorCode: 'MODBUS_MBAP_INVALID' };
  if (length < 2 || length > maxFrameBytes - 6) return { ok: false, errorCode: 'MODBUS_MBAP_INVALID' };
  if (buffer.length !== 6 + length) return { ok: false, errorCode: 'MODBUS_MBAP_INVALID' };

  const unitId = buffer[6];
  const pdu = buffer.subarray(7, 6 + length);
  if (pdu.length < 1) return { ok: false, errorCode: 'MODBUS_PDU_INVALID' };

  const functionCode = pdu[0];
  const isException = (functionCode & 0x80) !== 0;
  if (isException) {
    if (pdu.length < 2) return { ok: false, errorCode: 'MODBUS_PDU_INVALID' };
    return {
      ok: true,
      frame: {
        transactionId,
        protocolId,
        unitId,
        functionCode,
        exceptionCode: pdu[1],
        payload: [],
      },
    };
  }

  if (pdu.length < 2) return { ok: false, errorCode: 'MODBUS_PDU_INVALID' };
  const byteCount = pdu[1];
  const payload = pdu.subarray(2, 2 + byteCount);
  if (payload.length !== byteCount) return { ok: false, errorCode: 'MODBUS_PDU_INVALID' };

  return {
    ok: true,
    frame: {
      transactionId,
      protocolId,
      unitId,
      functionCode,
      byteCount,
      payload: [...payload],
    },
  };
}

async function readFullResponse(socket: net.Socket, config: ModbusProductionAdapterConfig): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    const timer = setTimeout(() => {
      cleanup();
      socket.destroy();
      reject(new Error('MODBUS_RESPONSE_TIMEOUT'));
    }, config.responseTimeoutMs);

    const cleanup = () => {
      clearTimeout(timer);
      socket.removeListener('data', onData);
      socket.removeListener('end', onEnd);
      socket.removeListener('error', onError);
    };

    const onData = (chunk: Buffer) => {
      chunks.push(chunk);
    };

    const onEnd = () => {
      cleanup();
      resolve(Buffer.concat(chunks));
    };

    const onError = (error: Error) => {
      cleanup();
      reject(error);
    };

    socket.on('data', onData);
    socket.on('end', onEnd);
    socket.on('error', onError);
  });
}

async function executeControlledRead(request: ModbusProductionReadRequest): Promise<ModbusProductionReadResult> {
  const { config, resolveTarget, testMode = false } = request;
  const configError = validateProductionAdapterConfig(config);
  if (configError) return failure(configError, config);

  const target = resolveTarget(config.targetReferenceId);
  if (!target) return failure('MODBUS_TARGET_REFERENCE_NOT_FOUND', config);

  const connectHostPreview = resolveConnectHost(target, request);
  if (!connectHostPreview.ok && connectHostPreview.errorCode === 'MODBUS_DNS_NOT_ALLOWED') {
    return failure(connectHostPreview.errorCode, config, target);
  }
  if (!connectHostPreview.ok && connectHostPreview.errorCode === 'MODBUS_DNS_RESULT_REJECTED') {
    return failure(connectHostPreview.errorCode, config, target);
  }
  if (!connectHostPreview.ok && connectHostPreview.errorCode === 'MODBUS_METADATA_TARGET_REJECTED') {
    return failure(connectHostPreview.errorCode, config, target);
  }

  const targetError = validateProductionTarget(target, config, testMode);
  if (targetError) return failure(targetError, config, target);

  const connectHost = resolveConnectHost(target, request);
  if (!connectHost.ok) return failure(connectHost.errorCode, config, target);

  const foundationError = runFoundationRequestValidation(target, config, testMode);
  if (foundationError) return failure(foundationError, config, target);

  const transactionId = randomInt(1, 65536);
  const requestFrame = buildReadRequestFrame(
    transactionId,
    config.unitId,
    config.functionCode,
    config.startAddress,
    config.quantity,
  );

  if (requestFrame.length > config.maxFrameBytes) {
    return failure('MODBUS_FRAME_SIZE_LIMIT_EXCEEDED', config, target);
  }

  const overallDeadline = config.maxProcessingMilliseconds;
  const startedAt = Date.now();

  return new Promise((resolve) => {
    const socket = net.createConnection(
      { host: connectHost.host, port: target.port },
      async () => {
        try {
          if (Date.now() - startedAt > overallDeadline) {
            socket.destroy();
            resolve(failure('MODBUS_RESPONSE_TIMEOUT', config, target));
            return;
          }
          const responsePromise = readFullResponse(socket, config);
          socket.write(requestFrame);
          const full = await responsePromise;
          if (full.length < 8) {
            socket.destroy();
            resolve(failure('MODBUS_MBAP_INVALID', config, target));
            return;
          }
          const response = parseResponseFrame(full, config.maxFrameBytes);
          socket.end();
          socket.destroy();

          if (!response.ok) {
            resolve(failure(response.errorCode, config, target));
            return;
          }

          if (response.frame.transactionId !== transactionId) {
            resolve(failure('MODBUS_TRANSACTION_MISMATCH', config, target));
            return;
          }
          if (response.frame.unitId !== config.unitId) {
            resolve(failure('MODBUS_UNIT_ID_MISMATCH', config, target));
            return;
          }
          if ((response.frame.functionCode & 0x7f) !== config.functionCode) {
            resolve(failure('MODBUS_FUNCTION_MISMATCH', config, target));
            return;
          }
          if ((response.frame.functionCode & 0x80) !== 0) {
            resolve(failure('MODBUS_EXCEPTION_RESPONSE', config, target));
            return;
          }

          const normalized = decodeAndNormalizeResponse(response.frame, target, config, testMode);
          if (!normalized.ok) {
            resolve(failure(normalized.errorCode, config, target));
            return;
          }

          resolve({
            ok: true,
            targetReferenceId: createTargetReferenceId(
              config.targetReferenceId,
              config.functionCode,
              config.startAddress,
            ),
            targetHash: createTargetHash(target.hostname, target.port),
            functionCode: config.functionCode,
            unitId: config.unitId,
            recordCount: normalized.records.length,
            records: normalized.records,
            foundationAccepted: true,
          });
        } catch (error) {
          socket.destroy();
          const message = error instanceof Error ? error.message : 'MODBUS_REQUEST_FAILED';
          if (message === 'MODBUS_RESPONSE_TIMEOUT') {
            resolve(failure('MODBUS_RESPONSE_TIMEOUT', config, target));
            return;
          }
          if (message === 'MODBUS_MBAP_INVALID') {
            resolve(failure('MODBUS_MBAP_INVALID', config, target));
            return;
          }
          resolve(failure('MODBUS_REQUEST_FAILED', config, target));
        }
      },
    );

    socket.setTimeout(config.connectTimeoutMs, () => {
      socket.destroy();
      resolve(failure('MODBUS_CONNECT_TIMEOUT', config, target));
    });

    socket.on('error', () => {
      socket.destroy();
      resolve(failure('MODBUS_REQUEST_FAILED', config, target));
    });
  });
}

export function createModbusProductionReadOnlyAdapter(): ModbusProductionReadOnlyAdapter {
  return {
    readOnce: async (request: ModbusProductionReadRequest): Promise<ModbusProductionReadResult> =>
      executeControlledRead(request),
  };
}

export const modbusProductionReadOnlyAdapter: ModbusProductionReadOnlyAdapter =
  createModbusProductionReadOnlyAdapter();
