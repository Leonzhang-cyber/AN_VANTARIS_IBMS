import { randomInt } from 'node:crypto';
import dgram from 'node:dgram';

import type {
  SnmpProductionAdapterConfig,
  SnmpProductionErrorCode,
  SnmpProductionReadFailure,
  SnmpProductionReadOnlyAdapter,
  SnmpProductionReadRequest,
  SnmpProductionReadResult,
  SnmpProductionResolvedTarget,
  SnmpProductionWalkRequest,
} from './snmp-production-adapter.types.js';
import {
  buildResponseMetadata,
  decodeAndNormalizeResponse,
  oidWithinAllowlistedSubtree,
  runFoundationRequestValidation,
  validateCredentialBundle,
  validateProductionAdapterConfig,
} from './snmp-production-response-normalizer.js';
import type { SnmpProductionNormalizedRecord } from './snmp-production-adapter.types.js';
import {
  createTargetHash,
  createTargetReferenceId,
  validateAllResolvedIps,
  validateProductionTarget,
} from './snmp-production-target-policy.js';

const REQUEST_MAGIC = Buffer.from([0x53, 0x4e, 0x50, 0x33]);
const RESPONSE_MAGIC = Buffer.from([0x53, 0x4e, 0x52, 0x33]);
const OP_GET = 1;
const OP_GETNEXT = 2;
const OP_GETBULK = 3;
const VERSION_V3 = 3;
const SECURITY_AUTH_PRIV = 3;

const IPV4_PATTERN = /^(?:\d{1,3}\.){3}\d{1,3}$/;

type DecodedResponse = {
  requestId: number;
  errorStatus: number;
  errorIndex: number;
  varbinds: SnmpVarbind[];
};

type SnmpVarbind = import('./snmp-production-response-normalizer.js').SnmpVarbind;

function failure(
  errorCode: SnmpProductionErrorCode,
  config: SnmpProductionAdapterConfig,
  target?: SnmpProductionResolvedTarget,
  extra?: Partial<SnmpProductionReadFailure>,
): SnmpProductionReadFailure {
  return {
    ok: false,
    errorCode,
    targetReferenceId: createTargetReferenceId(
      config.targetReferenceId,
      config.operation,
      config.oids[0] ?? '',
    ),
    targetHash: target ? createTargetHash(target.hostname, target.port) : undefined,
    operation: config.operation,
    ...extra,
  };
}

function isIpAddress(hostname: string): boolean {
  return IPV4_PATTERN.test(hostname.trim()) || hostname.includes(':');
}

function operationCode(operation: string): number {
  switch (operation.toUpperCase()) {
    case 'GET': return OP_GET;
    case 'GETNEXT': return OP_GETNEXT;
    case 'GETBULK': return OP_GETBULK;
    default: return 0;
  }
}

function encodeRequestPdu(input: {
  requestId: number;
  version: number;
  operation: number;
  securityMode: number;
  credentialReferenceId: string;
  oids: readonly string[];
  bulkRepetitions: number;
}): Buffer {
  const credentialBytes = Buffer.from(input.credentialReferenceId, 'utf8');
  if (credentialBytes.length > 255) throw new Error('SNMP_PDU_INVALID');

  let size = 4 + 4 + 1 + 1 + 1 + 1 + credentialBytes.length + 2 + 2;
  for (const oid of input.oids) {
    const oidBytes = Buffer.from(oid, 'utf8');
    if (oidBytes.length > 65535) throw new Error('SNMP_PDU_INVALID');
    size += 2 + oidBytes.length;
  }

  const buffer = Buffer.alloc(size);
  let offset = 0;
  REQUEST_MAGIC.copy(buffer, offset); offset += 4;
  buffer.writeUInt32BE(input.requestId, offset); offset += 4;
  buffer[offset++] = input.version;
  buffer[offset++] = input.operation;
  buffer[offset++] = input.securityMode;
  buffer[offset++] = credentialBytes.length;
  credentialBytes.copy(buffer, offset); offset += credentialBytes.length;
  buffer.writeUInt16BE(input.oids.length, offset); offset += 2;
  buffer.writeUInt16BE(input.bulkRepetitions, offset); offset += 2;
  for (const oid of input.oids) {
    const oidBytes = Buffer.from(oid, 'utf8');
    buffer.writeUInt16BE(oidBytes.length, offset); offset += 2;
    oidBytes.copy(buffer, offset); offset += oidBytes.length;
  }
  return buffer;
}

function decodeResponsePdu(buffer: Buffer, maxResponseBytes: number): DecodedResponse {
  if (buffer.length < 18) throw new Error('SNMP_PDU_INVALID');
  if (buffer.length > maxResponseBytes) throw new Error('SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED');
  if (!buffer.subarray(0, 4).equals(RESPONSE_MAGIC)) throw new Error('SNMP_PDU_INVALID');

  const requestId = buffer.readUInt32BE(4);
  const errorStatus = buffer.readUInt32BE(8);
  const errorIndex = buffer.readUInt32BE(12);
  const varbindCount = buffer.readUInt16BE(16);
  let offset = 18;
  const varbinds: SnmpVarbind[] = [];

  for (let i = 0; i < varbindCount; i += 1) {
    if (offset + 2 > buffer.length) throw new Error('SNMP_PDU_INVALID');
    const oidLen = buffer.readUInt16BE(offset); offset += 2;
    if (offset + oidLen + 1 + 2 > buffer.length) throw new Error('SNMP_PDU_INVALID');
    const oid = buffer.subarray(offset, offset + oidLen).toString('utf8'); offset += oidLen;
    const typeLen = buffer[offset]; offset += 1;
    if (offset + typeLen + 2 > buffer.length) throw new Error('SNMP_PDU_INVALID');
    const type = buffer.subarray(offset, offset + typeLen).toString('utf8'); offset += typeLen;
    const valueLen = buffer.readUInt16BE(offset); offset += 2;
    if (offset + valueLen > buffer.length) throw new Error('SNMP_PDU_INVALID');
    const valueText = buffer.subarray(offset, offset + valueLen).toString('utf8'); offset += valueLen;
    let value: string | number | boolean | null = valueText;
    if (type === 'INTEGER' || type === 'COUNTER32' || type === 'GAUGE32' || type === 'TIMETICKS') {
      value = Number(valueText);
    } else if (type === 'NULL') {
      value = null;
    }
    varbinds.push({ oid, type, value });
  }

  if (offset !== buffer.length) throw new Error('SNMP_PDU_INVALID');
  return { requestId, errorStatus, errorIndex, varbinds };
}

function resolveConnectHost(
  target: SnmpProductionResolvedTarget,
  request: SnmpProductionReadRequest,
): { ok: true; host: string } | { ok: false; errorCode: SnmpProductionErrorCode } {
  const { config, resolveDns, testMode = false } = request;
  const hostname = target.hostname.trim();

  if (isIpAddress(hostname)) {
    const ipError = validateAllResolvedIps([hostname], testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: hostname };
  }

  if (config.dnsMode === 'DENY' && !resolveDns) {
    return { ok: false, errorCode: 'SNMP_DNS_NOT_ALLOWED' };
  }

  if (resolveDns) {
    const injected = resolveDns(hostname);
    if (!injected || injected.length === 0) return { ok: false, errorCode: 'SNMP_DNS_RESULT_REJECTED' };
    const ipError = validateAllResolvedIps(injected, testMode, config.allowPrivateNetworkReference);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, host: injected[0] };
  }

  return { ok: false, errorCode: 'SNMP_DNS_NOT_ALLOWED' };
}

async function sendUdpRequest(
  host: string,
  port: number,
  payload: Buffer,
  config: SnmpProductionAdapterConfig,
): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    const socket = dgram.createSocket('udp4');
    const timer = setTimeout(() => {
      socket.close();
      reject(new Error('SNMP_RESPONSE_TIMEOUT'));
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

async function executeControlledRead(request: SnmpProductionReadRequest): Promise<SnmpProductionReadResult> {
  const { config, resolveTarget, resolveOidAllowlist, resolveCredential, testMode = false } = request;
  const configError = validateProductionAdapterConfig(config);
  if (configError) return failure(configError, config);

  const target = resolveTarget(config.targetReferenceId);
  if (!target) return failure('SNMP_TARGET_REFERENCE_NOT_FOUND', config);

  const connectPreview = resolveConnectHost(target, request);
  if (!connectPreview.ok && ['SNMP_DNS_NOT_ALLOWED', 'SNMP_DNS_RESULT_REJECTED', 'SNMP_METADATA_TARGET_REJECTED'].includes(connectPreview.errorCode)) {
    return failure(connectPreview.errorCode, config, target);
  }

  const targetError = validateProductionTarget(target, config, testMode);
  if (targetError) return failure(targetError, config, target);

  const oidPrefixes = resolveOidAllowlist(config.oidAllowlistReference);
  if (!oidPrefixes || oidPrefixes.length === 0) return failure('SNMP_OID_NOT_ALLOWLISTED', config, target);

  const credential = resolveCredential(config.credentialReferenceId);
  const credentialError = validateCredentialBundle(credential, config);
  if (credentialError) return failure(credentialError, config, target);

  const foundationError = runFoundationRequestValidation(target, config, oidPrefixes, credential!, testMode);
  if (foundationError) return failure(foundationError, config, target);

  const connectHost = resolveConnectHost(target, request);
  if (!connectHost.ok) return failure(connectHost.errorCode, config, target);

  const requestId = randomInt(1, 0xffffffff);
  let requestPdu: Buffer;
  try {
    requestPdu = encodeRequestPdu({
      requestId,
      version: VERSION_V3,
      operation: operationCode(config.operation),
      securityMode: SECURITY_AUTH_PRIV,
      credentialReferenceId: config.credentialReferenceId,
      oids: config.oids,
      bulkRepetitions: config.bulkRepetitions,
    });
  } catch {
    return failure('SNMP_PDU_INVALID', config, target);
  }

  if (requestPdu.length > config.maxResponseBytes) {
    return failure('SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED', config, target);
  }

  const startedAt = Date.now();
  if (Date.now() - startedAt > config.maxProcessingMilliseconds) {
    return failure('SNMP_RESPONSE_TIMEOUT', config, target);
  }

  try {
    const responseBuffer = await sendUdpRequest(connectHost.host, target.port, requestPdu, config);
    let decoded: DecodedResponse;
    try {
      decoded = decodeResponsePdu(responseBuffer, config.maxResponseBytes);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'SNMP_PDU_INVALID';
      if (message === 'SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED') {
        return failure('SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED', config, target);
      }
      return failure('SNMP_PDU_INVALID', config, target);
    }

    if (decoded.requestId !== requestId) {
      return failure('SNMP_REQUEST_ID_MISMATCH', config, target);
    }
    if (decoded.errorStatus !== 0) {
      return failure('SNMP_ERROR_STATUS', config, target);
    }

    const metadata = buildResponseMetadata(
      decoded.errorStatus,
      decoded.errorIndex,
      decoded.varbinds,
      config.operation,
    );
    const normalized = decodeAndNormalizeResponse(
      metadata,
      target,
      config,
      oidPrefixes,
      testMode,
      config.operation,
    );
    if (!normalized.ok) return failure(normalized.errorCode, config, target);

    return {
      ok: true,
      targetReferenceId: createTargetReferenceId(config.targetReferenceId, config.operation, config.oids[0] ?? ''),
      targetHash: createTargetHash(target.hostname, target.port),
      operation: config.operation,
      recordCount: normalized.records.length,
      records: normalized.records,
      foundationAccepted: true,
    };
  } catch {
    return failure('SNMP_REQUEST_FAILED', config, target);
  }
}

async function executeControlledWalk(request: SnmpProductionWalkRequest): Promise<SnmpProductionReadResult> {
  const { walkRootOid, config, testMode = false } = request;
  const oidPrefixes = request.resolveOidAllowlist(config.oidAllowlistReference);
  if (!oidPrefixes || oidPrefixes.length === 0) {
    return failure('SNMP_OID_NOT_ALLOWLISTED', config);
  }

  const target = request.resolveTarget(config.targetReferenceId);
  if (!target) return failure('SNMP_TARGET_REFERENCE_NOT_FOUND', config);

  let currentOid = walkRootOid;
  const collected: SnmpProductionNormalizedRecord[] = [];

  for (let row = 0; row < config.maxWalkRows; row += 1) {
    const stepResult = await executeControlledRead({
      ...request,
      config: { ...config, operation: 'GETNEXT', oids: [currentOid], bulkRepetitions: 0 },
    });
    if (!stepResult.ok) return stepResult;
    if (stepResult.recordCount === 0) break;

    const nextOid = stepResult.records[0]?.fields.oid;
    if (!nextOid || !oidWithinAllowlistedSubtree(nextOid, walkRootOid)) break;
    if (nextOid.split('.').length > config.maxWalkDepth) {
      return failure('SNMP_WALK_LIMIT_EXCEEDED', config, target);
    }

    collected.push(...stepResult.records);
    currentOid = nextOid;
    if (collected.length >= config.maxWalkRows) break;
  }

  if (collected.length === 0) {
    return failure('SNMP_WALK_LIMIT_EXCEEDED', config, target);
  }

  return {
    ok: true,
    targetReferenceId: createTargetReferenceId(config.targetReferenceId, 'WALK', walkRootOid),
    targetHash: createTargetHash(target.hostname, target.port),
    operation: 'WALK',
    recordCount: collected.length,
    records: collected,
    foundationAccepted: true,
  };
}

export function createSnmpProductionReadOnlyAdapter(): SnmpProductionReadOnlyAdapter {
  return {
    readOnce: async (request: SnmpProductionReadRequest): Promise<SnmpProductionReadResult> =>
      executeControlledRead(request),
    walkOnce: async (request: SnmpProductionWalkRequest): Promise<SnmpProductionReadResult> =>
      executeControlledWalk(request),
  };
}

export const snmpProductionReadOnlyAdapter: SnmpProductionReadOnlyAdapter = createSnmpProductionReadOnlyAdapter();

export {
  encodeRequestPdu,
  decodeResponsePdu,
  REQUEST_MAGIC,
  RESPONSE_MAGIC,
  OP_GET,
  OP_GETNEXT,
  OP_GETBULK,
};
