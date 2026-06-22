import type { ConnectorProtocol } from '../connector-types.js';
import type {
  NormalizedSamplePlaceholder,
  ProtocolPlugin,
  ProtocolPluginPollResult,
  ProtocolPluginRuntimeContext,
  ProtocolPluginRuntimeState,
} from '../protocol-plugin-types.js';
import {
  exportBacnetIpReadonlyEvidence,
  extractBacnetPointRecords,
  mapBacnetPointToPluginSample,
  parseBacnetSyntheticFixture,
  readBacnetSyntheticFixture,
  validateBacnetIpReadonlyConfig,
} from '../bacnet-ip-readonly-reader.js';
import type { BacnetIpReadonlyConfig } from '../bacnet-ip-readonly-types.js';

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

function asPointMappings(
  value: unknown,
): readonly {
  pointId: string;
  objectType:
    | 'analogInput'
    | 'analogOutput'
    | 'analogValue'
    | 'binaryInput'
    | 'binaryOutput'
    | 'binaryValue'
    | 'multiStateInput'
    | 'multiStateOutput'
    | 'multiStateValue';
  objectInstance: number;
  propertyIdentifier: 'presentValue' | 'statusFlags' | 'reliability' | 'units';
  assetRef: string;
  engineeringUnit: string;
}[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item) => typeof item == 'object' && item != null)
    .map((item) => {
      const row = item as Record<string, unknown>;
      return {
        pointId: asString(row.pointId),
        objectType: (asString(row.objectType) || 'analogInput') as
          | 'analogInput'
          | 'analogOutput'
          | 'analogValue'
          | 'binaryInput'
          | 'binaryOutput'
          | 'binaryValue'
          | 'multiStateInput'
          | 'multiStateOutput'
          | 'multiStateValue',
        objectInstance: asNumber(row.objectInstance, 0),
        propertyIdentifier: (asString(row.propertyIdentifier) || 'presentValue') as
          | 'presentValue'
          | 'statusFlags'
          | 'reliability'
          | 'units',
        assetRef: asString(row.assetRef),
        engineeringUnit: asString(row.engineeringUnit),
      };
    });
}

export class BacnetIpReadonlyProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-bacnet-ip-readonly-runtime';
  public readonly name = 'BACnet/IP Read-only';
  public readonly version = '0.0.0-c3-05';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['bacnet'];
  public readonly capability = {
    protocol: 'bacnet' as const,
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
  private lastConfig: BacnetIpReadonlyConfig | null = null;
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
      throw new Error('bacnet ip readonly protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const configValidation = validateBacnetIpReadonlyConfig(config);
    const fixtureRead = readBacnetSyntheticFixture(config);
    const fixtureParsed = fixtureRead.ok ? parseBacnetSyntheticFixture(fixtureRead.content) : null;
    const extracted =
      fixtureParsed && fixtureParsed.ok && fixtureParsed.fixture
        ? extractBacnetPointRecords({ fixture: fixtureParsed.fixture, config })
        : { points: [], errors: [] };
    const parseErrors = [...(fixtureRead.errors ?? []), ...(fixtureParsed?.errors ?? []), ...(extracted.errors ?? [])];

    this.lastPollAt = nowIso();
    this.lastWarnings = [...configValidation.errors, ...parseErrors.map((error) => error.message)];
    const samples: NormalizedSamplePlaceholder[] = extracted.points.map((point, index) =>
      mapBacnetPointToPluginSample({
        connectorId: context.connectorId,
        sourceSystemId: context.sourceSystemId,
        sequence: index + 1,
        point,
      }),
    );

    const evidence = {
      generatedAt: nowIso(),
      config,
      validation: configValidation,
      parse: {
        ok: configValidation.valid && parseErrors.length == 0,
        errors: parseErrors,
        points: extracted.points,
        bytesRead: fixtureRead.bytesRead,
        fixturePath: fixtureRead.fixturePath,
      },
      stats: {
        pointCount: extracted.points.length + parseErrors.length,
        validCount: extracted.points.length,
        invalidCount: parseErrors.length,
        bytesRead: fixtureRead.bytesRead,
        generatedAt: nowIso(),
      },
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = './AN_VANTARIS_EDGE/.runtime/evidence/edge-c3-bacnet-ip-readonly-connector-evidence.json';
    exportBacnetIpReadonlyEvidence(this.lastEvidencePath, evidence);

    if (!configValidation.valid || parseErrors.length > 0 || samples.length == 0) {
      this.state = 'failed';
      this.lastError = this.lastWarnings[0] ?? 'bacnet_ip_readonly_validation_failed';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'bacnet',
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

  private buildConfig(context: ProtocolPluginRuntimeContext): BacnetIpReadonlyConfig {
    const metadata = context.metadata ?? {};
    return {
      connectorId: context.connectorId,
      protocol: 'bacnet-ip-readonly',
      host: asString(metadata.host) || 'mock://synthetic-bacnet-device',
      port: asNumber(metadata.port, 47808),
      networkEnabled: asBoolean(metadata.networkEnabled, false),
      supportsWriteback: asBoolean(metadata.supportsWriteback, false),
      fixturePath: asString(metadata.fixturePath) || 'config/samples/bacnet-ip-readonly-response.json',
      pollingIntervalMs: asNumber(metadata.pollingIntervalMs, 30000),
      timeoutMs: asNumber(metadata.timeoutMs, 3000),
      retries: asNumber(metadata.retries, 1),
      pointMappings: asPointMappings(metadata.pointMappings),
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
      protocol: 'bacnet',
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
