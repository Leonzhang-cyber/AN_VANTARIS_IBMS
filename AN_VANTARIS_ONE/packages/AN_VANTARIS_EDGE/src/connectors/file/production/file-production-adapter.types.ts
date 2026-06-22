export type FileProductionAdapterMode = 'PRODUCTION_FILE_READONLY';

export type FileProductionFormat = 'json' | 'jsonl' | 'csv';

export type FileProductionFormulaPrefixPolicy = 'REJECT' | 'MARK';

export type FileProductionDangerousKeyPolicy = 'REJECT';

export type FileProductionEncoding = 'utf-8';

export type FileProductionErrorCode =
  | 'FILE_PATH_NOT_ALLOWLISTED'
  | 'FILE_PATH_TRAVERSAL_REJECTED'
  | 'FILE_SYMLINK_REJECTED'
  | 'FILE_SPECIAL_TYPE_REJECTED'
  | 'FILE_NOT_FOUND'
  | 'FILE_NOT_REGULAR'
  | 'FILE_SIZE_LIMIT_EXCEEDED'
  | 'FILE_LINE_LIMIT_EXCEEDED'
  | 'FILE_RECORD_LIMIT_EXCEEDED'
  | 'FILE_FORMAT_NOT_ALLOWED'
  | 'FILE_ENCODING_INVALID'
  | 'FILE_JSON_INVALID'
  | 'FILE_JSONL_INVALID'
  | 'FILE_CSV_INVALID'
  | 'FILE_FORMULA_PREFIX_REJECTED'
  | 'FILE_DANGEROUS_KEY_REJECTED'
  | 'FILE_CHANGED_DURING_OPEN'
  | 'FILE_READ_TIMEOUT'
  | 'FILE_READ_FAILED'
  | 'FILE_FOUNDATION_VALIDATION_FAILED'
  | 'FILE_ADAPTER_DISABLED'
  | 'FILE_CONFIG_INVALID';

export type FileProductionResourceLimits = {
  readonly maxFileBytes: number;
  readonly maxLineBytes: number;
  readonly maxRecordCount: number;
  readonly maxJsonDepth: number;
  readonly maxFieldCount: number;
  readonly maxFieldLength: number;
  readonly maxCsvColumns: number;
  readonly maxProcessingMilliseconds: number;
};

export type FileProductionAdapterConfig = {
  readonly adapterMode: FileProductionAdapterMode;
  readonly enabled: boolean;
  readonly rootReferenceId: string;
  readonly inputRelativePath: string;
  readonly format: FileProductionFormat;
  readonly encoding: FileProductionEncoding;
  readonly formulaPrefixPolicy: FileProductionFormulaPrefixPolicy;
  readonly dangerousKeyPolicy: FileProductionDangerousKeyPolicy;
} & FileProductionResourceLimits;

export type FileProductionRootResolver = (rootReferenceId: string) => string | undefined;

export type FileProductionReadRequest = {
  readonly config: FileProductionAdapterConfig;
  readonly resolveRoot: FileProductionRootResolver;
};

export type FileProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type FileProductionReadSuccess = {
  readonly ok: true;
  readonly pathReferenceId: string;
  readonly relativeAllowlistPath: string;
  readonly format: FileProductionFormat;
  readonly recordCount: number;
  readonly records: readonly FileProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type FileProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: FileProductionErrorCode;
  readonly pathReferenceId?: string;
  readonly lineNumber?: number;
};

export type FileProductionReadResult = FileProductionReadSuccess | FileProductionReadFailure;

export type FileProductionReadOnlyAdapter = {
  readonly readOnce: (request: FileProductionReadRequest) => Promise<FileProductionReadResult>;
};

export const FILE_PRODUCTION_LIMIT_CAPS: FileProductionResourceLimits = {
  maxFileBytes: 10_485_760,
  maxLineBytes: 1_048_576,
  maxRecordCount: 10_000,
  maxJsonDepth: 32,
  maxFieldCount: 256,
  maxFieldLength: 8_192,
  maxCsvColumns: 128,
  maxProcessingMilliseconds: 30_000,
};

export const FILE_PRODUCTION_DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;

export const FILE_PRODUCTION_FORMULA_PREFIXES = ['=', '+', '-', '@'] as const;
