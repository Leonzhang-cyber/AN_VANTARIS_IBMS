export type SbomComponentType =
  | 'FIRST_PARTY_SOURCE'
  | 'NODE_RUNTIME'
  | 'NODE_PRODUCTION_DEPENDENCY'
  | 'NODE_DEVELOPMENT_DEPENDENCY'
  | 'OS_REQUIRED_DEPENDENCY'
  | 'OS_OPTIONAL_SECURITY_DEPENDENCY'
  | 'CONNECTOR_FOUNDATION_DEPENDENCY'
  | 'HSM_FOUNDATION_DEPENDENCY'
  | 'SYSTEMD_TEMPLATE'
  | 'CONFIGURATION_ARTIFACT'
  | 'DEPLOYMENT_SCRIPT'
  | 'DOCUMENTATION'
  | 'EVIDENCE';

export type SbomScope =
  | 'RUNTIME'
  | 'BUILD'
  | 'TEST'
  | 'DEPLOYMENT'
  | 'SECURITY'
  | 'CONNECTOR'
  | 'DOCUMENTATION';

export type SbomRiskClassification = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNASSESSED';
export type SbomLicenseStatus =
  | 'DECLARED'
  | 'INFERRED_FROM_LOCAL_METADATA'
  | 'UNKNOWN'
  | 'NOT_APPLICABLE'
  | 'REQUIRES_REVIEW';
export type SbomProvenanceStatus =
  | 'FIRST_PARTY'
  | 'LOCKFILE_DECLARED'
  | 'STATIC_DECLARATION'
  | 'LOCAL_PLATFORM_DECLARATION'
  | 'PLACEHOLDER'
  | 'UNRESOLVED';

export type SbomComponentEntry = {
  readonly componentId: string;
  readonly name: string;
  readonly version: string;
  readonly type: SbomComponentType;
  readonly supplier: string;
  readonly source: string;
  readonly scope: SbomScope;
  readonly required: boolean;
  readonly runtimeRequired: boolean;
  readonly developmentOnly: boolean;
  readonly optional: boolean;
  readonly licenseDeclared: string;
  readonly licenseStatus: SbomLicenseStatus;
  readonly provenanceStatus: SbomProvenanceStatus;
  readonly integrityReference: string;
  readonly riskClassification: SbomRiskClassification;
  readonly notes: string;
};

export type ComponentInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly product: 'AN_VANTARIS_EDGE';
  readonly classification: 'SBOM_FOUNDATION_ONLY';
  readonly productionSbom: false;
  readonly sbomStandard: 'INTERNAL_FOUNDATION';
  readonly sourceCommit: string;
  readonly generationMode: 'OFFLINE_DETERMINISTIC';
  readonly networkLookupPerformed: false;
  readonly vulnerabilityScanPerformed: false;
  readonly licenseLegalReviewPerformed: false;
  readonly components: readonly SbomComponentEntry[];
  readonly componentCount: number;
  readonly aggregateDigest: string;
  readonly acceptanceResult: 'SBOM_FOUNDATION_ACCEPTED_NOT_PRODUCTION';
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type NodeDependencyStatus =
  | 'CONFIRMED'
  | 'DECLARED_NOT_CONFIRMED'
  | 'TRANSITIVE'
  | 'BUILT_IN'
  | 'NOT_REQUIRED_BY_EDGE'
  | 'UNRESOLVED';

export type NodeDependencyType = 'production' | 'development' | 'optional' | 'built-in';

export type NodeDependencyEntry = {
  readonly packageName: string;
  readonly declaredVersion: string;
  readonly resolvedVersion: string;
  readonly dependencyType: NodeDependencyType;
  readonly direct: boolean;
  readonly transitive: boolean;
  readonly usedByEdge: boolean;
  readonly usageEvidence: string;
  readonly license: string;
  readonly integrity: string;
  readonly productionRequired: boolean;
  readonly status: NodeDependencyStatus;
};

export type NodeDependencyInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly packageManager: 'npm';
  readonly lockfileVersion: number;
  readonly nodeVersionDeclarationPresent: boolean;
  readonly nodeVersionDeclarationRisk: string;
  readonly inventoryMode: 'LOCAL_LOCKFILE_ONLY';
  readonly dependencies: readonly NodeDependencyEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type OsDependencyEntry = {
  readonly package: string;
  readonly category: 'OS_REQUIRED_DEPENDENCY' | 'OS_OPTIONAL_SECURITY_DEPENDENCY' | 'NODE_RUNTIME_DECLARATION';
  readonly required: boolean;
  readonly productionRequired: boolean;
  readonly installPerformed: false;
  readonly versionPinned: boolean;
  readonly declaredVersion: string;
  readonly purpose: string;
  readonly sourceFile: string;
  readonly status: 'DECLARED' | 'UNRESOLVED';
};

export type OsDependencyInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly inventoryMode: 'STATIC_DECLARATION_ONLY';
  readonly dependencies: readonly OsDependencyEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type ConnectorDependencyEntry = {
  readonly registryKey: 'file' | 'http' | 'snmp' | 'modbus' | 'bacnet' | 'opcua';
  readonly productProtocol: string;
  readonly currentMaturity: 'FOUNDATION_READY';
  readonly syntheticFixtureOnly: true;
  readonly realConnectivityEnabled: false;
  readonly productionDependencyIncluded: false;
  readonly requiredRuntimeDependencies: readonly string[];
  readonly deferredProductionDependencies: readonly string[];
  readonly prohibitedWriteDependencies: readonly string[];
  readonly enablementGate: 'C5-00';
  readonly notes: string;
};

export type ConnectorDependencyInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly connectors: readonly ConnectorDependencyEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type SecurityDependencyEntry = {
  readonly dependency: string;
  readonly status: string;
  readonly requiredPhase: string;
  readonly installedByC4_03: false;
  readonly configured: false;
  readonly productionEnabled: false;
  readonly owner: string;
  readonly risk: SbomRiskClassification | 'UNASSESSED';
  readonly notes: string;
};

export type SecurityDependencyInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly dependencies: readonly SecurityDependencyEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type LicenseEntry = {
  readonly componentId: string;
  readonly componentName: string;
  readonly declaredLicense: string;
  readonly evidenceSource: string;
  readonly legalReviewStatus: 'NOT_REQUIRED_FIRST_PARTY' | 'PENDING' | 'UNKNOWN' | 'APPROVED';
  readonly distributionRisk: SbomRiskClassification;
  readonly actionRequired: string;
};

export type LicenseInventory = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly disclaimer: {
    readonly notLegalAdvice: true;
    readonly onlineLicenseVerificationPerformed: false;
    readonly formalDistributionReviewCompleted: false;
  };
  readonly licenses: readonly LicenseEntry[];
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type VulnerabilityAssessment = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C4-03';
  readonly assessmentMode: 'OFFLINE_METADATA_ONLY';
  readonly networkScanPerformed: false;
  readonly registryAuditPerformed: false;
  readonly nvdLookupPerformed: false;
  readonly osvLookupPerformed: false;
  readonly npmAuditPerformed: false;
  readonly knownVulnerabilities: readonly unknown[];
  readonly assessmentStatus: 'NOT_SCANNED';
  readonly productionAcceptance: false;
  readonly notes: string;
  readonly readinessKey: 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
};

export type SbomAcceptanceResult = 'SBOM_FOUNDATION_ACCEPTED_NOT_PRODUCTION' | 'SBOM_FOUNDATION_REJECTED';

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};
