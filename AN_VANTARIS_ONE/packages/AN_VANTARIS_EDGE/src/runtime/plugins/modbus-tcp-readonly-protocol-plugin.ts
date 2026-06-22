import type { ConnectorProtocol } from '../connector-types.js';
import {
  exportModbusTcpReadonlyEvidence,
  extractModbusRegisterRecords,
  mapModbusRegisterToPluginSample,
  parseModbusSyntheticFixture,
  readModbusSyntheticFixture,
  validateModbusTcpReadonlyConfig,
} from '../modbus-tcp-readonly-reader.js';
import type { ModbusTcpReadonlyConfig } from '../modbus-tcp-readonly-types.js';
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

function asRegisterMappings(
  value: unknown,
): readonly {
  registerType: 'holding' | 'input' | 'coil' | 'discrete';
  address: number;
  quantity: number;
  pointRef: string;
  assetRef: string;
  unit: string;
  scale: number;
}[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item) => typeof item == 'object' && item != null)
    .map((item) => {
      const row = item as Record<string, unknown>;
      const registerTypeRaw = asString(row.registerType).toLowerCase();
      const registerType = ['holding', 'input', 'coil', 'discrete'].includes(registerTypeRaw)
        ? registerTypeRaw
        : 'holding';
      return {
        registerType: registerType as 'holding' | 'input' | 'coil' | 'discrete',
        address: asNumber(row.address, 0),
        quantity: asNumber(row.quantity, 1),
        pointRef: asString(row.pointRef),
        assetRef: asString(row.assetRef),
        unit: asString(row.unit),
        scale: asNumber(row.scale, 1),
      };
    });
}

export class ModbusTcpReadonlyProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-modbus-tcp-readonly-runtime';
  public readonly name = 'Modbus TCP Read-only Protocol Plugin';
  public readonly version = '0.0.0-c3-04';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['modbus'];
  public readonly capability = {
    protocol: 'modbus' as const,
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
  private lastConfig: ModbusTcpReadonlyConfig | null = null;
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
      throw new Error('modbus tcp readonly protocol plugin must be initialized/started before pollOnce');
    }
    const config = this.buildConfig(context);
    this.lastConfig = config;
    const configValidation = validateModbusTcpReadonlyConfig(config);
    const fixtureRead = readModbusSyntheticFixture(config);
    const fixtureParsed = fixtureRead.ok ? parseModbusSyntheticFixture(fixtureRead.content) : null;
    const extracted =
      fixtureParsed && fixtureParsed.ok && fixtureParsed.fixture
        ? extractModbusRegisterRecords({ fixture: fixtureParsed.fixture, config })
        : { registers: [], errors: [] };
    const parseErrors = [...(fixtureRead.errors ?? []), ...(fixtureParsed?.errors ?? []), ...(extracted.errors ?? [])];

    this.lastPollAt = nowIso();
    this.lastWarnings = [...configValidation.errors, ...parseErrors.map((error) => error.message)];
    const observedAt = fixtureParsed?.fixture?.observedAt ?? nowIso();
    const samples: NormalizedSamplePlaceholder[] = extracted.registers.map((register, index) =>
      mapModbusRegisterToPluginSample({
        connectorId: context.connectorId,
        sourceSystemId: context.sourceSystemId,
        observedAt,
        sequence: index + 1,
        register,
      }),
    );

    const evidence = {
      generatedAt: nowIso(),
      config,
      validation: configValidation,
      parse: {
        ok: configValidation.valid && parseErrors.length == 0,
        errors: parseErrors,
        registers: extracted.registers,
        bytesRead: fixtureRead.bytesRead,
        fixturePath: fixtureRead.fixturePath,
      },
      stats: {
        registerCount: extracted.registers.length + parseErrors.length,
        validCount: extracted.registers.length,
        invalidCount: parseErrors.length,
        bytesRead: fixtureRead.bytesRead,
        generatedAt: nowIso(),
      },
      warnings: this.lastWarnings,
    };
    this.lastEvidencePath = './AN_VANTARIS_EDGE/.runtime/evidence/edge-c3-modbus-tcp-readonly-connector-evidence.json';
    exportModbusTcpReadonlyEvidence(this.lastEvidencePath, evidence);

    if (!configValidation.valid || parseErrors.length > 0 || samples.length == 0) {
      this.state = 'failed';
      this.lastError = this.lastWarnings[0] ?? 'modbus_tcp_readonly_validation_failed';
      return this.failedResult(context, startedAt, samples);
    }

    this.state = 'running';
    this.lastError = null;
    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'modbus',
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

  private buildConfig(context: ProtocolPluginRuntimeContext): ModbusTcpReadonlyConfig {
    const metadata = context.metadata ?? {};
    return {
      connectorId: context.connectorId,
      host: asString(metadata.host) || 'mock://synthetic-modbus-device',
      port: asNumber(metadata.port, 502),
      unitId: asNumber(metadata.unitId, 1),
      networkEnabled: asBoolean(metadata.networkEnabled, false),
      supportsWriteback: asBoolean(metadata.supportsWriteback, false),
      fixturePath: asString(metadata.fixturePath) || 'config/samples/modbus-tcp-readonly-response.json',
      pollingIntervalMs: asNumber(metadata.pollingIntervalMs, 30_000),
      timeoutMs: asNumber(metadata.timeoutMs, 3_000),
      retries: asNumber(metadata.retries, 1),
      registerMappings: asRegisterMappings(metadata.registerMappings),
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
      protocol: 'modbus',
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
