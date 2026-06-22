export type ConnectorStatus =
  | 'configured'
  | 'starting'
  | 'running'
  | 'degraded'
  | 'stopped'
  | 'failed'
  | 'disabled';

export type PluginLifecycleState = 'configured' | 'running' | 'degraded' | 'stopped' | 'disabled';

export type NormalizedMessageType =
  | 'telemetry.point.updated'
  | 'event.created'
  | 'alarm.raised'
  | 'device.health.updated'
  | 'evidence.captured';

export interface ConnectorMetadata {
  readonly id: string;
  readonly name: string;
  readonly protocol: 'bacnet' | 'modbus' | 'opcua' | 'mqtt' | 'vendor-sdk' | 'http';
  readonly edgeId: string;
  readonly siteId: string;
  readonly sourceSystemId: string;
  readonly capabilities: readonly string[];
  readonly enabled: boolean;
  readonly notes?: string;
}

export interface ConnectorRecord {
  readonly metadata: ConnectorMetadata;
  status: ConnectorStatus;
  lastError: string | null;
  lastDataAt: string | null;
  healthStatus: 'healthy' | 'degraded' | 'failed' | 'starting' | 'stopped';
  updatedAt: string;
}

export interface PluginMetadata {
  readonly id: string;
  readonly name: string;
  readonly protocol: 'bacnet' | 'modbus' | 'opcua' | 'mqtt' | 'vendor-sdk';
  readonly version: string;
  readonly capabilities: readonly string[];
  lifecycleState: PluginLifecycleState;
  readonly configSchemaRef?: string;
  enabled: boolean;
  readonly notes?: string;
}

export interface RawTagSample {
  readonly sourceSystemId: string;
  readonly protocol: string;
  readonly rawTag: string;
  readonly rawName: string;
  readonly value: string;
  readonly timestamp: string;
}

export interface CanonicalMappedPoint {
  readonly siteId: string;
  readonly assetCode: string;
  readonly deviceCode: string;
  readonly pointCode: string;
  readonly value: number | string | boolean;
  readonly valueType: 'float' | 'int' | 'string' | 'bool';
  readonly unit: string;
  readonly quality: 'good' | 'uncertain' | 'bad';
  readonly unmappedPolicyApplied?: 'store_raw' | 'drop' | 'quarantine';
}

export interface EdgeLocalEnvelope {
  readonly messageId: string;
  readonly edgeId: string;
  readonly siteId: string;
  readonly sourceSystemId: string;
  readonly connectorId: string;
  readonly messageType: NormalizedMessageType;
  readonly timestamp: string;
  readonly nonce: string;
  readonly payload: Record<string, unknown>;
  readonly trace: {
    readonly traceId: string;
    readonly spanId: string;
  };
  readonly integrity: {
    readonly algorithm: 'sha256';
    readonly checksum: string;
    readonly signature: null;
    readonly signatureStatus: 'disabled';
  };
}

export type BufferState = 'pending' | 'accepted_local' | 'failed' | 'expired' | 'purged';

export interface AuditPlaceholderEvent {
  readonly eventId: string;
  readonly eventType: string;
  readonly actor: 'edge-runtime';
  readonly edgeId: string;
  readonly timestamp: string;
  readonly action: string;
  readonly result: 'ok' | 'error';
  readonly details: Record<string, unknown>;
}

export type EdgeRuntimeMode = 'production' | 'staging' | 'development' | 'diagnostic' | 'maintenance' | 'dry-run';

export type HardwareKeyStatus = 'disabled' | 'missing' | 'implementation_pending' | 'locked' | 'verified';

export interface HardwareKeyGuardState {
  readonly required: boolean;
  readonly provider: string;
  readonly serial: string;
  readonly label: string;
  readonly present: boolean;
  readonly status: HardwareKeyStatus;
  readonly locked: boolean;
  readonly lockedReason: string | null;
  readonly runtimeMode: EdgeRuntimeMode;
}
