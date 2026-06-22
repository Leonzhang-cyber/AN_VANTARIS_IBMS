import { randomInt } from 'node:crypto';
import dgram from 'node:dgram';

import type {
  BacnetProductionAdapterConfig,
  BacnetProductionDiscoverRequest,
  BacnetProductionErrorCode,
  BacnetProductionNormalizedRecord,
  BacnetProductionReadFailure,
  BacnetProductionReadOnlyAdapter,
  BacnetProductionReadRequest,
  BacnetProductionReadResult,
  BacnetProductionResolvedTarget,
} from './bacnet-production-adapter.types.js';
import type { BacnetObjectType, BacnetPropertyId } from '../bacnet-readonly-types.js';
import {
  decodeAndNormalizeResponse,
  runFoundationRequestValidation,
  validateProductionAdapterConfig,
  validateProductionService,
} from './bacnet-production-response-normalizer.js';
import type { BacnetPropertyResult, BacnetResponsePayload } from './bacnet-production-response-normalizer.js';
import {
  createTargetHash,
  createTargetReferenceId,
  validateAllResolvedIps,
  validateProductionTarget,
} from './bacnet-production-target-policy.js';

const REQUEST_MAGIC = Buffer.from([0x42, 0x41, 0x43, 0x4e]);
const RESPONSE_MAGIC = Buffer.from([0x42, 0x41, 0x43, 0x52]);
const BVLC_TYPE_BACNET_IP = 0x81;
const BVLC_FUNCTION_ORIGINAL_UNICAST_NPDU = 0x0a;
const NPDU_VERSION = 1;
const SVC_READ_PROPERTY = 1;
const SVC_READ_PROPERTY_MULTIPLE = 2;
const SVC_WHO_IS = 3;
const ERR_OK = 0;
const ERR_ERROR = 1;
const ERR_REJECT = 2;
const ERR_ABORT = 3;

const IPV4_PATTERN = /^(?:\d{1,3}\.){3}\d{1,3}$/;

type DecodedPacket = BacnetResponsePayload & {
  results: BacnetPropertyResult[];
};

function failure(
  errorCode: BacnetProductionErrorCode,
  config: BacnetProductionAdapterConfig,
  target?: BacnetProductionResolvedTarget,
  extra?: Partial<BacnetProductionReadFailure>,
): BacnetProductionReadFailure {
  return {
    ok: false,
    errorCode,
    targetReferenceId: createTargetReferenceId(
      config.targetReferenceId,
      config.service,
      String(config.reads[0]?.objectType ?? 'DEVICE'),
    ),
    targetHash: target ? createTargetHash(target.hostname, target.port) : undefined,
    service: config.service,
    ...extra,
  };
}

function isIpAddress(hostname: string): boolean {
  return IPV4_PATTERN.test(hostname.trim()) || hostname.includes(':');
}

function serviceCode(service: string): number {
  switch (service.toUpperCase()) {
    case 'READ_PROPERTY': return SVC_READ_PROPERTY;
    case 'READ_PROPERTY_MULTIPLE': return SVC_READ_PROPERTY_MULTIPLE;
    case 'WHO_IS': return SVC_WHO_IS;
    default: return 0;
  }
}

function writeString(buffer: Buffer, offset: number, value: string): number {
  const bytes = Buffer.from(value, 'utf8');
  if (bytes.length > 255) throw new Error('BACNET_APDU_INVALID');
  buffer[offset] = bytes.length;
  bytes.copy(buffer, offset + 1);
  return 1 + bytes.length;
}

function readString(buffer: Buffer, offset: number): { value: string; next: number } {
  const len = buffer[offset];
  const value = buffer.subarray(offset + 1, offset + 1 + len).toString('utf8');
  return { value, next: offset + 1 + len };
}

export function encodeRequestPacket(input: {
  invokeId: number;
  service: string;
  deviceInstance: number;
  reads: BacnetProductionAdapterConfig['reads'];
  discoveryLow?: number;
  discoveryHigh?: number;
}): Buffer {
  let payloadSize = 1 + 1 + 1 + 1 + 4 + 2 + 4 + 4;
  for (const read of input.reads) {
    payloadSize += 1 + Buffer.byteLength(String(read.objectType), 'utf8');
    payloadSize += 4 + 1 + Buffer.byteLength(String(read.propertyIdentifier), 'utf8') + 1 + 4;
  }
  const total = 10 + payloadSize;
  const buffer = Buffer.alloc(total);
  let offset = 0;
  REQUEST_MAGIC.copy(buffer, offset); offset += 4;
  buffer.writeUInt16BE(BVLC_TYPE_BACNET_IP, offset); offset += 2;
  buffer.writeUInt16BE(BVLC_FUNCTION_ORIGINAL_UNICAST_NPDU, offset); offset += 2;
  buffer.writeUInt16BE(payloadSize, offset); offset += 2;
  buffer[offset++] = NPDU_VERSION;
  buffer[offset++] = 0;
  buffer[offset++] = input.invokeId & 0xff;
  buffer[offset++] = serviceCode(input.service);
  buffer.writeUInt32BE(input.deviceInstance, offset); offset += 4;
  buffer.writeUInt16BE(input.reads.length, offset); offset += 2;
  buffer.writeUInt32BE(input.discoveryLow ?? 0, offset); offset += 4;
  buffer.writeUInt32BE(input.discoveryHigh ?? 4194303, offset); offset += 4;
  for (const read of input.reads) {
    offset += writeString(buffer, offset, String(read.objectType));
    buffer.writeUInt32BE(read.objectInstance, offset); offset += 4;
    offset += writeString(buffer, offset, String(read.propertyIdentifier));
    buffer[offset++] = read.arrayIndex === undefined ? 0 : 1;
    buffer.writeUInt32BE(read.arrayIndex ?? 0, offset); offset += 4;
  }
  if (offset !== total) throw new Error('BACNET_TEST_ENCODER_SIZE_MISMATCH');
  return buffer;
}

export function decodeResponsePacket(buffer: Buffer, maxResponseBytes: number): DecodedPacket {
  if (buffer.length < 21) throw new Error('BACNET_BVLC_INVALID');
  if (buffer.length > maxResponseBytes) throw new Error('BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED');
  if (!buffer.subarray(0, 4).equals(RESPONSE_MAGIC)) throw new Error('BACNET_BVLC_INVALID');
  if (buffer.readUInt16BE(4) !== BVLC_TYPE_BACNET_IP) throw new Error('BACNET_BVLC_INVALID');
  if (buffer.readUInt16BE(6) !== BVLC_FUNCTION_ORIGINAL_UNICAST_NPDU) throw new Error('BACNET_BVLC_INVALID');
  const length = buffer.readUInt16BE(8);
  if (length + 10 !== buffer.length) throw new Error('BACNET_BVLC_INVALID');
  if (buffer[10] !== NPDU_VERSION) throw new Error('BACNET_NPDU_INVALID');
  if ((buffer[11] & 0x20) !== 0) throw new Error('BACNET_NPDU_INVALID');
  const invokeId = buffer[12];
  const serviceNum = buffer[13];
  const service =
    serviceNum === SVC_READ_PROPERTY
      ? 'READ_PROPERTY'
      : serviceNum === SVC_READ_PROPERTY_MULTIPLE
        ? 'READ_PROPERTY_MULTIPLE'
        : serviceNum === SVC_WHO_IS
          ? 'I_AM'
          : 'UNKNOWN';
  const deviceInstance = buffer.readUInt32BE(14);
  const errorClassNum = buffer.readUInt8(18);
  const errorClass =
    errorClassNum === ERR_OK ? undefined : errorClassNum === ERR_ERROR ? 'ERROR' : errorClassNum === ERR_REJECT ? 'REJECT' : 'ABORT';
  const resultCount = buffer.readUInt16BE(19);
  let offset = 21;
  const results: BacnetPropertyResult[] = [];
  for (let i = 0; i < resultCount; i += 1) {
    const objectTypeRead = readString(buffer, offset);
    offset = objectTypeRead.next;
    const objectInstance = buffer.readUInt32BE(offset); offset += 4;
    const propertyRead = readString(buffer, offset);
    offset = propertyRead.next;
    const hasArrayIndex = buffer[offset++] === 1;
    const arrayIndex = hasArrayIndex ? buffer.readUInt32BE(offset) : undefined;
    if (hasArrayIndex) offset += 4;
    const valueTypeRead = readString(buffer, offset);
    offset = valueTypeRead.next;
    const valueLen = buffer.readUInt16BE(offset); offset += 2;
    if (offset + valueLen > buffer.length) throw new Error('BACNET_APDU_INVALID');
    const valueRaw = buffer.subarray(offset, offset + valueLen).toString('utf8'); offset += valueLen;
    let value: unknown = valueRaw;
    const vt = valueTypeRead.value.toUpperCase();
    if (vt === 'NULL') value = null;
    else if (vt === 'BOOLEAN') value = valueRaw === 'true';
    else if (vt === 'UNSIGNED' || vt === 'SIGNED' || vt === 'REAL' || vt === 'DOUBLE' || vt === 'ENUMERATED') {
      value = Number(valueRaw);
      if (!Number.isFinite(value as number)) throw new Error('BACNET_DECODE_FAILED');
    }
    results.push({
      objectType: objectTypeRead.value as BacnetObjectType,
      objectInstance,
      propertyId: propertyRead.value,
      arrayIndex,
      valueType: valueTypeRead.value,
      value,
    });
  }
  if (offset !== buffer.length) throw new Error('BACNET_APDU_INVALID');
  return {
    invokeId,
    service,
    deviceInstance,
    errorClass,
    segmented: false,
    results,
    responseBytes: buffer.length,
    apduBytes: buffer.length - 10,
  };
}

function resolveConnectHost(
  target: BacnetProductionResolvedTarget,
  request: BacnetProductionReadRequest,
): { ok: true; host: string } | { ok: false; errorCode: BacnetProductionErrorCode } {
  const { config, resolveDns, testMode = false } = request;
  const hostname = target.hostname.trim();
  if (isIpAddress(hostname)) {
    const ipError = validateAllResolvedIps([hostname], testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: hostname };
  }
  if (config.dnsMode === 'DENY' && !resolveDns) return { ok: false, errorCode: 'BACNET_DNS_NOT_ALLOWED' };
  if (resolveDns) {
    const injected = resolveDns(hostname);
    if (!injected || injected.length === 0) return { ok: false, errorCode: 'BACNET_DNS_RESULT_REJECTED' };
    const ipError = validateAllResolvedIps(injected, testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: injected[0] };
  }
  return { ok: false, errorCode: 'BACNET_DNS_NOT_ALLOWED' };
}

async function sendUdpRequest(host: string, port: number, payload: Buffer, config: BacnetProductionAdapterConfig): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const socket = dgram.createSocket('udp4');
    const timer = setTimeout(() => {
      socket.close();
      reject(new Error('BACNET_RESPONSE_TIMEOUT'));
    }, config.responseTimeoutMs);
    socket.once('message', (message) => {
      clearTimeout(timer);
      socket.close();
      resolve(message);
    });
    socket.once('error', (error) => {
      clearTimeout(timer);
      socket.close();
      reject(error);
    });
    socket.send(payload, port, host, (error) => {
      if (error) {
        clearTimeout(timer);
        socket.close();
        reject(error);
      }
    });
  });
}

async function executeControlledRead(
  request: BacnetProductionReadRequest | BacnetProductionDiscoverRequest,
  serviceOverride?: BacnetProductionAdapterConfig['service'] | 'WHO_IS',
): Promise<BacnetProductionReadResult> {
  const { config, resolveTarget, resolveObjectAllowlist, resolvePropertyAllowlist, testMode = false } = request;
  const wireService = serviceOverride ?? config.service;
  const configError = validateProductionAdapterConfig(config);
  if (configError) return failure(configError, config);

  const target = resolveTarget(config.targetReferenceId);
  if (!target) return failure('BACNET_TARGET_REFERENCE_NOT_FOUND', config);

  const connectPreview = resolveConnectHost(target, request);
  if (
    !connectPreview.ok &&
    ['BACNET_DNS_NOT_ALLOWED', 'BACNET_DNS_RESULT_REJECTED', 'BACNET_METADATA_TARGET_REJECTED'].includes(connectPreview.errorCode)
  ) {
    return failure(connectPreview.errorCode, config, target);
  }

  const targetError = validateProductionTarget(target, config, testMode);
  if (targetError) return failure(targetError, config, target);

  const objectTypes = resolveObjectAllowlist(config.objectReferenceId);
  const properties = resolvePropertyAllowlist(config.propertyReferenceId);
  if (!objectTypes?.length || !properties?.length) {
    return failure('BACNET_OBJECT_NOT_ALLOWLISTED', config, target);
  }

  const foundationError = runFoundationRequestValidation(target, config, objectTypes, properties, testMode);
  if (foundationError) return failure(foundationError, config, target);

  const connectHost = resolveConnectHost(target, request);
  if (!connectHost.ok) return failure(connectHost.errorCode, config, target);

  const invokeId = randomInt(0, 256);
  const discoveryLow = 'discoveryDeviceInstanceLow' in request ? request.discoveryDeviceInstanceLow : undefined;
  const discoveryHigh = 'discoveryDeviceInstanceHigh' in request ? request.discoveryDeviceInstanceHigh : undefined;
  let packet: Buffer;
  try {
    packet = encodeRequestPacket({
      invokeId,
      service: wireService,
      deviceInstance: config.deviceInstance,
      reads: config.reads,
      discoveryLow,
      discoveryHigh,
    });
  } catch {
    return failure('BACNET_APDU_INVALID', config, target);
  }
  if (packet.length > config.maxApduBytes) return failure('BACNET_PROPERTY_LIMIT_EXCEEDED', config, target);

  try {
    const responseBuffer = await sendUdpRequest(connectHost.host, target.port, packet, config);
    let decoded: DecodedPacket;
    try {
      decoded = decodeResponsePacket(responseBuffer, config.maxResponseBytes);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'BACNET_BVLC_INVALID';
      if (message === 'BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED') return failure('BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED', config, target);
      if (message === 'BACNET_DECODE_FAILED') return failure('BACNET_DECODE_FAILED', config, target);
      if (message.includes('NPDU')) return failure('BACNET_NPDU_INVALID', config, target);
      if (message.includes('APDU')) return failure('BACNET_APDU_INVALID', config, target);
      return failure('BACNET_BVLC_INVALID', config, target);
    }

    if (decoded.invokeId !== invokeId) return failure('BACNET_INVOKE_ID_MISMATCH', config, target);
    if (wireService !== 'WHO_IS' && decoded.service !== wireService) {
      return failure('BACNET_SERVICE_MISMATCH', config, target);
    }
    if (wireService === 'WHO_IS' && decoded.service !== 'I_AM' && decoded.service !== 'WHO_IS') {
      return failure('BACNET_SERVICE_MISMATCH', config, target);
    }
    if (decoded.errorClass === 'ERROR') return failure('BACNET_ERROR_RESPONSE', config, target);
    if (decoded.errorClass === 'REJECT' || decoded.errorClass === 'ABORT') {
      return failure('BACNET_ABORT_REJECT_RESPONSE', config, target);
    }
    if (decoded.segmented) return failure('BACNET_SEGMENTATION_NOT_ALLOWED', config, target);

    const normalized = decodeAndNormalizeResponse(
      decoded,
      target,
      config,
      objectTypes,
      properties,
      testMode,
      wireService,
    );
    if (!normalized.ok) return failure(normalized.errorCode, config, target);

    return {
      ok: true,
      targetReferenceId: createTargetReferenceId(config.targetReferenceId, wireService, String(config.reads[0]?.objectType ?? 'DEVICE')),
      targetHash: createTargetHash(target.hostname, target.port),
      service: wireService,
      recordCount: normalized.records.length,
      records: normalized.records,
      foundationAccepted: true,
    };
  } catch {
    return failure('BACNET_REQUEST_FAILED', config, target);
  }
}

export function createBacnetProductionReadOnlyAdapter(): BacnetProductionReadOnlyAdapter {
  return {
    readPropertyOnce: async (request) => {
      if (request.config.service !== 'READ_PROPERTY') {
        return failure('BACNET_SERVICE_NOT_ALLOWED', { ...request.config, service: 'READ_PROPERTY' });
      }
      return executeControlledRead(request, 'READ_PROPERTY');
    },
    readPropertyMultipleOnce: async (request) => {
      if (request.config.service !== 'READ_PROPERTY_MULTIPLE') {
        return failure('BACNET_SERVICE_NOT_ALLOWED', { ...request.config, service: 'READ_PROPERTY_MULTIPLE' });
      }
      if (request.config.reads.length > request.config.maxProperties) {
        return failure('BACNET_PROPERTY_LIMIT_EXCEEDED', request.config);
      }
      return executeControlledRead(request, 'READ_PROPERTY_MULTIPLE');
    },
    discoverOnce: async (request: BacnetProductionDiscoverRequest) => {
      const { config, testMode = false } = request;
      if (!testMode || config.broadcastMode !== 'TEST_DISCOVERY_ONLY' || config.udpMode !== 'LOOPBACK_TEST') {
        return failure('BACNET_BROADCAST_NOT_ALLOWED', config);
      }
      const discoveryConfig: BacnetProductionAdapterConfig = {
        ...config,
        service: 'READ_PROPERTY',
        reads: [{ objectType: 'DEVICE', objectInstance: request.discoveryDeviceInstanceLow, propertyIdentifier: 'OBJECT_NAME' }],
      };
      return executeControlledRead({ ...request, config: discoveryConfig }, 'WHO_IS');
    },
  };
}

export const bacnetProductionReadOnlyAdapter: BacnetProductionReadOnlyAdapter = createBacnetProductionReadOnlyAdapter();
