export type OpcUaReadonlyDataType =
  | 'Boolean'
  | 'Byte'
  | 'Int16'
  | 'UInt16'
  | 'Int32'
  | 'UInt32'
  | 'Int64'
  | 'UInt64'
  | 'Float'
  | 'Double'
  | 'String'
  | 'DateTime';

export interface OpcUaNodeMapping {
  readonly pointId: string;
  readonly nodeId: string;
  readonly browseName: string;
  readonly displayName: string;
  readonly dataType: OpcUaReadonlyDataType;
  readonly engineeringUnit: string;
  readonly assetRef: string;
}

export interface OpcUaReadonlyConfig {
  readonly connectorId: string;
  readonly protocol: 'opc-ua-readonly';
  readonly endpointUrl: string;
  readonly securityMode: 'None';
  readonly securityPolicy: 'None';
  readonly namespaceUri: string;
  readonly serverApplicationUri: string;
  readonly networkEnabled: boolean;
  readonly supportsWriteback: boolean;
  readonly fixturePath: string;
  readonly pollingIntervalMs: number;
  readonly timeoutMs: number;
  readonly retries: number;
  readonly nodeMappings: readonly OpcUaNodeMapping[];
}

export interface OpcUaSyntheticNode {
  readonly pointId: string;
  readonly nodeId: string;
  readonly browseName: string;
  readonly displayName: string;
  readonly dataType: OpcUaReadonlyDataType;
  readonly value: number | string | boolean;
  readonly statusCode: string;
  readonly sourceTimestamp: string;
  readonly serverTimestamp: string;
  readonly engineeringUnit: string;
}

export interface OpcUaSyntheticFixture {
  readonly connectorId: string;
  readonly protocol: 'opc-ua-readonly';
  readonly networkEnabled: false;
  readonly source: 'synthetic-fixture';
  readonly endpointUrl: string;
  readonly securityMode: 'None';
  readonly securityPolicy: 'None';
  readonly namespaceUri: string;
  readonly serverApplicationUri: string;
  readonly nodes: readonly OpcUaSyntheticNode[];
}

export interface OpcUaReadonlyValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface OpcUaReadonlyError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, unknown>;
}

export interface OpcUaReadonlyStats {
  readonly nodeCount: number;
  readonly validCount: number;
  readonly invalidCount: number;
  readonly bytesRead: number;
  readonly generatedAt: string;
}

export interface OpcUaReadonlyEvidence {
  readonly generatedAt: string;
  readonly config: OpcUaReadonlyConfig;
  readonly validation: OpcUaReadonlyValidationResult;
  readonly parse: {
    readonly ok: boolean;
    readonly errors: readonly OpcUaReadonlyError[];
    readonly nodes: readonly OpcUaSyntheticNode[];
    readonly bytesRead: number;
    readonly fixturePath: string;
  };
  readonly stats: OpcUaReadonlyStats;
  readonly warnings: readonly string[];
}
