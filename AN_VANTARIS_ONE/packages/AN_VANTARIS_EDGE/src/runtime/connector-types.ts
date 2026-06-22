export type ConnectorProtocol = 'snmp' | 'modbus' | 'bacnet' | 'opcua' | 'opc-tcp' | 'http' | 'file' | 'simulator';

export type ConnectorLifecycleState =
  | 'configured'
  | 'validated'
  | 'stopped'
  | 'starting'
  | 'running'
  | 'degraded'
  | 'failed'
  | 'disabled'
  | 'quarantine';

export type ConnectorHealthStatus = 'healthy' | 'degraded' | 'failed' | 'disabled' | 'unknown';

export interface ConnectorRetryPolicy {
  readonly maxRetries: number;
  readonly backoffMs: number;
}

export interface ConnectorDefinition {
  readonly connectorId: string;
  readonly name: string;
  readonly protocol: ConnectorProtocol | string;
  readonly enabled: boolean;
  readonly siteId: string;
  readonly zoneId: string;
  readonly sourceSystemId: string;
  readonly endpointRef: string;
  readonly mappingRef: string;
  readonly capabilityProfile: string;
  readonly pollIntervalSec: number;
  readonly timeoutMs: number;
  readonly retryPolicy: ConnectorRetryPolicy;
  readonly metadata: Record<string, unknown>;
}

export interface ConnectorCapability {
  readonly protocol: ConnectorProtocol;
  readonly supportsPolling: boolean;
  readonly supportsSubscription: boolean;
  readonly supportsTraps: boolean;
  readonly supportsWriteback: boolean;
  readonly supportsDiscovery: boolean;
  readonly supportsHealthCheck: boolean;
  readonly supportsTimeSync: boolean;
  readonly outputTypes: readonly string[];
}

export interface ConnectorRuntimeState {
  readonly connectorId: string;
  readonly protocol: string;
  lifecycleState: ConnectorLifecycleState;
  healthStatus: ConnectorHealthStatus;
  lastStartedAt: string | null;
  lastStoppedAt: string | null;
  lastSeenAt: string | null;
  lastError: string | null;
  messageCount: number;
  errorCount: number;
  quarantineCount: number;
  capabilitySummary: ConnectorCapability;
}

export interface ConnectorValidationResult {
  readonly connectorId: string;
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface ConnectorManagerHealthSnapshot {
  readonly connectorCount: number;
  readonly runningCount: number;
  readonly disabledCount: number;
  readonly failedCount: number;
  readonly quarantineCount: number;
  readonly protocols: readonly string[];
  readonly generatedAt: string;
}
