import type {
  OpcUaBrowseTarget,
  OpcUaNodeIdType,
  OpcUaNodeIdValidation,
  OpcUaNormalizedNodeId,
  OpcUaReadOnlyPolicy,
  OpcUaReadTarget,
  ValidationResult,
} from './opcua-readonly-types.js';

const NODE_ID_PATTERN = /^ns\s*=\s*(\d+)\s*;\s*(i|s|g|b)\s*=\s*(.+)$/i;

export function stringNodeIdHasPrefix(identifier: string, prefix: string): boolean {
  if (!identifier.startsWith(prefix)) return false;
  if (identifier.length === prefix.length) return true;
  const next = identifier[prefix.length];
  return next === '.' || next === '/' || /^\d/.test(identifier.slice(prefix.length));
}

function normalizeIdentifierType(typeToken: string): OpcUaNodeIdType | null {
  const token = typeToken.toLowerCase();
  if (token === 'i') return 'NUMERIC';
  if (token === 's') return 'STRING';
  if (token === 'g') return 'GUID';
  if (token === 'b') return 'BYTESTRING';
  return null;
}

function buildCanonical(namespaceIndex: number, identifierType: OpcUaNodeIdType, identifier: string): string {
  const typeToken =
    identifierType === 'NUMERIC' ? 'i' : identifierType === 'STRING' ? 's' : identifierType === 'GUID' ? 'g' : 'b';
  return `ns=${namespaceIndex};${typeToken}=${identifier}`;
}

export function normalizeOpcUaNodeId(nodeId: string): OpcUaNormalizedNodeId | null {
  if (!nodeId || typeof nodeId !== 'string') return null;
  const trimmed = nodeId.trim();
  const match = NODE_ID_PATTERN.exec(trimmed);
  if (!match) return null;

  const namespaceIndex = Number(match[1]);
  const identifierType = normalizeIdentifierType(match[2]);
  if (!Number.isInteger(namespaceIndex) || namespaceIndex < 0 || !identifierType) return null;

  let identifier = match[3].trim();
  if (identifierType === 'NUMERIC') {
    if (!/^\d+$/.test(identifier)) return null;
    identifier = String(Number(identifier));
  } else if (identifierType === 'STRING') {
    if (!identifier || /[\x00-\x1f\x7f]/.test(identifier)) return null;
  }

  return {
    originalNodeId: nodeId,
    namespaceIndex,
    identifierType,
    identifier,
    canonical: buildCanonical(namespaceIndex, identifierType, identifier),
  };
}

function isNumericAllowed(normalized: OpcUaNormalizedNodeId, policy: OpcUaReadOnlyPolicy): boolean {
  if (normalized.identifierType !== 'NUMERIC') return false;
  const id = Number(normalized.identifier);
  return policy.allowedNumericNodeIds.some(
    (entry) => entry.namespaceIndex === normalized.namespaceIndex && entry.identifier === id,
  );
}

function isStringAllowed(normalized: OpcUaNormalizedNodeId, policy: OpcUaReadOnlyPolicy): boolean {
  if (normalized.identifierType !== 'STRING') return false;
  for (const denied of policy.deniedStringNodeIdPrefixes) {
    if (
      denied.namespaceIndex === normalized.namespaceIndex &&
      stringNodeIdHasPrefix(normalized.identifier, denied.prefix)
    ) {
      return false;
    }
  }
  return policy.allowedStringNodeIdPrefixes.some(
    (entry) =>
      entry.namespaceIndex === normalized.namespaceIndex && stringNodeIdHasPrefix(normalized.identifier, entry.prefix),
  );
}

export function validateOpcUaNodeId(nodeId: string, policy: OpcUaReadOnlyPolicy): OpcUaNodeIdValidation {
  const errors: string[] = [];
  const normalized = normalizeOpcUaNodeId(nodeId);
  if (!normalized) return { ok: false, errors: ['OPCUA_NODE_ID_INVALID'] };

  if (!policy.allowedNamespaceIndexes.includes(normalized.namespaceIndex)) {
    errors.push('OPCUA_NAMESPACE_NOT_ALLOWED');
  }

  if (!policy.allowedNodeIdTypes.includes(normalized.identifierType)) {
    errors.push('OPCUA_NODE_ID_TYPE_NOT_ALLOWED');
  }

  if (normalized.identifierType === 'NUMERIC') {
    const numeric = Number(normalized.identifier);
    if (!Number.isInteger(numeric) || numeric < 0) errors.push('OPCUA_NODE_ID_INVALID');
    if (normalized.identifier.length > 1 && normalized.identifier.startsWith('0')) errors.push('OPCUA_NODE_ID_INVALID');
  }

  if (normalized.identifierType === 'STRING') {
    if (!normalized.identifier) errors.push('OPCUA_NODE_ID_INVALID');
    if (normalized.identifier.length > policy.maxStringLength) errors.push('OPCUA_NODE_ID_INVALID');
    if (normalized.identifier.includes('..') || normalized.identifier.includes('../')) {
      errors.push('OPCUA_NODE_ID_DENIED');
    }
  }

  for (const denied of policy.deniedStringNodeIdPrefixes) {
    if (
      normalized.identifierType === 'STRING' &&
      denied.namespaceIndex === normalized.namespaceIndex &&
      normalized.identifier.startsWith(denied.prefix)
    ) {
      return { ok: false, normalized, errors: ['OPCUA_NODE_ID_DENIED'] };
    }
  }

  const allowed =
    normalized.identifierType === 'NUMERIC'
      ? isNumericAllowed(normalized, policy)
      : normalized.identifierType === 'STRING'
        ? isStringAllowed(normalized, policy)
        : false;

  if (!allowed && errors.length === 0) {
    errors.push('OPCUA_NODE_ID_NOT_ALLOWED');
  }

  return { ok: errors.length === 0, normalized, errors: [...new Set(errors)] };
}

export function validateOpcUaAttribute(attributeId: string, policy: OpcUaReadOnlyPolicy): ValidationResult {
  const normalized = attributeId.trim().toUpperCase().replace(/[\s-]+/g, '_');
  if (!policy.allowedAttributes.includes(normalized as (typeof policy.allowedAttributes)[number])) {
    return { ok: false, errors: ['OPCUA_ATTRIBUTE_NOT_ALLOWED'] };
  }
  return { ok: true, errors: [] };
}

function validateIndexRange(indexRange: string | undefined): ValidationResult {
  if (indexRange === undefined || indexRange === '') return { ok: true, errors: [] };
  if (!/^\d+(:\d+)?$/.test(indexRange.trim())) {
    return { ok: false, errors: ['OPCUA_INDEX_RANGE_INVALID'] };
  }
  return { ok: true, errors: [] };
}

export function validateOpcUaReadRequest(
  input: {
    readonly reads?: readonly OpcUaReadTarget[];
    readonly maxRequestBytes?: number;
  },
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];
  const reads = input.reads ?? [];

  if (reads.length === 0) errors.push('OPCUA_REQUEST_MALFORMED');
  if (reads.length > policy.maxNodesPerRead) errors.push('OPCUA_READ_LIMIT_EXCEEDED');

  const seen = new Set<string>();
  for (const read of reads) {
    const nodeResult = validateOpcUaNodeId(read.nodeId, policy);
    if (!nodeResult.ok) errors.push(...nodeResult.errors);
    const attrResult = validateOpcUaAttribute(read.attributeId, policy);
    if (!attrResult.ok) errors.push(...attrResult.errors);
    const rangeResult = validateIndexRange(read.indexRange);
    if (!rangeResult.ok) errors.push(...rangeResult.errors);
    const key = `${nodeResult.normalized?.canonical ?? read.nodeId}:${read.attributeId.trim().toUpperCase()}:${read.indexRange ?? ''}`;
    if (seen.has(key)) errors.push('OPCUA_REQUEST_MALFORMED');
    seen.add(key);
  }

  const estimatedBytes = JSON.stringify(reads).length;
  if (typeof input.maxRequestBytes === 'number' && estimatedBytes > input.maxRequestBytes) {
    errors.push('OPCUA_READ_LIMIT_EXCEEDED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}

export function validateOpcUaBrowseRequest(
  input: OpcUaBrowseTarget,
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];

  const nodeResult = validateOpcUaNodeId(input.nodeId, policy);
  if (!nodeResult.ok) errors.push(...nodeResult.errors);

  const depth = input.depth ?? 1;
  if (depth > policy.maxBrowseDepth) errors.push('OPCUA_BROWSE_DEPTH_EXCEEDED');

  if (typeof input.continuationPoint === 'string') {
    if (!/^SYNTHETIC_CP_[A-Z0-9_]+$/.test(input.continuationPoint)) {
      errors.push('OPCUA_CONTINUATION_POINT_INVALID');
    }
    if (input.continuationPoint.length > policy.maxContinuationPointLength) {
      errors.push('OPCUA_CONTINUATION_POINT_INVALID');
    }
  }

  const direction = (input.browseDirection ?? 'FORWARD').trim().toUpperCase();
  if (!['FORWARD', 'INVERSE', 'BOTH'].includes(direction)) {
    errors.push('OPCUA_BROWSE_REQUEST_MALFORMED');
  }

  if (typeof input.nodeClassMask === 'number' && input.nodeClassMask < 0) {
    errors.push('OPCUA_BROWSE_REQUEST_MALFORMED');
  }

  if (typeof input.maxNodesPerBrowse === 'number' && input.maxNodesPerBrowse > policy.maxNodesPerBrowse) {
    errors.push('OPCUA_BROWSE_LIMIT_EXCEEDED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}
