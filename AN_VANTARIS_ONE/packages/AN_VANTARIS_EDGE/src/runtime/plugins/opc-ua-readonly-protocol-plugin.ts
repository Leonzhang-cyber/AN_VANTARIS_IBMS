import type { ConnectorProtocol } from '../connector-types.js';
import type {
  NormalizedSamplePlaceholder,
  ProtocolPlugin,
  ProtocolPluginPollResult,
  ProtocolPluginRuntimeContext,
  ProtocolPluginRuntimeState,
} from '../protocol-plugin-types.js';
import {
  exportOpcUaReadonlyEvidence,
  extractOpcUaNodeRecords,
  mapOpcUaNodeToPluginSample,
  parseOpcUaSyntheticFixture,
  readOpcUaSyntheticFixture,
  validateOpcUaReadonlyConfig,
} from '../opc-ua-readonly-reader.js';
import type { OpcUaReadonlyConfig, OpcUaReadonlyDataType } from '../opc-ua-readonly-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asNumber(value: unknown, fallback: number): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : fallback;
}

function asBoolean(value: unknown, fallback = false): boolean {
  return typeof value == 'boolean' ? value : fallback;
}

function asNodeMappings(
  value: unknown,
): readonly {
  pointId: string;
  nodeId: string;
  browseName: string;
  displayName: string;
  dataType: OpcUaReadonlyDataType;
  engineeringUnit: string;
  assetRef: string;
}[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item) => typeof item == 'object' && item != null)
    .map((item) => {
      const row = item as Record<string, unknown>;
      return {
        pointId: asString(row.pointId),
        nodeId: asString(row.nodeId),
        browseName: asString(row.browseName),
        displayName: asString(row.displayName),
        dataType: (asString(row.dataType) || 'Double') as OpcUaReadonlyDataType,
        engineeringUnit: asString(row.engineeringUnit),
        assetRef: asString(row.assetRef),
      };
    });
}

export class OpcUaReadonlyProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-opc-ua-readonly-runtime';
  public readonly name = 'OPC UA Read-only';
  public readonly version = '0.0.0-c3-06';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['opcua'];
  public readonly capability = {
    protocol: 'opcua' as const,
    supportsPolling: true,
    supportsSubscription: false,
    supportsWriteback: false,
    supportsDiscovery: false,
    supportsDiagnostics: true,
    supportsSyntheticData: true,
    outputTypes: ['telemetry', 'event'],
  };

  private state: ProtocolPluginRuntimeState = 'created';
  private lastError: string | null = null;
  private lastPollAt: string | null = null;
  private lastWarnings: string[] = [];
  private lastConfig: OpcUaReadonlyConfig | null = null;
  private lastEvidencePath: string | null = null;

  public initialize(context: ProtocolPluginRuntimeContext): void {
    this.state = 'initialized';
    this.lastError = null;
    this.lastWarnings = [];
    this.lastConfig = this.buildConfig(context);
  }

  public start(context: ProtocolPluginRuntimeContext): void {
    this.state = 'running';
    this.lastError = null;
    this.lastConfig = this.buildConfig(context);
  }

  public stop(_context: ProtocolPluginRuntimeContext): void {
    this.state = 'stopped';
  }

  public pollOnce(context: ProtocolPluginRuntimeContext): ProtocolPluginPollResult {
    const startedAt = Date.now();
    if (this.state != 'running' && this.state != 'initialized') {
      this.state = 'failed';
      this.lastError = 'poll_once_called_before_start';
      throw new Error('opc ua readonly protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const configValidation = validateOpcUaReadonlyConfig(config);
    const fixtureRead = readOpcUaSyntheticFixture(config);
    const fixtureParsed = fixtureRead.ok ? parseOpcUaSyntheticFixture(fixtureRead.content) : null;
    const extracted =
      fixtureParsed && fixtureParsed.ok && fixtureParsed.fixture
        ? extractOpcUaNodeRecords({ fixture: fixtureParsed.fixture, config })
        : { nodes: [], errors: [] };
    const parseErrors = [...(fixtureRead.errors ?? []), ...(fixtureParsed?.errors ?? []), ...(extracted.errors ?? [])];

    this.lastPollAt = nowIso();
    this.lastWarnings = [...configValidation.errors, ...parseErrors.map((error) => error.message)];
    const samples: NormalizedSamplePlaceholder[] = extracted.nodes.map((node, index) =>
      mapOpcUaNodeToPluginSample({
        connectorId: context.connectorId,
        sourceSystemId: context.sourceSystemId,
        sequence: index + 1,
        node,
      }),
    );

    const evidence = {
      generatedAt: nowIso(),
      config,
      validation: configValidation,
      parse: {
        ok: configValidation.valid && parseErrors.length == 0,
        errors: parseErrors,
        nodes: extracted.nodes,
        bytesRead: fixtureRead.bytesRead,
        fixturePath: fixtureRead.fixturePath,
      },
      stats: {
        nodeCount: extracted.nodes.length + parseErrors.length,
        validCount: extracted.nodes.length,
        invalidCount: parseErrors.length,
        bytesRead: fixtureRead.bytesRead,
        generatedAt: nowIso(),
      },
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = './AN_VANTARIS_EDGE/.runtime/evidence/edge-c3-opc-ua-readonly-connector-evidence.json';
    exportOpcUaReadonlyEvidence(this.lastEvidencePath, evidence);

    if (!configValidation.valid || parseErrors.length > 0 || samples.length == 0) {
      this.state = 'failed';
      this.lastError = this.lastWarnings[0] ?? 'opc_ua_readonly_validation_failed';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'opcua',
      samples,
      health: {
        status: this.lastWarnings.length > 0 ? 'degraded' : 'healthy',
        runtimeState: this.state,
        lastPollAt: this.lastPollAt,
        lastError: this.lastError,
        generatedAt: nowIso(),
      },
      diagnostics: {
        synthetic: true,
        durationMs: Date.now() - startedAt,
        warnings: this.lastWarnings,
      },
    };
  }

  public diagnostics(): {
    readonly pluginId: string;
    readonly state: ProtocolPluginRuntimeState;
    readonly lastError: string | null;
    readonly lastPollAt: string | null;
    readonly generatedAt: string;
  } {
    return {
      pluginId: this.pluginId,
      state: this.state,
      lastError: this.lastError,
      lastPollAt: this.lastPollAt,
      generatedAt: nowIso(),
    };
  }

  private buildConfig(context: ProtocolPluginRuntimeContext): OpcUaReadonlyConfig {
    const metadata = context.metadata ?? {};
    return {
      connectorId: context.connectorId,
      protocol: 'opc-ua-readonly',
      endpointUrl: asString(metadata.endpointUrl) || 'mock://synthetic-opc-ua-server',
      securityMode: 'None',
      securityPolicy: 'None',
      namespaceUri: asString(metadata.namespaceUri) || 'urn:synthetic:opcua:namespace',
      serverApplicationUri: asString(metadata.serverApplicationUri) || 'urn:synthetic:opcua:server',
      networkEnabled: asBoolean(metadata.networkEnabled, false),
      supportsWriteback: asBoolean(metadata.supportsWriteback, false),
      fixturePath: asString(metadata.fixturePath) || 'config/samples/opc-ua-readonly-response.json',
      pollingIntervalMs: asNumber(metadata.pollingIntervalMs, 30000),
      timeoutMs: asNumber(metadata.timeoutMs, 3000),
      retries: asNumber(metadata.retries, 1),
      nodeMappings: asNodeMappings(metadata.nodeMappings),
    };
  }

  private failedResult(
    context: ProtocolPluginRuntimeContext,
    startedAt: number,
    samples: readonly NormalizedSamplePlaceholder[] = [],
  ): ProtocolPluginPollResult {
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'opcua',
      samples,
      health: {
        status: 'failed',
        runtimeState: this.state,
        lastPollAt: this.lastPollAt,
        lastError: this.lastError,
        generatedAt: nowIso(),
      },
      diagnostics: {
        synthetic: true,
        durationMs: Date.now() - startedAt,
        warnings: this.lastWarnings,
      },
    };
  }
}
