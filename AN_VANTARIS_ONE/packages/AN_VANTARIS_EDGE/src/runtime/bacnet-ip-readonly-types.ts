export type BacnetObjectType =
  | 'analogInput'
  | 'analogOutput'
  | 'analogValue'
  | 'binaryInput'
  | 'binaryOutput'
  | 'binaryValue'
  | 'multiStateInput'
  | 'multiStateOutput'
  | 'multiStateValue';

export type BacnetPropertyIdentifier = 'presentValue' | 'statusFlags' | 'reliability' | 'units';

export interface BacnetPointMapping {
  readonly pointId: string;
  readonly objectType: BacnetObjectType;
  readonly objectInstance: number;
  readonly propertyIdentifier: BacnetPropertyIdentifier;
  readonly assetRef: string;
  readonly engineeringUnit: string;
}

export interface BacnetIpReadonlyConfig {
  readonly connectorId: string;
  readonly protocol: 'bacnet-ip-readonly';
  readonly host: string;
  readonly port: number;
  readonly networkEnabled: boolean;
  readonly supportsWriteback: boolean;
  readonly fixturePath: string;
  readonly pollingIntervalMs: number;
  readonly timeoutMs: number;
  readonly retries: number;
  readonly pointMappings: readonly BacnetPointMapping[];
}

export interface BacnetSyntheticDevice {
  readonly deviceId: number;
  readonly name: string;
  readonly address: string;
  readonly vendorName: string;
}

export interface BacnetSyntheticPoint {
  readonly pointId: string;
  readonly objectType: BacnetObjectType;
  readonly objectInstance: number;
  readonly propertyIdentifier: BacnetPropertyIdentifier;
  readonly value: number | string | boolean;
  readonly engineeringUnit: string;
  readonly status: 'good' | 'bad' | 'uncertain';
  readonly timestamp: string;
}

export interface BacnetSyntheticFixture {
  readonly connectorId: string;
  readonly protocol: 'bacnet-ip-readonly';
  readonly networkEnabled: false;
  readonly source: 'synthetic-fixture';
  readonly device: BacnetSyntheticDevice;
  readonly points: readonly BacnetSyntheticPoint[];
}

export interface BacnetIpReadonlyValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface BacnetIpReadonlyError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, unknown>;
}

export interface BacnetIpReadonlyStats {
  readonly pointCount: number;
  readonly validCount: number;
  readonly invalidCount: number;
  readonly bytesRead: number;
  readonly generatedAt: string;
}

export interface BacnetIpReadonlyEvidence {
  readonly generatedAt: string;
  readonly config: BacnetIpReadonlyConfig;
  readonly validation: BacnetIpReadonlyValidationResult;
  readonly parse: {
    readonly ok: boolean;
    readonly errors: readonly BacnetIpReadonlyError[];
    readonly points: readonly BacnetSyntheticPoint[];
    readonly bytesRead: number;
    readonly fixturePath: string;
  };
  readonly stats: BacnetIpReadonlyStats;
  readonly warnings: readonly string[];
}
