import type {
  SnmpReadOnlyPolicy,
  SnmpResponseMetadata,
  SnmpResponseValidation,
  SnmpVarbind,
} from './snmp-readonly-types.js';
import { validateSnmpOid } from './snmp-oid-validator.js';

function estimateVarbindBytes(varbind: SnmpVarbind): number {
  return (
    Buffer.byteLength(String(varbind.oid), 'utf8') +
    Buffer.byteLength(String(varbind.type), 'utf8') +
    Buffer.byteLength(String(varbind.value ?? ''), 'utf8')
  );
}

function normalizeVarbindType(type: string): string {
  return type.trim().toUpperCase().replace(/[\s-]+/g, '_');
}

export function validateSnmpResponse(
  metadata: SnmpResponseMetadata,
  policy: SnmpReadOnlyPolicy,
): SnmpResponseValidation {
  const errors: string[] = [];

  if (metadata.errorStatus !== 0) {
    errors.push('SNMP_RESPONSE_MALFORMED');
  }

  if (metadata.varbinds.length > policy.maxVarbinds) {
    errors.push('SNMP_VARBIND_LIMIT_EXCEEDED');
  }

  if (metadata.responseBytes > policy.maxResponseBytes) {
    errors.push('SNMP_RESPONSE_TOO_LARGE');
  }

  if ((metadata.walkDepth ?? 0) > policy.maxWalkDepth) {
    errors.push('SNMP_WALK_LIMIT_EXCEEDED');
  }

  if ((metadata.walkRows ?? metadata.varbinds.length) > policy.maxWalkRows) {
    errors.push('SNMP_WALK_LIMIT_EXCEEDED');
  }

  const seenOids = new Set<string>();
  for (const varbind of metadata.varbinds) {
    if (!varbind.oid || !varbind.type) {
      errors.push('SNMP_RESPONSE_MALFORMED');
      continue;
    }
    const oidCheck = validateSnmpOid(varbind.oid, policy);
    if (!oidCheck.ok) {
      errors.push(...oidCheck.errors.map((e) => (e === 'SNMP_OID_NOT_ALLOWED' ? e : 'SNMP_OID_NOT_ALLOWED')));
    }
    const normalizedOid = oidCheck.normalized?.oid ?? varbind.oid;
    if (seenOids.has(normalizedOid)) errors.push('SNMP_RESPONSE_MALFORMED');
    seenOids.add(normalizedOid);

    const type = normalizeVarbindType(varbind.type);
    if (!policy.allowedVarbindTypes.includes(type)) {
      errors.push('SNMP_RESPONSE_TYPE_NOT_ALLOWED');
    }
  }

  return { ok: errors.length === 0, metadata, errors: [...new Set(errors)] };
}

export function calculateResponseBytes(varbinds: readonly SnmpVarbind[]): number {
  return varbinds.reduce((sum, vb) => sum + estimateVarbindBytes(vb), 0);
}
