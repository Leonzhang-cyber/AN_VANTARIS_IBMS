export type SnmpVersion = 'v1' | 'v2c' | 'v3';

export interface SnmpOidMapping {
  readonly oid: string;
  readonly pointRef: string;
  readonly assetRef: string;
  readonly unit: string;
}

export interface SnmpReadonlyConfig {
  readonly connectorId: string;
  readonly host: string;
  readonly port: number;
  readonly version: SnmpVersion;
  readonly community: string;
  readonly networkEnabled: boolean;
  readonly fixturePath: string;
  readonly oidMappings: readonly SnmpOidMapping[];
  readonly pollingIntervalMs: number;
  readonly timeoutMs: number;
  readonly retries: number;
  readonly supportsWriteback: boolean;
  readonly observedAtField: string;
}

export interface SnmpSyntheticVarbind {
  readonly oid: string;
  readonly pointRef: string;
  readonly assetRef: string;
  readonly value: number | string | boolean;
  readonly unit: string;
  readonly quality: 'good' | 'bad' | 'uncertain';
  readonly metadata: Record<string, unknown>;
}

export interface SnmpSyntheticFixture {
  readonly source: string;
  readonly observedAt: string;
  readonly varbinds: readonly SnmpSyntheticVarbind[];
}

export interface SnmpReadonlyPollResult {
  readonly ok: boolean;
  readonly connectorId: string;
  readonly varbindCount: number;
  readonly varbinds: readonly SnmpSyntheticVarbind[];
  readonly errors: readonly SnmpReadonlyError[];
}

export interface SnmpReadonlyValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface SnmpReadonlyError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, unknown>;
}

export interface SnmpReadonlyStats {
  readonly varbindCount: number;
  readonly validCount: number;
  readonly invalidCount: number;
  readonly bytesRead: number;
  readonly generatedAt: string;
}

export interface SnmpReadonlyEvidence {
  readonly generatedAt: string;
  readonly config: SnmpReadonlyConfig;
  readonly validation: SnmpReadonlyValidationResult;
  readonly parse: {
    readonly ok: boolean;
    readonly errors: readonly SnmpReadonlyError[];
    readonly varbinds: readonly SnmpSyntheticVarbind[];
    readonly bytesRead: number;
    readonly fixturePath: string;
  };
  readonly stats: SnmpReadonlyStats;
  readonly warnings: readonly string[];
}
