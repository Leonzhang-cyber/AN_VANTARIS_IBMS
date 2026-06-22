import type { ConnectorProtocol } from '../connector-types.js';
import {
  exportSnmpReadonlyEvidence,
  extractSnmpVarbindRecords,
  mapSnmpVarbindToPluginSample,
  parseSnmpSyntheticFixture,
  readSnmpSyntheticFixture,
  validateSnmpReadonlyConfig,
} from '../snmp-readonly-reader.js';
import type { SnmpReadonlyConfig } from '../snmp-readonly-types.js';
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

function asBoolean(value: unknown, fallback = false): boolean {
  return typeof value == 'boolean' ? value : fallback;
}

function asVersion(value: unknown): 'v1' | 'v2c' | 'v3' {
  const normalized = asString(value).toLowerCase();
  if (normalized == 'v1') return 'v1';
  if (normalized == 'v3') return 'v3';
  return 'v2c';
}

function asOidMappings(value: unknown): readonly { oid: string; pointRef: string; assetRef: string; unit: string }[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item) => typeof item == 'object' && item != null)
    .map((item) => {
      const row = item as Record<string, unknown>;
      return {
        oid: asString(row.oid),
        pointRef: asString(row.pointRef),
        assetRef: asString(row.assetRef),
        unit: asString(row.unit),
      };
    });
}

export class SnmpReadonlyProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-snmp-readonly-runtime';
  public readonly name = 'SNMP Read-only Protocol Plugin';
  public readonly version = '0.0.0-c3-03';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['snmp'];
  public readonly capability = {
    protocol: 'snmp' as const,
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
  private lastConfig: SnmpReadonlyConfig | null = null;
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
      throw new Error('snmp readonly protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const configValidation = validateSnmpReadonlyConfig(config);
    const fixtureRead = readSnmpSyntheticFixture(config);
    const fixtureParsed = fixtureRead.ok ? parseSnmpSyntheticFixture(fixtureRead.content) : null;
    const extracted =
      fixtureParsed && fixtureParsed.ok && fixtureParsed.fixture
        ? extractSnmpVarbindRecords({ fixture: fixtureParsed.fixture, config })
        : { varbinds: [], errors: [] };
    const parseErrors = [
      ...(fixtureRead.errors ?? []),
      ...(fixtureParsed?.errors ?? []),
      ...(extracted.errors ?? []),
    ];

    this.lastPollAt = nowIso();
    this.lastWarnings = [...configValidation.errors, ...parseErrors.map((error) => error.message)];
    const observedAt = fixtureParsed?.fixture?.observedAt ?? nowIso();
    const samples: NormalizedSamplePlaceholder[] = extracted.varbinds.map((varbind, index) =>
      mapSnmpVarbindToPluginSample({
        connectorId: context.connectorId,
        sourceSystemId: context.sourceSystemId,
        observedAt,
        sequence: index + 1,
        varbind,
      }),
    );

    const evidence = {
      generatedAt: nowIso(),
      config,
      validation: configValidation,
      parse: {
        ok: configValidation.valid && parseErrors.length == 0,
        errors: parseErrors,
        varbinds: extracted.varbinds,
        bytesRead: fixtureRead.bytesRead,
        fixturePath: fixtureRead.fixturePath,
      },
      stats: {
        varbindCount: extracted.varbinds.length + parseErrors.length,
        validCount: extracted.varbinds.length,
        invalidCount: parseErrors.length,
        bytesRead: fixtureRead.bytesRead,
        generatedAt: nowIso(),
      },
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = './AN_VANTARIS_EDGE/.runtime/evidence/edge-c3-snmp-readonly-connector-evidence.json';
    exportSnmpReadonlyEvidence(this.lastEvidencePath, evidence);

    if (!configValidation.valid || parseErrors.length > 0 || samples.length == 0) {
      this.state = 'failed';
      this.lastError = this.lastWarnings[0] ?? 'snmp_readonly_validation_failed';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'snmp',
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

  private buildConfig(context: ProtocolPluginRuntimeContext): SnmpReadonlyConfig {
    const metadata = context.metadata ?? {};
    return {
      connectorId: context.connectorId,
      host: asString(metadata.host) || 'mock://synthetic-snmp-device',
      port: asNumber(metadata.port, 161),
      version: asVersion(metadata.version),
      community: asString(metadata.community) || 'synthetic-public-readonly',
      networkEnabled: asBoolean(metadata.networkEnabled, false),
      fixturePath: asString(metadata.fixturePath) || 'config/samples/snmp-readonly-response.json',
      oidMappings: asOidMappings(metadata.oidMappings),
      pollingIntervalMs: asNumber(metadata.pollingIntervalMs, 30_000),
      timeoutMs: asNumber(metadata.timeoutMs, 3_000),
      retries: asNumber(metadata.retries, 1),
      supportsWriteback: asBoolean(metadata.supportsWriteback, false),
      observedAtField: asString(metadata.observedAtField) || 'observedAt',
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
      protocol: 'snmp',
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
