import type { ConnectorProtocol } from './connector-types.js';

export type ProtocolPluginRuntimeState = 'created' | 'initialized' | 'running' | 'stopped' | 'failed';

export interface ProtocolPluginCapability {
  readonly protocol: ConnectorProtocol;
  readonly supportsPolling: boolean;
  readonly supportsSubscription: boolean;
  readonly supportsWriteback: boolean;
  readonly supportsDiscovery: boolean;
  readonly supportsDiagnostics: boolean;
  readonly supportsSyntheticData: boolean;
  readonly outputTypes: readonly string[];
}

export interface ProtocolPluginHealth {
  readonly status: 'healthy' | 'degraded' | 'failed' | 'unknown';
  readonly runtimeState: ProtocolPluginRuntimeState;
  readonly lastPollAt: string | null;
  readonly lastError: string | null;
  readonly generatedAt: string;
}

export interface ProtocolPluginError {
  readonly code: string;
  readonly message: string;
  readonly retryable: boolean;
  readonly details?: Record<string, unknown>;
}

export interface NormalizedSamplePlaceholder {
  readonly sampleId: string;
  readonly connectorId: string;
  readonly sourceSystemId: string;
  readonly protocol: ConnectorProtocol;
  readonly sampleType: 'telemetry' | 'event' | 'alarm' | 'health' | 'evidence';
  readonly timestamp: string;
  readonly payload: Record<string, unknown>;
}

export interface ProtocolPluginPollResult {
  readonly pluginId: string;
  readonly connectorId: string;
  readonly protocol: ConnectorProtocol;
  readonly samples: readonly NormalizedSamplePlaceholder[];
  readonly health: ProtocolPluginHealth;
  readonly diagnostics: {
    readonly synthetic: true;
    readonly durationMs: number;
    readonly warnings: readonly string[];
  };
}

export interface ProtocolPluginRuntimeContext {
  readonly edgeId: string;
  readonly siteId: string;
  readonly connectorId: string;
  readonly sourceSystemId: string;
  readonly protocol: ConnectorProtocol;
  readonly now: string;
  readonly metadata: Record<string, unknown>;
}

export interface ProtocolPlugin {
  readonly pluginId: string;
  readonly name: string;
  readonly version: string;
  readonly supportedProtocols: readonly ConnectorProtocol[];
  readonly capability: ProtocolPluginCapability;
  initialize(context: ProtocolPluginRuntimeContext): void;
  start(context: ProtocolPluginRuntimeContext): void;
  stop(context: ProtocolPluginRuntimeContext): void;
  pollOnce(context: ProtocolPluginRuntimeContext): ProtocolPluginPollResult;
  diagnostics(): {
    readonly pluginId: string;
    readonly state: ProtocolPluginRuntimeState;
    readonly lastError: string | null;
    readonly lastPollAt: string | null;
    readonly generatedAt: string;
  };
}
