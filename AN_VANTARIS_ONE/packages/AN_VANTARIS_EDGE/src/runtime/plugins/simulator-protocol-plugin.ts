import type { ConnectorProtocol } from '../connector-types.js';
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

export class SimulatorProtocolPlugin implements ProtocolPlugin {
  public readonly pluginId = 'plugin-simulator-runtime';
  public readonly name = 'Simulator Protocol Plugin';
  public readonly version = '0.0.0-c2-02';
  public readonly supportedProtocols: readonly ConnectorProtocol[] = ['simulator'];
  public readonly capability = {
    protocol: 'simulator' as const,
    supportsPolling: true,
    supportsSubscription: true,
    supportsWriteback: false,
    supportsDiscovery: true,
    supportsDiagnostics: true,
    supportsSyntheticData: true,
    outputTypes: ['telemetry', 'event', 'alarm', 'health'],
  };

  private state: ProtocolPluginRuntimeState = 'created';
  private lastError: string | null = null;
  private lastPollAt: string | null = null;
  private sequence = 0;

  public initialize(_context: ProtocolPluginRuntimeContext): void {
    this.state = 'initialized';
    this.lastError = null;
  }

  public start(_context: ProtocolPluginRuntimeContext): void {
    this.state = 'running';
    this.lastError = null;
  }

  public stop(_context: ProtocolPluginRuntimeContext): void {
    this.state = 'stopped';
  }

  public pollOnce(context: ProtocolPluginRuntimeContext): ProtocolPluginPollResult {
    const startedAt = Date.now();
    if (this.state != 'running' && this.state != 'initialized') {
      this.state = 'failed';
      this.lastError = 'poll_once_called_before_start';
      throw new Error('simulator protocol plugin must be initialized/started before pollOnce');
    }
    this.sequence += 1;
    this.lastPollAt = nowIso();
    this.state = 'running';

    const sample: NormalizedSamplePlaceholder = {
      sampleId: `${context.connectorId}-sample-${this.sequence}`,
      connectorId: context.connectorId,
      sourceSystemId: context.sourceSystemId,
      protocol: 'simulator',
      sampleType: 'telemetry',
      timestamp: this.lastPollAt,
      payload: {
        sequence: this.sequence,
        value: 20 + this.sequence,
        unit: 'synthetic-unit',
        quality: 'good',
        synthetic: true,
      },
    };

    return {
      pluginId: this.pluginId,
      connectorId: context.connectorId,
      protocol: 'simulator',
      samples: [sample],
      health: {
        status: 'healthy',
        runtimeState: this.state,
        lastPollAt: this.lastPollAt,
        lastError: this.lastError,
        generatedAt: nowIso(),
      },
      diagnostics: {
        synthetic: true,
        durationMs: Date.now() - startedAt,
        warnings: [],
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
}
