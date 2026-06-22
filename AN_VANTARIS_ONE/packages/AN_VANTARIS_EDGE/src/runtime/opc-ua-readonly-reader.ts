import { mkdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type { NormalizedSamplePlaceholder } from './protocol-plugin-types.js';
import type {
  OpcUaReadonlyConfig,
  OpcUaReadonlyDataType,
  OpcUaReadonlyError,
  OpcUaReadonlyEvidence,
  OpcUaReadonlyValidationResult,
  OpcUaSyntheticFixture,
  OpcUaSyntheticNode,
} from './opc-ua-readonly-types.js';

const DEFAULT_MAX_BYTES = 1024 * 1024;
const ALLOWED_DATA_TYPES = new Set<OpcUaReadonlyDataType>([
  'Boolean',
  'Byte',
  'Int16',
  'UInt16',
  'Int32',
  'UInt32',
  'Int64',
  'UInt64',
  'Float',
  'Double',
  'String',
  'DateTime',
]);

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asNumber(value: unknown): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : 0;
}

function isUnder(absolutePath: string, allowedRoot: string): boolean {
  const normalizedRoot = resolve(allowedRoot);
  const normalizedPath = resolve(absolutePath);
  return normalizedPath == normalizedRoot || normalizedPath.startsWith(normalizedRoot + '/');
}

function isValidOpcNodeId(nodeId: string): boolean {
  return /^ns=\d+;(s=.+|i=\d+)$/.test(nodeId.trim());
}

export function validateOpcUaEndpoint(endpointUrl: string): OpcUaReadonlyValidationResult {
  const normalized = endpointUrl.trim().toLowerCase();
  const allowed =
    normalized == 'mock://synthetic-opc-ua-server' ||
    normalized == 'opc.tcp://127.0.0.1:4840' ||
    normalized == 'opc.tcp://localhost:4840' ||
    normalized == 'opc.tcp://example.invalid:4840';
  if (!allowed) {
    return {
      valid: false,
      errors: ['endpoint_url_not_allowed_for_opc_ua_readonly_foundation'],
    };
  }
  return { valid: true, errors: [] };
}

export function validateOpcUaFixturePath(edgeRoot: string, fixturePath: string): OpcUaReadonlyValidationResult & {
  readonly absolutePath: string;
} {
  const resolvedEdgeRoot = resolve(edgeRoot);
  const resolvedFixture = resolve(resolvedEdgeRoot, fixturePath);
  const allowedConfigSamples = resolve(resolvedEdgeRoot, 'config/samples');
  const allowedRuntimeInput = resolve(resolvedEdgeRoot, '.runtime/input');
  const valid = isUnder(resolvedFixture, allowedConfigSamples) || isUnder(resolvedFixture, allowedRuntimeInput);
  if (!valid) {
    return {
      valid: false,
      absolutePath: resolvedFixture,
      errors: [`fixture_path_not_allowed:${resolvedFixture}`],
    };
  }
  return {
    valid: true,
    absolutePath: resolvedFixture,
    errors: [],
  };
}

function validateNodeShape(node: { readonly nodeId: string; readonly dataType: string }): OpcUaReadonlyValidationResult {
  const errors: string[] = [];
  if (!isValidOpcNodeId(node.nodeId)) {
    errors.push(`invalid_node_id:${node.nodeId}`);
  }
  if (!ALLOWED_DATA_TYPES.has(node.dataType as OpcUaReadonlyDataType)) {
    errors.push(`invalid_data_type:${node.dataType}`);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function validateOpcUaReadonlyConfig(config: OpcUaReadonlyConfig): OpcUaReadonlyValidationResult {
  const errors: string[] = [];
  if (!config.connectorId) errors.push('connectorId is required');
  if (config.protocol != 'opc-ua-readonly') errors.push('protocol must be opc-ua-readonly');
  if (!config.endpointUrl) errors.push('endpointUrl is required');
  if (config.securityMode != 'None') errors.push('securityMode must be None');
  if (config.securityPolicy != 'None') errors.push('securityPolicy must be None');
  if (!config.namespaceUri) errors.push('namespaceUri is required');
  if (!config.serverApplicationUri) errors.push('serverApplicationUri is required');
  if (config.pollingIntervalMs <= 0) errors.push('pollingIntervalMs must be > 0');
  if (config.timeoutMs <= 0) errors.push('timeoutMs must be > 0');
  if (config.retries < 0) errors.push('retries must be >= 0');
  if (config.networkEnabled !== false) errors.push('networkEnabled must be false in c3-06 foundation');
  if (config.supportsWriteback !== false) errors.push('supportsWriteback must be false for opc ua readonly');
  const endpointCheck = validateOpcUaEndpoint(config.endpointUrl);
  if (!endpointCheck.valid) errors.push(...endpointCheck.errors);
  if (!config.fixturePath) errors.push('fixturePath is required');
  for (const mapping of config.nodeMappings) {
    const nodeCheck = validateNodeShape(mapping);
    if (!nodeCheck.valid) errors.push(...nodeCheck.errors);
  }
  return {
    valid: errors.length == 0,
    errors,
  };
}

export function readOpcUaSyntheticFixture(config: OpcUaReadonlyConfig): {
  readonly ok: boolean;
  readonly fixturePath: string;
  readonly bytesRead: number;
  readonly content: string;
  readonly errors: readonly OpcUaReadonlyError[];
} {
  const pathCheck = validateOpcUaFixturePath('./AN_VANTARIS_EDGE', config.fixturePath);
  if (!pathCheck.valid) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: pathCheck.errors.map((message) => ({ code: 'fixture_path_invalid', message })),
    };
  }
  let fileSize = 0;
  try {
    fileSize = statSync(pathCheck.absolutePath).size;
  } catch (error) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [{ code: 'fixture_stat_failed', message: error instanceof Error ? error.message : 'fixture stat failed' }],
    };
  }
  if (fileSize > DEFAULT_MAX_BYTES) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: fileSize,
      content: '',
      errors: [{ code: 'fixture_too_large', message: `fixture exceeds max bytes: ${fileSize}` }],
    };
  }
  try {
    const content = readFileSync(pathCheck.absolutePath, 'utf8');
    return {
      ok: true,
      fixturePath: pathCheck.absolutePath,
      bytesRead: Buffer.byteLength(content, 'utf8'),
      content,
      errors: [],
    };
  } catch (error) {
    return {
      ok: false,
      fixturePath: pathCheck.absolutePath,
      bytesRead: 0,
      content: '',
      errors: [{ code: 'fixture_read_failed', message: error instanceof Error ? error.message : 'fixture read failed' }],
    };
  }
}

export function parseOpcUaSyntheticFixture(content: string): {
  readonly ok: boolean;
  readonly fixture: OpcUaSyntheticFixture | null;
  readonly errors: readonly OpcUaReadonlyError[];
} {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_json_parse_failed', message: error instanceof Error ? error.message : 'fixture parse failed' }],
    };
  }
  if (!isObject(parsed)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_invalid_shape', message: 'fixture root must be object' }],
    };
  }
  if (asString(parsed.protocol) != 'opc-ua-readonly') {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_protocol_invalid', message: 'fixture protocol must be opc-ua-readonly' }],
    };
  }
  if (parsed.networkEnabled !== false) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_network_enabled_invalid', message: 'fixture networkEnabled must be false' }],
    };
  }
  const endpointUrl = asString(parsed.endpointUrl);
  const endpointCheck = validateOpcUaEndpoint(endpointUrl);
  if (!endpointCheck.valid) {
    return {
      ok: false,
      fixture: null,
      errors: endpointCheck.errors.map((message) => ({ code: 'fixture_endpoint_invalid', message })),
    };
  }
  const nodesRaw = parsed.nodes;
  if (!Array.isArray(nodesRaw)) {
    return {
      ok: false,
      fixture: null,
      errors: [{ code: 'fixture_nodes_missing', message: 'nodes array is required' }],
    };
  }

  const nodes: OpcUaSyntheticNode[] = [];
  const errors: OpcUaReadonlyError[] = [];
  nodesRaw.forEach((item, index) => {
    if (!isObject(item)) {
      errors.push({ code: 'node_invalid_shape', message: 'node must be object', details: { index } });
      return;
    }
    const nodeId = asString(item.nodeId);
    const dataType = asString(item.dataType);
    const nodeCheck = validateNodeShape({ nodeId, dataType });
    if (!nodeCheck.valid) {
      errors.push({
        code: 'node_mapping_invalid',
        message: nodeCheck.errors.join('; '),
        details: { index },
      });
      return;
    }
    nodes.push({
      pointId: asString(item.pointId),
      nodeId,
      browseName: asString(item.browseName),
      displayName: asString(item.displayName),
      dataType: dataType as OpcUaReadonlyDataType,
      value:
        typeof item.value == 'number' || typeof item.value == 'string' || typeof item.value == 'boolean'
          ? item.value
          : asString(item.value),
      statusCode: asString(item.statusCode) || 'Good',
      sourceTimestamp: asString(item.sourceTimestamp) || nowIso(),
      serverTimestamp: asString(item.serverTimestamp) || nowIso(),
      engineeringUnit: asString(item.engineeringUnit) || 'synthetic-unit',
    });
  });

  return {
    ok: errors.length == 0,
    fixture: {
      connectorId: asString(parsed.connectorId) || 'connector-opcua-example-01',
      protocol: 'opc-ua-readonly',
      networkEnabled: false,
      source: 'synthetic-fixture',
      endpointUrl,
      securityMode: 'None',
      securityPolicy: 'None',
      namespaceUri: asString(parsed.namespaceUri) || 'urn:synthetic:opcua:namespace',
      serverApplicationUri: asString(parsed.serverApplicationUri) || 'urn:synthetic:opcua:server',
      nodes,
    },
    errors,
  };
}

export function extractOpcUaNodeRecords(input: {
  fixture: OpcUaSyntheticFixture;
  config: OpcUaReadonlyConfig;
}): {
  readonly nodes: readonly OpcUaSyntheticNode[];
  readonly errors: readonly OpcUaReadonlyError[];
} {
  const errors: OpcUaReadonlyError[] = [];
  const mappingByPointId = new Map(input.config.nodeMappings.map((mapping) => [mapping.pointId, mapping]));
  const nodes = input.fixture.nodes.map((node) => {
    const mapped = mappingByPointId.get(node.pointId);
    if (!mapped) return node;
    return {
      ...node,
      browseName: node.browseName || mapped.browseName,
      displayName: node.displayName || mapped.displayName,
      engineeringUnit: node.engineeringUnit || mapped.engineeringUnit,
    };
  });
  nodes.forEach((node, index) => {
    if (!node.pointId) {
      errors.push({
        code: 'point_id_missing',
        message: 'pointId is required',
        details: { index },
      });
    }
  });
  return { nodes, errors };
}

export function mapOpcUaNodeToPluginSample(input: {
  connectorId: string;
  sourceSystemId: string;
  sequence: number;
  node: OpcUaSyntheticNode;
}): NormalizedSamplePlaceholder {
  return {
    sampleId: `${input.connectorId}-opcua-${input.sequence}`,
    connectorId: input.connectorId,
    sourceSystemId: input.sourceSystemId,
    protocol: 'opcua',
    sampleType: 'telemetry',
    timestamp: input.node.sourceTimestamp,
    payload: {
      pointId: input.node.pointId,
      nodeId: input.node.nodeId,
      browseName: input.node.browseName,
      displayName: input.node.displayName,
      dataType: input.node.dataType,
      value: input.node.value,
      statusCode: input.node.statusCode,
      sourceTimestamp: input.node.sourceTimestamp,
      serverTimestamp: input.node.serverTimestamp,
      engineeringUnit: input.node.engineeringUnit,
      synthetic: true,
      writeback: false,
    },
  };
}

export function exportOpcUaReadonlyEvidence(path: string, payload: OpcUaReadonlyEvidence): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
