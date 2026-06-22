export type FileImportFormat = 'json' | 'jsonl';

export interface FileImportConfig {
  readonly edgeRoot: string;
  readonly samplePath: string;
  readonly format: FileImportFormat;
  readonly maxBytes: number;
  readonly maxJsonlLines: number;
}

export interface FileImportRecord {
  readonly sourceRef: string;
  readonly pointRef: string;
  readonly value: number | string | boolean;
  readonly unit: string;
  readonly quality: 'good' | 'bad' | 'uncertain';
  readonly observedAt: string;
  readonly assetRef: string;
  readonly metadata: Record<string, unknown>;
  readonly sampleType?: 'telemetry' | 'event' | 'alarm' | 'health' | 'evidence';
  readonly message?: string;
}

export interface FileImportValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface FileImportParseResult {
  readonly ok: boolean;
  readonly format: FileImportFormat;
  readonly records: readonly FileImportRecord[];
  readonly validationErrors: readonly FileImportError[];
  readonly bytesRead: number;
  readonly lineCount: number;
  readonly sourcePath: string;
}

export interface FileImportError {
  readonly code: string;
  readonly message: string;
  readonly line?: number;
  readonly details?: Record<string, unknown>;
}

export interface FileImportStats {
  readonly recordsRead: number;
  readonly recordsValid: number;
  readonly recordsInvalid: number;
  readonly bytesRead: number;
  readonly lineCount: number;
  readonly generatedAt: string;
}

export interface FileImportEvidence {
  readonly generatedAt: string;
  readonly config: FileImportConfig;
  readonly parseResult: FileImportParseResult;
  readonly stats: FileImportStats;
  readonly warnings: readonly string[];
}
