export type RuntimeHardeningClassification = 'HARDENING_FOUNDATION_ONLY';

export type RuntimeIdentityPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-04';
  readonly classification: RuntimeHardeningClassification;
  readonly runtimeUser: string;
  readonly runtimeGroup: string;
  readonly dedicatedUserRequired: boolean;
  readonly dedicatedGroupRequired: boolean;
  readonly loginShellAllowed: boolean;
  readonly interactiveLoginAllowed: boolean;
  readonly homeDirectoryRequired: boolean;
  readonly rootExecutionAllowed: boolean;
  readonly supplementaryGroups: readonly string[];
  readonly userCreationPerformed: false;
  readonly groupCreationPerformed: false;
  readonly realOwnershipChangePerformed: false;
  readonly productionHardeningApplied: false;
  readonly readinessKey: 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
};

export type FilesystemClassification =
  | 'IMMUTABLE_RELEASE'
  | 'SHARED_CONFIGURATION'
  | 'SHARED_OPERATIONAL_DATA'
  | 'SHARED_BUFFER'
  | 'SHARED_AUDIT'
  | 'SHARED_EVIDENCE'
  | 'SHARED_LOGS'
  | 'SHARED_BACKUPS'
  | 'SHARED_RUNTIME'
  | 'LIFECYCLE_STATE'
  | 'POINTER'
  | 'SECRET_MATERIAL'
  | 'CERTIFICATE_MATERIAL';

export type FilesystemOwnershipEntry = {
  readonly path: string;
  readonly classification: FilesystemClassification;
  readonly owner: string;
  readonly group: string;
  readonly directoryMode: string;
  readonly fileMode: string;
  readonly writableByRuntime: boolean;
  readonly writableByDeployment: boolean;
  readonly mutable: boolean;
  readonly executableAllowed: boolean;
  readonly symlinkAllowed: boolean;
  readonly retentionRequired: boolean;
  readonly sensitive: boolean;
  readonly notes: string;
};

export type FilesystemOwnershipPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-04';
  readonly classification: RuntimeHardeningClassification;
  readonly entries: readonly FilesystemOwnershipEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
};

export type PermissionMatrix = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-04';
  readonly classification: RuntimeHardeningClassification;
  readonly directoryModes: Record<string, string>;
  readonly fileModes: Record<string, string>;
  readonly forbiddenModes: readonly string[];
  readonly forbiddenFlags: readonly string[];
  readonly forbiddenPolicies: readonly string[];
  readonly readinessKey: 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
};

export type SensitiveFilePolicyEntry = {
  readonly category: string;
  readonly allowedLocation: string;
  readonly prohibitedLocation: string;
  readonly owner: string;
  readonly group: string;
  readonly maxFileMode: string;
  readonly plaintextAllowed: false;
  readonly repositoryTrackingAllowed: false;
  readonly runtimeReadAllowed: boolean;
  readonly runtimeWriteAllowed: boolean;
  readonly rotationRequired: boolean;
  readonly provisioningOwner: string;
  readonly status: string;
};

export type SensitiveFilePolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-04';
  readonly classification: RuntimeHardeningClassification;
  readonly realMaterialPresent: false;
  readonly entries: readonly SensitiveFilePolicyEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
};

export type SystemdHardeningRecommendation = {
  readonly setting: string;
  readonly recommendedValue: string;
  readonly appliedByC4_04: false;
  readonly compatibilityReviewRequired: boolean;
  readonly riskAddressed: string;
  readonly notes: string;
};

export type SystemdHardeningPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-04';
  readonly classification: RuntimeHardeningClassification;
  readonly recommendations: readonly SystemdHardeningRecommendation[];
  readonly readinessKey: 'UFMS_EDGE_C4_04_RUNTIME_USER_PERMISSION_FILESYSTEM_HARDENING_PASS';
};

export type RuntimeHardeningAcceptanceResult =
  | 'HARDENING_FOUNDATION_ACCEPTED_NOT_APPLIED'
  | 'HARDENING_FOUNDATION_REJECTED';

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};
