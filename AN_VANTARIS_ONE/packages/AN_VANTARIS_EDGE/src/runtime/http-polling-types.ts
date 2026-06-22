export type HttpPollingMethod = 'GET' | 'POST';

export interface HttpPollingRequestConfig {
  readonly method: HttpPollingMethod;
  readonly url: string;
  readonly headers: Record<string, string>;
  readonly query: Record<string, string | number | boolean>;
  readonly timeoutMs: number;
  readonly intervalMs: number;
  readonly networkEnabled: boolean;
}

export interface HttpPollingConfig {
  readonly connectorId: string;
  readonly endpointRef: string;
  readonly method: HttpPollingMethod;
  readonly url: string;
  readonly headers: Record<string, string>;
  readonly query: Record<string, string | number | boolean>;
  readonly timeoutMs: number;
  readonly intervalMs: number;
  readonly networkEnabled: boolean;
  readonly fixturePath: string;
  readonly responseMapping: {
    readonly observedAtField: string;
    readonly recordsPath: string;
    readonly valueField: string;
    readonly pointRefField: string;
    readonly assetRefField: string;
    readonly qualityField: string;
    readonly metadataField: string;
  };
}

export interface HttpPollingResponseFixture {
  readonly source: string;
  readonly observedAt: string;
  readonly records: readonly Record<string, unknown>[];
}

export interface HttpPollingRecord {
  readonly sourceRef: string;
  readonly pointRef: string;
  readonly assetRef: string;
  readonly value: number | string | boolean;
  readonly unit: string;
  readonly quality: 'good' | 'bad' | 'uncertain';
  readonly observedAt: string;
  readonly metadata: Record<string, unknown>;
}

export interface HttpPollingPollResult {
  readonly ok: boolean;
  readonly connectorId: string;
  readonly endpointRef: string;
  readonly recordCount: number;
  readonly records: readonly HttpPollingRecord[];
  readonly errors: readonly HttpPollingError[];
}

export interface HttpPollingValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface HttpPollingError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, unknown>;
}

export interface HttpPollingStats {
  readonly recordCount: number;
  readonly validCount: number;
  readonly invalidCount: number;
  readonly bytesRead: number;
  readonly generatedAt: string;
}

export interface HttpPollingEvidence {
  readonly generatedAt: string;
  readonly config: HttpPollingConfig;
  readonly validation: HttpPollingValidationResult;
  readonly parse: {
    readonly ok: boolean;
    readonly errors: readonly HttpPollingError[];
    readonly records: readonly HttpPollingRecord[];
    readonly bytesRead: number;
    readonly fixturePath: string;
  };
  readonly stats: HttpPollingStats;
  readonly warnings: readonly string[];
}
