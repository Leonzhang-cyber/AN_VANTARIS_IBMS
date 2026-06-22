import type { SnmpNormalizedOid, SnmpOidValidation, SnmpReadOnlyPolicy } from './snmp-readonly-types.js';

function stripLeadingDot(oid: string): string {
  return oid.replace(/^\.+/, '').trim();
}

function parsePrefixComponents(prefix: string): number[] {
  return stripLeadingDot(prefix)
    .split('.')
    .filter(Boolean)
    .map((part) => Number(part));
}

export function oidHasPrefix(components: readonly number[], prefixComponents: readonly number[]): boolean {
  if (prefixComponents.length === 0 || components.length < prefixComponents.length) return false;
  for (let i = 0; i < prefixComponents.length; i += 1) {
    if (components[i] !== prefixComponents[i]) return false;
  }
  return true;
}

export function normalizeSnmpOid(oid: string): SnmpNormalizedOid | null {
  if (!oid || typeof oid !== 'string') return null;
  const cleaned = stripLeadingDot(oid);
  if (!cleaned) return null;
  if (cleaned.includes('..')) return null;
  const parts = cleaned.split('.');
  if (parts.some((part) => part.length === 0)) return null;
  const numeric: number[] = [];
  for (const part of parts) {
    if (!/^\d+$/.test(part)) return null;
    const value = Number(part);
    if (!Number.isInteger(value) || value < 0) return null;
    numeric.push(value);
  }
  return { originalOid: oid, oid: numeric.join('.'), components: numeric };
}

export function validateSnmpOid(oid: string, policy: SnmpReadOnlyPolicy): SnmpOidValidation {
  if (!oid || typeof oid !== 'string' || oid.trim().length === 0) {
    return { ok: false, errors: ['SNMP_OID_EMPTY'] };
  }
  if (oid.includes('..')) {
    return { ok: false, errors: ['SNMP_OID_REPEATED_SEPARATOR'] };
  }

  const normalized = normalizeSnmpOid(oid);
  if (!normalized) {
    if (oid.split('.').some((part) => /^-/.test(part.trim()))) {
      return { ok: false, errors: ['SNMP_OID_NEGATIVE_COMPONENT'] };
    }
    if (/[^0-9.]/.test(stripLeadingDot(oid))) {
      return { ok: false, errors: ['SNMP_OID_NON_NUMERIC'] };
    }
    return { ok: false, errors: ['SNMP_OID_MALFORMED'] };
  }

  const errors: string[] = [];
  if (normalized.components.length > policy.maxOidComponents) {
    errors.push('SNMP_OID_EXCESSIVE_COMPONENTS');
  }
  if (normalized.components.some((part) => part > policy.maxOidComponentValue)) {
    errors.push('SNMP_OID_OVERSIZED');
  }

  for (const denied of policy.deniedOidPrefixes) {
    if (oidHasPrefix(normalized.components, parsePrefixComponents(denied))) {
      errors.push('SNMP_OID_DENIED_PREFIX');
    }
  }

  const allowed = policy.allowedOidPrefixes.some((prefix) =>
    oidHasPrefix(normalized.components, parsePrefixComponents(prefix)),
  );
  if (!allowed) errors.push('SNMP_OID_NOT_ALLOWED');

  if (normalized.components.length > policy.maxWalkDepth) {
    errors.push('SNMP_WALK_LIMIT_EXCEEDED');
  }

  return { ok: errors.length === 0, normalized, errors: [...new Set(errors)] };
}
