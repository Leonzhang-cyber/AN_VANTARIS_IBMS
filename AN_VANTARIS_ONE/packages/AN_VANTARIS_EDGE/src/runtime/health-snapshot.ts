import type { ConnectorRecord, EdgeRuntimeMode, HardwareKeyGuardState, PluginMetadata } from './types.js';

export interface EdgeHealthSnapshot {
  readonly edgeId: string;
  readonly siteId: string;
  readonly version: string;
  readonly runtimeMode: EdgeRuntimeMode;
  readonly connectorCount: number;
  readonly runningConnectorCount: number;
  readonly degradedConnectorCount: number;
  readonly failedConnectorCount: number;
  readonly bufferPendingCount: number;
  readonly bufferFailedCount: number;
  readonly dlqCount: number;
  readonly pluginCount: number;
  readonly pluginIds: readonly string[];
  readonly boundaryMode: 'edge-only';
  readonly lastGeneratedAt: string;
  readonly status: 'healthy' | 'degraded' | 'failed' | 'starting' | 'stopped' | 'locked';
  readonly hardwareKey: {
    readonly required: boolean;
    readonly present: boolean;
    readonly provider: string;
    readonly serial: string;
    readonly status: HardwareKeyGuardState['status'];
  };
  readonly lockedReason: string | null;
}

export function buildHealthSnapshot(input: {
  edgeId: string;
  siteId: string;
  version: string;
  connectors: readonly ConnectorRecord[];
  plugins: readonly PluginMetadata[];
  runtimeMode: EdgeRuntimeMode;
  hardwareKey: HardwareKeyGuardState;
  bufferSummary: {
    pending: number;
    failed: number;
    dlqCount: number;
  };
}): EdgeHealthSnapshot {
  const running = input.connectors.filter((item) => item.status == 'running').length;
  const degraded = input.connectors.filter((item) => item.status == 'degraded').length;
  const failed = input.connectors.filter((item) => item.status == 'failed').length;
  const status: EdgeHealthSnapshot['status'] = input.hardwareKey.locked
    ? 'locked'
    : failed > 0
      ? 'failed'
      : degraded > 0 || input.bufferSummary.failed > 0
        ? 'degraded'
        : 'healthy';

  return {
    edgeId: input.edgeId,
    siteId: input.siteId,
    version: input.version,
    runtimeMode: input.runtimeMode,
    connectorCount: input.connectors.length,
    runningConnectorCount: running,
    degradedConnectorCount: degraded,
    failedConnectorCount: failed,
    bufferPendingCount: input.bufferSummary.pending,
    bufferFailedCount: input.bufferSummary.failed,
    dlqCount: input.bufferSummary.dlqCount,
    pluginCount: input.plugins.length,
    pluginIds: input.plugins.map((item) => item.id),
    boundaryMode: 'edge-only',
    lastGeneratedAt: new Date().toISOString(),
    status,
    hardwareKey: {
      required: input.hardwareKey.required,
      present: input.hardwareKey.present,
      provider: input.hardwareKey.provider,
      serial: input.hardwareKey.serial,
      status: input.hardwareKey.status,
    },
    lockedReason: input.hardwareKey.lockedReason,
  };
}
