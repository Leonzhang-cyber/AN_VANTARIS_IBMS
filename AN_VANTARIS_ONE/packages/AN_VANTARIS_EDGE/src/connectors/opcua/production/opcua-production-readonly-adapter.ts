import { randomInt } from 'node:crypto';
import net from 'node:net';

import type {
  OpcuaProductionAdapterConfig,
  OpcuaProductionErrorCode,
  OpcuaProductionReadFailure,
  OpcuaProductionReadOnlyAdapter,
  OpcuaProductionReadRequest,
  OpcuaProductionReadResult,
  OpcuaProductionResolvedEndpoint,
} from './opcua-production-adapter.types.js';
import type { OpcUaReadResult } from '../opcua-readonly-types.js';
import {
  decodeAndNormalizeResponse,
  runFoundationRequestValidation,
  validateProductionAdapterConfig,
  validateProductionService,
} from './opcua-production-response-normalizer.js';
import type { OpcUaResponsePayload } from './opcua-production-response-normalizer.js';
import {
  createEndpointHash,
  createEndpointReferenceId,
  validateAllResolvedIps,
  validateProductionEndpoint,
} from './opcua-production-target-policy.js';

const REQUEST_MAGIC = Buffer.from([0x4f, 0x50, 0x43, 0x51]);
const RESPONSE_MAGIC = Buffer.from([0x4f, 0x50, 0x43, 0x52]);
const PROTOCOL_VERSION = 1;
const SVC_READ = 1;
const SVC_BROWSE = 2;
const SVC_HEALTH_PROBE = 3;
const STATUS_OK = 0;
const STATUS_ERROR = 1;
const STATUS_BAD = 2;

const IPV4_PATTERN = /^(?:\d{1,3}\.){3}\d{1,3}$/;

type DecodedResponse = OpcUaResponsePayload & { results: OpcUaReadResult[]; responseStatus: number };

function failure(
  errorCode: OpcuaProductionErrorCode,
  config: OpcuaProductionAdapterConfig,
  endpoint?: OpcuaProductionResolvedEndpoint,
  extra?: Partial<OpcuaProductionReadFailure>,
): OpcuaProductionReadFailure {
  return {
    ok: false,
    errorCode,
    endpointReferenceId: createEndpointReferenceId(
      config.endpointReferenceId,
      config.service,
      config.reads[0]?.nodeId ?? 'ns=0;i=0',
    ),
    endpointHash: endpoint ? createEndpointHash(endpoint.hostname, endpoint.port) : undefined,
    service: config.service,
    ...extra,
  };
}

function isIpAddress(hostname: string): boolean {
  return IPV4_PATTERN.test(hostname.trim()) || hostname.includes(':');
}

function serviceCode(service: string): number {
  switch (service.toUpperCase()) {
    case 'READ': return SVC_READ;
    case 'BROWSE': return SVC_BROWSE;
    case 'HEALTH_PROBE': return SVC_HEALTH_PROBE;
    default: return 0;
  }
}

function serviceName(code: number): string {
  if (code === SVC_READ) return 'READ';
  if (code === SVC_BROWSE) return 'BROWSE';
  if (code === SVC_HEALTH_PROBE) return 'HEALTH_PROBE';
  return 'UNKNOWN';
}

function writeString(buffer: Buffer, offset: number, value: string, maxLen: number): number {
  const bytes = Buffer.from(value, 'utf8');
  if (bytes.length > maxLen || bytes.length > 255) throw new Error('OPCUA_REQUEST_FRAME_INVALID');
  buffer[offset] = bytes.length;
  bytes.copy(buffer, offset + 1);
  return 1 + bytes.length;
}

function readString(buffer: Buffer, offset: number, maxLen: number): { value: string; next: number } {
  const len = buffer[offset];
  if (len > maxLen) throw new Error('OPCUA_RESPONSE_FRAME_INVALID');
  const value = buffer.subarray(offset + 1, offset + 1 + len).toString('utf8');
  return { value, next: offset + 1 + len };
}

export function encodeRequestPacket(input: {
  requestId: number;
  service: string;
  endpointHash: string;
  reads: OpcuaProductionAdapterConfig['reads'];
  maxNodeIdLength: number;
}): Buffer {
  let payloadSize = 1 + 1 + 4 + 1 + Buffer.byteLength(input.endpointHash, 'utf8') + 2;
  for (const read of input.reads) {
    payloadSize += 1 + Buffer.byteLength(read.nodeId, 'utf8');
    payloadSize += 1 + Buffer.byteLength(read.attributeId, 'utf8');
  }
  const total = 4 + payloadSize;
  const buffer = Buffer.alloc(total);
  let offset = 0;
  REQUEST_MAGIC.copy(buffer, offset); offset += 4;
  buffer[offset++] = PROTOCOL_VERSION;
  buffer[offset++] = serviceCode(input.service);
  buffer.writeUInt32BE(input.requestId, offset); offset += 4;
  offset += writeString(buffer, offset, input.endpointHash, 64);
  buffer.writeUInt16BE(input.reads.length, offset); offset += 2;
  for (const read of input.reads) {
    offset += writeString(buffer, offset, read.nodeId, input.maxNodeIdLength);
    offset += writeString(buffer, offset, read.attributeId, 64);
  }
  if (offset !== total) throw new Error('OPCUA_TEST_ENCODER_SIZE_MISMATCH');
  return buffer;
}

export function decodeResponsePacket(buffer: Buffer, maxResponseBytes: number, maxNodeIdLength: number, maxValueBytes: number): DecodedResponse {
  if (buffer.length < 13) throw new Error('OPCUA_RESPONSE_MAGIC_INVALID');
  if (buffer.length > maxResponseBytes) throw new Error('OPCUA_RESPONSE_SIZE_LIMIT_EXCEEDED');
  if (!buffer.subarray(0, 4).equals(RESPONSE_MAGIC)) throw new Error('OPCUA_RESPONSE_MAGIC_INVALID');
  if (buffer[4] !== PROTOCOL_VERSION) throw new Error('OPCUA_RESPONSE_FRAME_INVALID');
  const serviceNum = buffer[5];
  const requestId = buffer.readUInt32BE(6);
  const responseStatus = buffer[10];
  const resultCount = buffer.readUInt16BE(11);
  let offset = 13;
  const results: OpcUaReadResult[] = [];
  for (let i = 0; i < resultCount; i += 1) {
    const nodeRead = readString(buffer, offset, maxNodeIdLength); offset = nodeRead.next;
    const attrRead = readString(buffer, offset, 64); offset = attrRead.next;
    const statusRead = readString(buffer, offset, 64); offset = statusRead.next;
    const typeRead = readString(buffer, offset, 64); offset = typeRead.next;
    const valueLen = buffer.readUInt16BE(offset); offset += 2;
    if (valueLen > maxValueBytes || offset + valueLen > buffer.length) throw new Error('OPCUA_RESPONSE_FRAME_INVALID');
    const valueRaw = buffer.subarray(offset, offset + valueLen).toString('utf8'); offset += valueLen;
    let value: unknown = valueRaw;
    const vt = typeRead.value.toUpperCase();
    if (vt === 'NULL') value = null;
    else if (vt === 'BOOLEAN') value = valueRaw === 'true';
    else if (vt === 'INT32' || vt === 'UINT32') {
      value = Number(valueRaw);
      if (!Number.isFinite(value as number)) throw new Error('OPCUA_DECODE_FAILED');
    } else if (vt === 'DOUBLE') {
      value = Number(valueRaw);
      if (!Number.isFinite(value as number)) throw new Error('OPCUA_DECODE_FAILED');
    }
    const hasSource = buffer[offset++] === 1;
    let sourceTimestamp: string | undefined;
    if (hasSource) {
      const ts = readString(buffer, offset, 64); offset = ts.next;
      sourceTimestamp = ts.value;
    }
    const hasServer = buffer[offset++] === 1;
    let serverTimestamp: string | undefined;
    if (hasServer) {
      const ts = readString(buffer, offset, 64); offset = ts.next;
      serverTimestamp = ts.value;
    }
    results.push({
      nodeId: nodeRead.value,
      attributeId: attrRead.value,
      statusCode: statusRead.value,
      valueType: typeRead.value,
      value,
      sourceTimestamp,
      serverTimestamp,
    });
  }
  if (offset !== buffer.length) throw new Error('OPCUA_RESPONSE_FRAME_INVALID');
  return {
    requestHandle: requestId,
    service: serviceName(serviceNum),
    responseStatus,
    results,
    responseBytes: buffer.length,
  };
}

function resolveConnectHost(
  endpoint: OpcuaProductionResolvedEndpoint,
  request: OpcuaProductionReadRequest,
): { ok: true; host: string } | { ok: false; errorCode: OpcuaProductionErrorCode } {
  const { config, resolveDns, testMode = false } = request;
  const hostname = endpoint.hostname.trim();
  if (isIpAddress(hostname)) {
    const ipError = validateAllResolvedIps([hostname], testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: hostname };
  }
  if (config.dnsMode === 'DENY' && !resolveDns) return { ok: false, errorCode: 'OPCUA_DNS_NOT_ALLOWED' };
  if (resolveDns) {
    const injected = resolveDns(hostname);
    if (!injected || injected.length === 0) return { ok: false, errorCode: 'OPCUA_DNS_RESULT_REJECTED' };
    const ipError = validateAllResolvedIps(injected, testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: injected[0] };
  }
  return { ok: false, errorCode: 'OPCUA_DNS_NOT_ALLOWED' };
}

async function readFullResponse(socket: net.Socket, config: OpcuaProductionAdapterConfig): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    const timer = setTimeout(() => {
      cleanup();
      socket.destroy();
      reject(new Error('OPCUA_RESPONSE_TIMEOUT'));
    }, config.responseTimeoutMs);
    const cleanup = () => {
      clearTimeout(timer);
      socket.removeListener('data', onData);
      socket.removeListener('end', onEnd);
      socket.removeListener('error', onError);
    };
    const onData = (chunk: Buffer) => { chunks.push(chunk); };
    const onEnd = () => { cleanup(); resolve(Buffer.concat(chunks)); };
    const onError = (error: Error) => { cleanup(); reject(error); };
    socket.on('data', onData);
    socket.on('end', onEnd);
    socket.on('error', onError);
  });
}

async function executeControlledRequest(
  request: OpcuaProductionReadRequest,
  wireService: OpcuaProductionAdapterConfig['service'],
): Promise<OpcuaProductionReadResult> {
  const { config, resolveEndpoint, resolveNodeAllowlist, testMode = false } = request;
  const configError = validateProductionAdapterConfig({ ...config, service: wireService });
  if (configError) return failure(configError, config);

  const endpoint = resolveEndpoint(config.endpointReferenceId);
  if (!endpoint) return failure('OPCUA_ENDPOINT_REFERENCE_NOT_FOUND', config);

  const connectPreview = resolveConnectHost(endpoint, request);
  if (
    !connectPreview.ok &&
    ['OPCUA_DNS_NOT_ALLOWED', 'OPCUA_DNS_RESULT_REJECTED', 'OPCUA_METADATA_ENDPOINT_REJECTED'].includes(connectPreview.errorCode)
  ) {
    return failure(connectPreview.errorCode, config, endpoint);
  }

  const targetError = validateProductionEndpoint(endpoint, config, testMode);
  if (targetError) return failure(targetError, config, endpoint);

  const nodeAllowlist = resolveNodeAllowlist(config.nodeAllowlistReferenceId);
  if (!nodeAllowlist?.length) return failure('OPCUA_NODE_NOT_ALLOWLISTED', config, endpoint);

  const foundationError = runFoundationRequestValidation(endpoint, config, nodeAllowlist, testMode, wireService === 'HEALTH_PROBE' ? 'READ' : wireService);
  if (foundationError) return failure(foundationError, config, endpoint);

  const connectHost = resolveConnectHost(endpoint, request);
  if (!connectHost.ok) return failure(connectHost.errorCode, config, endpoint);

  const requestId = randomInt(1, 0xffffffff);
  const endpointHash = createEndpointHash(endpoint.hostname, endpoint.port);
  let packet: Buffer;
  try {
    packet = encodeRequestPacket({
      requestId,
      service: wireService,
      endpointHash,
      reads: config.reads,
      maxNodeIdLength: config.maxNodeIdLength,
    });
  } catch {
    return failure('OPCUA_REQUEST_FRAME_INVALID', config, endpoint);
  }

  const startedAt = Date.now();
  return new Promise((resolve) => {
    const socket = net.createConnection({ host: connectHost.host, port: endpoint.port }, async () => {
      try {
        if (Date.now() - startedAt > config.maxProcessingMilliseconds) {
          socket.destroy();
          resolve(failure('OPCUA_RESPONSE_TIMEOUT', config, endpoint));
          return;
        }
        const responsePromise = readFullResponse(socket, config);
        socket.write(packet);
        socket.end();
        const responseBuffer = await responsePromise;
        let decoded: DecodedResponse;
        try {
          decoded = decodeResponsePacket(responseBuffer, config.maxResponseBytes, config.maxNodeIdLength, config.maxValueBytes);
        } catch (error) {
          const message = error instanceof Error ? error.message : 'OPCUA_RESPONSE_MAGIC_INVALID';
          if (message === 'OPCUA_RESPONSE_SIZE_LIMIT_EXCEEDED') resolve(failure('OPCUA_RESPONSE_SIZE_LIMIT_EXCEEDED', config, endpoint));
          else if (message === 'OPCUA_DECODE_FAILED') resolve(failure('OPCUA_DECODE_FAILED', config, endpoint));
          else if (message.includes('FRAME')) resolve(failure('OPCUA_RESPONSE_FRAME_INVALID', config, endpoint));
          else resolve(failure('OPCUA_RESPONSE_MAGIC_INVALID', config, endpoint));
          return;
        }

        if (decoded.requestHandle !== requestId) {
          resolve(failure('OPCUA_REQUEST_ID_MISMATCH', config, endpoint));
          return;
        }
        if (decoded.service !== wireService) {
          resolve(failure('OPCUA_SERVICE_MISMATCH', config, endpoint));
          return;
        }
        if (decoded.responseStatus === STATUS_ERROR) {
          resolve(failure('OPCUA_STATUS_ERROR_RESPONSE', config, endpoint));
          return;
        }
        if (decoded.responseStatus === STATUS_BAD) {
          resolve(failure('OPCUA_BAD_STATUS_RESPONSE', config, endpoint));
          return;
        }

        const foundationService = wireService === 'HEALTH_PROBE' ? 'READ' : wireService;
        const responseForFoundation = wireService === 'HEALTH_PROBE'
          ? { ...decoded, service: 'READ' }
          : decoded;

        const normalized = decodeAndNormalizeResponse(
          responseForFoundation,
          endpoint,
          config,
          nodeAllowlist,
          testMode,
          foundationService,
        );
        if (!normalized.ok) {
          resolve(failure(normalized.errorCode, config, endpoint));
          return;
        }

        resolve({
          ok: true,
          endpointReferenceId: createEndpointReferenceId(config.endpointReferenceId, wireService, config.reads[0]?.nodeId ?? 'ns=0;i=0'),
          endpointHash,
          service: wireService,
          recordCount: normalized.records.length,
          records: normalized.records,
          foundationAccepted: true,
        });
      } catch {
        resolve(failure('OPCUA_REQUEST_FAILED', config, endpoint));
      }
    });
    socket.on('error', () => resolve(failure('OPCUA_REQUEST_FAILED', config, endpoint)));
  });
}

export function createOpcuaProductionReadOnlyAdapter(): OpcuaProductionReadOnlyAdapter {
  return {
    readOnce: async (request) => {
      if (request.config.service !== 'READ') {
        return failure('OPCUA_SERVICE_NOT_ALLOWED', { ...request.config, service: 'READ' });
      }
      return executeControlledRequest(request, 'READ');
    },
    browseOnce: async (request) => {
      if (request.config.service !== 'BROWSE') {
        return failure('OPCUA_SERVICE_NOT_ALLOWED', { ...request.config, service: 'BROWSE' });
      }
      return executeControlledRequest(request, 'BROWSE');
    },
    healthProbeOnce: async (request) => {
      if (request.config.service !== 'HEALTH_PROBE') {
        return failure('OPCUA_SERVICE_NOT_ALLOWED', { ...request.config, service: 'HEALTH_PROBE' });
      }
      return executeControlledRequest(request, 'HEALTH_PROBE');
    },
  };
}

export const opcuaProductionReadOnlyAdapter: OpcuaProductionReadOnlyAdapter = createOpcuaProductionReadOnlyAdapter();

export { validateProductionService };
