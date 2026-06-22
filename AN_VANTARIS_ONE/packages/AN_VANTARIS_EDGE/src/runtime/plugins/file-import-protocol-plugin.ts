import type { ConnectorProtocol } from '../connector-types.js';
import {
  exportFileImportEvidence,
  parseFileImportFromConfig,
  validateFileImportPath,
} from '../file-import-reader.js';
import type { FileImportConfig } from '../file-import-types.js';
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

function asNumber(value: unknown, fallback: number): number {
  return typeof value == 'number' && Number.isFinite(value) ? value : fallback;
}

export class FileImportProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-file-import-runtime';
  public readonly name = 'File Import Protocol Plugin';
  public readonly version = '0.0.0-c3-01';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['file'];
  public readonly capability = {
    protocol: 'file' as const,
    supportsPolling: true,
    supportsSubscription: false,
    supportsWriteback: false,
    supportsDiscovery: false,
    supportsDiagnostics: true,
    supportsSyntheticData: true,
    outputTypes: ['telemetry', 'event', 'evidence'],
  };

  private state: ProtocolPluginRuntimeState = 'created';
  private lastError: string | null = null;
  private lastPollAt: string | null = null;
  private lastWarnings: string[] = [];
  private lastConfig: FileImportConfig | null = null;
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
      throw new Error('file import protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const pathCheck = validateFileImportPath(config.edgeRoot, config.samplePath);
    if (!pathCheck.valid) {
      this.state = 'failed';
      this.lastError = pathCheck.errors.join('; ');
      this.lastWarnings = [...pathCheck.errors];
      this.lastPollAt = nowIso();
      return this.failedResult(context, startedAt);
    }

    const parsed = parseFileImportFromConfig(config);
    this.lastPollAt = nowIso();
    this.lastWarnings = parsed.parseResult.validationErrors.map((error) => error.message);
    const samples: NormalizedSamplePlaceholder[] = parsed.parseResult.records.map((record, index) => ({
      sampleId: `${context.connectorId}-file-${index + 1}`,
      connectorId: context.connectorId,
      sourceSystemId: context.sourceSystemId,
      protocol: 'file',
      sampleType: record.sampleType ?? 'telemetry',
      timestamp: record.observedAt,
      payload: {
        sourceRef: record.sourceRef,
        pointRef: record.pointRef,
        value: record.value,
        unit: record.unit,
        quality: record.quality,
        assetRef: record.assetRef,
        message: record.message ?? `file import sample ${index + 1}`,
        metadata: record.metadata,
        synthetic: true,
      },
    }));

    const evidence = {
      generatedAt: nowIso(),
      config,
      parseResult: parsed.parseResult,
      stats: parsed.stats,
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = `${config.edgeRoot}/.runtime/evidence/edge-c3-file-import-connector-evidence.json`;
    exportFileImportEvidence(this.lastEvidencePath, evidence);

    if (!parsed.parseResult.ok || samples.length == 0) {
      this.state = 'failed';
      this.lastError = parsed.parseResult.validationErrors[0]?.message ?? 'no_valid_file_import_records';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'file',
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

  private buildConfig(context: ProtocolPluginRuntimeContext): FileImportConfig {
    const metadata = context.metadata ?? {};
    return {
      edgeRoot: asString(metadata.edgeRoot) || './AN_VANTARIS_EDGE',
      samplePath: asString(metadata.samplePath) || 'config/samples/file-import-sample.jsonl',
      format: asString(metadata.format).toLowerCase() == 'json' ? 'json' : 'jsonl',
      maxBytes: asNumber(metadata.maxBytes, 1024 * 1024),
      maxJsonlLines: asNumber(metadata.maxJsonlLines, 5000),
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
      protocol: 'file',
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
