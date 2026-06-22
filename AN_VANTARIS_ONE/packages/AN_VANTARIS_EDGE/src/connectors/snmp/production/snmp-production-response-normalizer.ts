import { validateSnmpOperation, validateSnmpReadOnlyPolicy, validateSnmpVersion } from '../snmp-readonly-policy.js';
import { validateSnmpOid, oidHasPrefix, normalizeSnmpOid } from '../snmp-oid-validator.js';
import { validateSnmpCredentialModel } from '../snmp-target-validator.js';
import { calculateResponseBytes, validateSnmpResponse } from '../snmp-response-validator.js';
import type { SnmpResponseMetadata, SnmpVarbind } from '../snmp-readonly-types.js';

import type {
  SnmpProductionAdapterConfig,
  SnmpProductionCredentialBundle,
  SnmpProductionErrorCode,
  SnmpProductionNormalizedRecord,
  SnmpProductionOperation,
  SnmpProductionResolvedTarget,
} from './snmp-production-adapter.types.js';
import {
  SNMP_PRODUCTION_DENIED_OPERATIONS,
  SNMP_PRODUCTION_READ_OPERATIONS,
} from './snmp-production-adapter.types.js';
import {
  buildFoundationPolicyForProduction,
  createOidReferenceHash,
  validateProductionResourceLimits,
} from './snmp-production-target-policy.js';

export function validateProductionOperation(operation: string): SnmpProductionErrorCode | null {
  const normalized = operation.trim().toUpperCase();
  if ((SNMP_PRODUCTION_DENIED_OPERATIONS as readonly string[]).includes(normalized)) {
    return 'SNMP_OPERATION_NOT_ALLOWED';
  }
  if (!SNMP_PRODUCTION_READ_OPERATIONS.includes(normalized as SnmpProductionOperation)) {
    return 'SNMP_OPERATION_NOT_ALLOWED';
  }
  return null;
}

export function validateProductionAdapterConfig(config: SnmpProductionAdapterConfig): SnmpProductionErrorCode | null {
  if (config.adapterMode !== 'PRODUCTION_SNMPV3_READONLY') return 'SNMP_CONFIG_INVALID';
  if (config.enabled !== true) return 'SNMP_ADAPTER_DISABLED';
  if (!config.targetReferenceId || !config.oidAllowlistReference || !config.credentialReferenceId) {
    return 'SNMP_CONFIG_INVALID';
  }
  if (config.snmpVersion !== '3') return 'SNMP_SECURITY_MODE_NOT_ALLOWED';
  if (config.securityMode !== 'authPriv') return 'SNMP_SECURITY_MODE_NOT_ALLOWED';
  if (!config.authProtocolReference || !config.privProtocolReference) return 'SNMP_CONFIG_INVALID';
  if (!(config.targetPort >= 1 && config.targetPort <= 65535)) return 'SNMP_PORT_NOT_ALLOWED';
  if (config.udpMode !== 'PRODUCTION_UDP' && config.udpMode !== 'LOOPBACK_TEST') return 'SNMP_CONFIG_INVALID';
  if (config.dnsMode !== 'DENY' && config.dnsMode !== 'INJECTED_TEST') return 'SNMP_CONFIG_INVALID';
  const opError = validateProductionOperation(config.operation);
  if (opError) return opError;
  if (!Array.isArray(config.oids) || config.oids.length === 0) return 'SNMP_OID_INVALID';
  if (config.oids.length > config.maxOids) return 'SNMP_VARBIND_LIMIT_EXCEEDED';
  if (config.operation === 'GETBULK' && config.bulkRepetitions > config.maxBulkRepetitions) {
    return 'SNMP_BULK_LIMIT_EXCEEDED';
  }
  if (config.maxRetries !== 0) return 'SNMP_CONFIG_INVALID';
  return validateProductionResourceLimits(config);
}

export function validateCredentialBundle(
  bundle: SnmpProductionCredentialBundle | undefined,
  config: SnmpProductionAdapterConfig,
): SnmpProductionErrorCode | null {
  if (!bundle) return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  if (bundle.credentialReferenceId !== config.credentialReferenceId) return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  if (bundle.securityMode !== 'authPriv') return 'SNMP_SECURITY_MODE_NOT_ALLOWED';
  if (bundle.authProtocolReference !== config.authProtocolReference) return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  if (bundle.privProtocolReference !== config.privProtocolReference) return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  if (config.engineIdReference && bundle.engineIdReference !== config.engineIdReference) {
    return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  }
  return null;
}

export function runFoundationRequestValidation(
  target: SnmpProductionResolvedTarget,
  config: SnmpProductionAdapterConfig,
  oidPrefixes: readonly string[],
  credential: SnmpProductionCredentialBundle,
  testMode: boolean,
): SnmpProductionErrorCode | null {
  const policy = buildFoundationPolicyForProduction(target, config, oidPrefixes, testMode);

  const versionResult = validateSnmpVersion(config.snmpVersion, policy);
  if (!versionResult.ok) return 'SNMP_SECURITY_MODE_NOT_ALLOWED';

  const operationResult = validateSnmpOperation(config.operation, policy);
  if (!operationResult.ok) return 'SNMP_OPERATION_NOT_ALLOWED';

  const credentialResult = validateSnmpCredentialModel(
    { credentialRef: credential.credentialReferenceId },
    policy,
  );
  if (!credentialResult.ok) {
    if (credentialResult.errors.includes('PLAINTEXT_COMMUNITY_PROHIBITED')) return 'SNMP_COMMUNITY_STRING_REJECTED';
    return 'SNMP_CREDENTIAL_REFERENCE_FAILED';
  }

  for (const oid of config.oids) {
    const oidResult = validateSnmpOid(oid, policy);
    if (!oidResult.ok) {
      if (oidResult.errors.includes('SNMP_OID_NOT_ALLOWED')) return 'SNMP_OID_NOT_ALLOWLISTED';
      return 'SNMP_OID_INVALID';
    }
  }

  if (testMode && config.udpMode === 'LOOPBACK_TEST') {
    return null;
  }

  const policyValidation = validateSnmpReadOnlyPolicy({
    ...policy,
    syntheticTransportOnly: false,
  } as unknown as typeof policy);
  if (!policyValidation.ok) return 'SNMP_FOUNDATION_VALIDATION_FAILED';
  return null;
}

export function mapFoundationResponseError(errors: readonly string[]): SnmpProductionErrorCode {
  if (errors.includes('SNMP_VARBIND_LIMIT_EXCEEDED')) return 'SNMP_VARBIND_LIMIT_EXCEEDED';
  if (errors.includes('SNMP_RESPONSE_TOO_LARGE')) return 'SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED';
  if (errors.includes('SNMP_WALK_LIMIT_EXCEEDED')) return 'SNMP_WALK_LIMIT_EXCEEDED';
  if (errors.includes('SNMP_OID_NOT_ALLOWED')) return 'SNMP_OID_NOT_ALLOWLISTED';
  if (errors.includes('SNMP_RESPONSE_MALFORMED')) return 'SNMP_PDU_INVALID';
  return 'SNMP_FOUNDATION_VALIDATION_FAILED';
}

export function validateFoundationResponse(
  metadata: SnmpResponseMetadata,
  target: SnmpProductionResolvedTarget,
  config: SnmpProductionAdapterConfig,
  oidPrefixes: readonly string[],
  testMode: boolean,
): SnmpProductionErrorCode | null {
  if (metadata.errorStatus !== 0) return 'SNMP_ERROR_STATUS';
  const policy = buildFoundationPolicyForProduction(target, config, oidPrefixes, testMode);
  const validation = validateSnmpResponse(metadata, policy);
  if (!validation.ok) return mapFoundationResponseError(validation.errors);
  return null;
}

export function oidWithinAllowlistedSubtree(oid: string, rootOid: string): boolean {
  const normalized = normalizeSnmpOid(oid);
  const root = normalizeSnmpOid(rootOid);
  if (!normalized || !root) return false;
  return oidHasPrefix(normalized.components, root.components);
}

export function normalizeVarbindRecords(
  varbinds: readonly SnmpVarbind[],
  operation: string,
): SnmpProductionNormalizedRecord[] {
  return varbinds.map((varbind, index) => ({
    fields: {
      index: String(index),
      oid: varbind.oid,
      oidReference: createOidReferenceHash(varbind.oid),
      type: varbind.type,
      value: String(varbind.value ?? ''),
      operation,
    },
  }));
}

export function decodeAndNormalizeResponse(
  metadata: SnmpResponseMetadata,
  target: SnmpProductionResolvedTarget,
  config: SnmpProductionAdapterConfig,
  oidPrefixes: readonly string[],
  testMode: boolean,
  operation: string,
): { ok: true; records: SnmpProductionNormalizedRecord[] } | { ok: false; errorCode: SnmpProductionErrorCode } {
  const foundationError = validateFoundationResponse(metadata, target, config, oidPrefixes, testMode);
  if (foundationError) return { ok: false, errorCode: foundationError };

  if (metadata.responseBytes > config.maxResponseBytes) {
    return { ok: false, errorCode: 'SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED' };
  }
  if (metadata.varbinds.length > config.maxVarbinds) {
    return { ok: false, errorCode: 'SNMP_VARBIND_LIMIT_EXCEEDED' };
  }

  return { ok: true, records: normalizeVarbindRecords(metadata.varbinds, operation) };
}

export function buildResponseMetadata(
  errorStatus: number,
  errorIndex: number,
  varbinds: readonly SnmpVarbind[],
  operation: string,
  walkDepth?: number,
  walkRows?: number,
): SnmpResponseMetadata {
  return {
    errorStatus,
    errorIndex,
    varbinds,
    responseBytes: calculateResponseBytes(varbinds),
    walkDepth,
    walkRows,
    operation,
  };
}

export type { SnmpResponseMetadata, SnmpVarbind };
