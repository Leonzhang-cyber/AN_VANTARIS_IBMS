export type ReleaseClassification = 'FOUNDATION_ONLY';
export type SignatureMode = 'SYNTHETIC_METADATA_ONLY';
export type ChecksumAlgorithm = 'SHA-256';

export type ReleaseInventorySourceCategory =
  | 'src'
  | 'config'
  | 'deploy'
  | 'scripts'
  | 'docs'
  | 'evidence';

export type ReleaseFileInventoryEntry = {
  readonly relativePath: string;
  readonly sizeBytes: number;
  readonly sha256: string;
  readonly classification: 'REQUIRED_RUNTIME' | 'REQUIRED_CONFIG' | 'RELEASE_METADATA' | 'DOCUMENTATION';
  readonly executable: boolean;
  readonly required: boolean;
  readonly sourceCategory: ReleaseInventorySourceCategory;
};

export type ReleaseManifest = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-02';
  readonly releaseId: string;
  readonly product: 'AN_VANTARIS_EDGE';
  readonly releaseVersion: string;
  readonly releaseClassification: ReleaseClassification;
  readonly productionRelease: boolean;
  readonly generatedAt: string;
  readonly sourceCommit: string;
  readonly platform: {
    readonly os: readonly string[];
    readonly architectures: readonly string[];
  };
  readonly fileInventory: readonly ReleaseFileInventoryEntry[];
  readonly checksumAlgorithm: ChecksumAlgorithm;
  readonly signatureRequiredForProduction: boolean;
  readonly productionSignaturePresent: boolean;
  readonly signatureMode: SignatureMode;
  readonly sbomPresent: boolean;
  readonly readinessKey: 'UFMS_EDGE_C4_02_RELEASE_MANIFEST_CHECKSUM_SIGNATURE_FOUNDATION_PASS';
};

export type ChecksumEntry = {
  readonly path: string;
  readonly sizeBytes: number;
  readonly sha256: string;
};

export type ChecksumManifest = {
  readonly schemaVersion: '1.0';
  readonly algorithm: ChecksumAlgorithm;
  readonly releaseId: string;
  readonly sourceCommit: string;
  readonly generatedAt: string;
  readonly files: readonly ChecksumEntry[];
  readonly fileCount: number;
  readonly aggregateDigest: string;
  readonly productionCertification: boolean;
  readonly readinessKey: 'UFMS_EDGE_C4_02_RELEASE_MANIFEST_CHECKSUM_SIGNATURE_FOUNDATION_PASS';
};

export type SignatureMetadata = {
  readonly schemaVersion: '1.0';
  readonly releaseId: string;
  readonly signatureStatus: 'NOT_PRODUCTION_SIGNED';
  readonly signatureMode: SignatureMode;
  readonly algorithm: string;
  readonly signerIdentity: {
    readonly type: 'PLACEHOLDER';
    readonly id: string;
  };
  readonly keyReference: string;
  readonly certificateChainPresent: boolean;
  readonly detachedSignaturePresent: boolean;
  readonly hsmBacked: boolean;
  readonly pkcs11Backed: boolean;
  readonly verificationPerformed: boolean;
  readonly productionCertification: boolean;
};

export type SignatureVerificationPolicy = {
  readonly schemaVersion: '1.0';
  readonly policyId: string;
  readonly productionRequirements: {
    readonly requiresDetachedSignature: boolean;
    readonly requiresTrustedSignerIdentity: boolean;
    readonly requiresCertificateOrKeyTrustDecision: boolean;
    readonly requiresChecksumVerificationBeforeSignature: boolean;
    readonly blocksInstallOnSignatureFailure: boolean;
    readonly blocksInstallOnUnknownSigner: boolean;
    readonly blocksInstallOnUnsignedProductionRelease: boolean;
    readonly noFallbackToUnsignedProductionInstall: boolean;
  };
  readonly foundationBehavior: {
    readonly scaffoldVerificationAllowed: boolean;
    readonly maxReachableState: 'SIGNATURE_METADATA_VALID';
    readonly productionSignatureVerifiedReachable: false;
  };
  readonly states: readonly [
    'SCAFFOLD_VERIFIED',
    'CHECKSUM_VERIFIED',
    'SIGNATURE_METADATA_VALID',
    'PRODUCTION_SIGNATURE_VERIFIED',
  ];
  readonly deferredControls: readonly string[];
};

export type ReleaseAcceptancePolicy = {
  readonly schemaVersion: '1.0';
  readonly policyId: string;
  readonly foundationRequirements: readonly string[];
  readonly productionRequirements: readonly string[];
  readonly foundationResult: 'FOUNDATION_ACCEPTED_NOT_PRODUCTION';
};

export type ReleaseAcceptanceResult =
  | 'FOUNDATION_ACCEPTED_NOT_PRODUCTION'
  | 'FOUNDATION_REJECTED'
  | 'PRODUCTION_REJECTED_UNSIGNED';

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};
