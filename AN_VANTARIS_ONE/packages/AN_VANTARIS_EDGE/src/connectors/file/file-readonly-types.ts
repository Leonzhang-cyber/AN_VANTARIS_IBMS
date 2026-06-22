export type FileDuplicateDetectionMode = 'SHA256_LOCAL_FOUNDATION';
export type FileQuarantineMode = 'DECISION_ONLY';

export type FileQuarantineReason =
  | 'PATH_OUTSIDE_ALLOWLIST'
  | 'PATH_TRAVERSAL_DETECTED'
  | 'SYMLINK_REJECTED'
  | 'FILE_TYPE_NOT_ALLOWED'
  | 'FILE_TOO_LARGE'
  | 'FILE_NOT_STABLE'
  | 'MALFORMED_JSON'
  | 'MALFORMED_CSV'
  | 'DUPLICATE_DETECTED'
  | 'NON_REGULAR_FILE'
  | 'HIDDEN_FILE_REJECTED'
  | 'NETWORK_FILESYSTEM_NOT_ALLOWED';

export type FileReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-01';
  readonly classification: 'CONTROLLED_LOCAL_READ_ONLY_FOUNDATION';
  readonly allowedRoots: readonly string[];
  readonly deniedRoots: readonly string[];
  readonly allowedExtensions: readonly string[];
  readonly maxFileSizeBytes: number;
  readonly rejectTraversal: boolean;
  readonly rejectSymlinks: boolean;
  readonly rejectHiddenFiles: boolean;
  readonly rejectDeviceFiles: boolean;
  readonly rejectSockets: boolean;
  readonly rejectDirectories: boolean;
  readonly requireRegularFile: boolean;
  readonly requireStableSize: boolean;
  readonly stableObservationWindowMs: number;
  readonly duplicateDetectionMode: FileDuplicateDetectionMode;
  readonly quarantineMode: FileQuarantineMode;
  readonly sourceMutationAllowed: false;
  readonly sourceDeletionAllowed: false;
  readonly sourceRenameAllowed: false;
  readonly networkFilesystemAllowed: false;
  readonly csvHeaderRequired: boolean;
  readonly csvDelimiter: ',';
  readonly csvMaxRows: number;
  readonly jsonAllowObject: boolean;
  readonly jsonAllowArray: boolean;
  readonly jsonAllowScalar: boolean;
  readonly jsonMaxDepth: number;
  readonly candidateStatus: 'CONTROLLED_LOCAL_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_01_FILE_IMPORT_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type FileCandidateValidation = {
  readonly ok: boolean;
  readonly canonicalPath: string;
  readonly extension: string;
  readonly sizeBytes: number;
  readonly quarantineReason?: FileQuarantineReason;
  readonly errors: readonly string[];
};

export type FileStabilityEvaluation = {
  readonly stable: boolean;
  readonly reason?: 'FILE_NOT_STABLE' | 'NON_REGULAR_FILE';
  readonly firstSize: number;
  readonly secondSize: number;
  readonly firstMtimeMs: number;
  readonly secondMtimeMs: number;
};

export type FileDigestIdentity = {
  readonly digestSha256: string;
  readonly sizeBytes: number;
  readonly extension: string;
  readonly relativePath?: string;
};

export type FileDuplicateResult = {
  readonly duplicate: boolean;
  readonly identityKey: string;
};

export type FileQuarantineDecision = {
  readonly quarantine: boolean;
  readonly mode: FileQuarantineMode;
  readonly reason?: FileQuarantineReason;
  readonly suggestedTarget?: string;
};

export type ParsedJsonImport = {
  readonly kind: 'json';
  readonly records: readonly Record<string, unknown>[];
};

export type ParsedCsvImport = {
  readonly kind: 'csv';
  readonly headers: readonly string[];
  readonly records: readonly Record<string, string>[];
};

export type ParsedImportResult = ParsedJsonImport | ParsedCsvImport;

export type FileReadOnlyIngestionResult = {
  readonly accepted: boolean;
  readonly canonicalPath: string;
  readonly quarantineDecision: FileQuarantineDecision;
  readonly duplicate: FileDuplicateResult;
  readonly parsed?: ParsedImportResult;
  readonly errors: readonly string[];
};

export type FileImportAcceptanceResult =
  | 'FILE_IMPORT_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'FILE_IMPORT_READ_ONLY_FOUNDATION_REJECTED';
