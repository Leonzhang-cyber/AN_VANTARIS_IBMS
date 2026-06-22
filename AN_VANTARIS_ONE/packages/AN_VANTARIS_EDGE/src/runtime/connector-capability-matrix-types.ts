export type ConnectorMatrixCategory = 'file-import' | 'http-polling' | 'industrial-readonly';
export type ConnectorMatrixDirection = 'ingest-readonly';
export type ConnectorFoundationStatus = 'foundation-ready';

export interface ConnectorCapabilityMatrixEntry {
  readonly protocolKey: string;
  readonly displayName: string;
  readonly category: ConnectorMatrixCategory;
  readonly direction: ConnectorMatrixDirection;
  readonly networkEnabled: boolean;
  readonly supportsWriteback: boolean;
  readonly syntheticFixtureOnly: boolean;
  readonly realConnectivityEnabled: boolean;
  readonly fixturePath: string;
  readonly configValidation: boolean;
  readonly normalizationSupported: boolean;
  readonly envelopeSupported: boolean;
  readonly localBufferSupported: boolean;
  readonly deliveryPreviewSupported: boolean;
  readonly auditSupported: boolean;
  readonly diagnosticsSupported: boolean;
  readonly productionDependencyIncluded: boolean;
  readonly productionDependencyName: string;
  readonly productionEnablementGate: string;
  readonly readinessKey: string;
  readonly foundationStatus: ConnectorFoundationStatus;
}

export interface ConnectorCapabilityMatrixSnapshot {
  readonly generatedAt: string;
  readonly scope: 'c3-foundation-freeze';
  readonly connectors: readonly ConnectorCapabilityMatrixEntry[];
}
