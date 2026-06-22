import type { ConnectorProtocol } from '../connector-types.js';
import {
  exportHttpPollingEvidence,
  mapHttpPollingRecordToPluginSample,
  runHttpPollingFixtureParse,
  validateHttpPollingConfig,
} from '../http-polling-reader.js';
import type { HttpPollingConfig } from '../http-polling-types.js';
import type {
  NormalizedSamplePlaceholder,
  ProtocolPlugin,
  ProtocolPluginPollResult,
  ProtocolPluginRuntimeContext,
  ProtocolPluginRuntimeState,
} from '../protocol-plugin-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function asString(value: unknown): string {
  return typeof value == 'string' ? value : '';
}

function asBoolean(value: unknown, fallback = false): boolean {
  return typeof value == 'boolean' ? value : fallback;
}

function asNumber(value: unknown, fallback: number): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : fallback;
}

function asMethod(value: unknown): 'GET' | 'POST' {
  return asString(value).toUpperCase() == 'POST' ? 'POST' : 'GET';
}

function asStringRecord(value: unknown): Record<string, string> {
  if (!value || typeof value != 'object') return {};
  const out: Record<string, string> = {};
  for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
    out[key] = typeof item == 'string' ? item : String(item ?? '');
  }
  return out;
}

function asQueryRecord(value: unknown): Record<string, string | number | boolean> {
  if (!value || typeof value != 'object') return {};
  const out: Record<string, string | number | boolean> = {};
  for (const [key, item] of Object.entries(value as Record<string, unknown>)) {
    if (typeof item == 'string' || typeof item == 'number' || typeof item == 'boolean') {
      out[key] = item;
    }
  }
  return out;
}

export class HttpPollingProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-http-polling-runtime';
  public readonly name = 'HTTP Polling Protocol Plugin';
  public readonly version = '0.0.0-c3-02';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['http'];
  public readonly capability = {
    protocol: 'http' as const,
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
  private lastConfig: HttpPollingConfig | null = null;
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
      throw new Error('http polling protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const configValidation = validateHttpPollingConfig(config);
    const parsed = runHttpPollingFixtureParse(config);

    this.lastPollAt = nowIso();
    this.lastWarnings = [...configValidation.errors, ...parsed.errors.map((error) => error.message)];
    const samples: NormalizedSamplePlaceholder[] = parsed.records.map((record, index) =>
      mapHttpPollingRecordToPluginSample({
        connectorId: context.connectorId,
        sourceSystemId: context.sourceSystemId,
        sequence: index + 1,
        record,
      }),
    );

    const evidence = {
      generatedAt: nowIso(),
      config,
      validation: configValidation,
      parse: {
        ok: configValidation.valid && parsed.errors.length == 0,
        errors: parsed.errors,
        records: parsed.records,
        bytesRead: parsed.bytesRead,
        fixturePath: parsed.fixturePath,
      },
      stats: {
        recordCount: parsed.records.length + parsed.errors.length,
        validCount: parsed.records.length,
        invalidCount: parsed.errors.length,
        bytesRead: parsed.bytesRead,
        generatedAt: nowIso(),
      },
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = './AN_VANTARIS_EDGE/.runtime/evidence/edge-c3-http-polling-connector-evidence.json';
    exportHttpPollingEvidence(this.lastEvidencePath, evidence);

    if (!configValidation.valid || parsed.errors.length > 0 || samples.length == 0) {
      this.state = 'failed';
      this.lastError = this.lastWarnings[0] ?? 'http_polling_validation_failed';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'http',
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

  private buildConfig(context: ProtocolPluginRuntimeContext): HttpPollingConfig {
    const metadata = context.metadata ?? {};
    return {
      connectorId: context.connectorId,
      endpointRef: asString(metadata.endpointRef) || 'http-polling-endpoint-placeholder',
      method: asMethod(metadata.method),
      url: asString(metadata.url) || 'mock://synthetic-http-system/points',
      headers: asStringRecord(metadata.headers),
      query: asQueryRecord(metadata.query),
      timeoutMs: asNumber(metadata.timeoutMs, 5000),
      intervalMs: asNumber(metadata.intervalMs, 60_000),
      networkEnabled: asBoolean(metadata.networkEnabled, false),
      fixturePath: asString(metadata.fixturePath) || 'config/samples/http-polling-response.json',
      responseMapping: {
        observedAtField: asString(metadata.observedAtField) || 'observedAt',
        recordsPath: asString(metadata.recordsPath) || 'records',
        valueField: asString(metadata.valueField) || 'value',
        pointRefField: asString(metadata.pointRefField) || 'pointRef',
        assetRefField: asString(metadata.assetRefField) || 'assetRef',
        qualityField: asString(metadata.qualityField) || 'quality',
        metadataField: asString(metadata.metadataField) || 'metadata',
      },
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
      protocol: 'http',
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
