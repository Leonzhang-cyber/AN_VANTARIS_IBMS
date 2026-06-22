export type EdgeAuditSnapshotClassification = 'AUDIT_SNAPSHOT';

export type EdgeAuditRiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export type EdgeAuditOwner =
  | 'EDGE'
  | 'LINK'
  | 'DB'
  | 'CONSOLE'
  | 'CONTRACTS'
  | 'NEXUS_AI'
  | 'UFMS'
  | 'VANTARIS_ONE'
  | 'SHARED_GOVERNANCE'
  | 'REQUIRES_DECISION';

export type EdgeFoundationStatus = 'foundation-ready';

export type EdgeConnectorAuditEntry = {
  readonly productProtocol:
    | 'file-import'
    | 'http-polling'
    | 'snmp-readonly'
    | 'modbus-tcp-readonly'
    | 'bacnet-ip-readonly'
    | 'opc-ua-readonly';
  readonly registryKey: 'file' | 'http' | 'snmp' | 'modbus' | 'bacnet' | 'opcua';
  readonly foundationStatus: EdgeFoundationStatus;
  readonly syntheticFixtureOnly: true;
  readonly realConnectivityEnabled: false;
  readonly supportsWriteback: false;
  readonly productionDependencyIncluded: false;
};

export type EdgeProductionBlockerA0 = {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly risk: EdgeAuditRiskLevel;
};

export type EdgeNextDevelopmentTaskA0 = {
  readonly order: number;
  readonly code:
    | 'C4-01'
    | 'C4-02'
    | 'C4-03'
    | 'C4-04'
    | 'C4-05'
    | 'C4-06'
    | 'C5-00'
    | 'C5-01'
    | 'C5-02'
    | 'C6';
  readonly title: string;
  readonly purpose: string;
  readonly prerequisites: readonly string[];
  readonly allowedScope: readonly string[];
  readonly prohibitedScope: readonly string[];
  readonly completionEvidence: readonly string[];
  readonly productionRiskAddressed: readonly string[];
};

export type EdgeAuditReadinessSnapshotA0 = {
  readonly foundationCompletenessPercent: number;
  readonly productionRuntimeReadinessPercent: number;
  readonly connectorProductionReadinessPercent: number;
  readonly offlineDeploymentReadinessPercent: number;
  readonly securityReadinessPercent: number;
  readonly validationConfidencePercent: number;
  readonly overallConfidencePercent: number;
};

export type EdgeAuditFindingsSnapshotA0 = {
  readonly auditId: 'UFMS-EDGE-CURRENT-CAPABILITY-AUDIT-A0';
  readonly freezeTaskId: 'UFMS-EDGE-C4-00A';
  readonly repository: '/Volumes/Work/VANTARIS_UFMS_FULL';
  readonly branch: 'main';
  readonly baselineCommit: '3c70692';
  readonly classification: EdgeAuditSnapshotClassification;
  readonly productionCertification: false;
  readonly foundationCompletenessPercent: number;
  readonly productionRuntimeReadinessPercent: number;
  readonly connectorProductionReadinessPercent: number;
  readonly offlineDeploymentReadinessPercent: number;
  readonly securityReadinessPercent: number;
  readonly validationConfidencePercent: number;
  readonly overallConfidencePercent: number;
  readonly connectors: readonly EdgeConnectorAuditEntry[];
  readonly productionBlockers: readonly EdgeProductionBlockerA0[];
  readonly nextDevelopmentSequence: readonly EdgeNextDevelopmentTaskA0[];
  readonly readinessKey: 'UFMS_EDGE_C4_00A_AUDIT_FINDINGS_FREEZE_PASS';
};

export type EdgeProductionGapRegisterEntryA0 = {
  readonly id:
    | 'PG-01'
    | 'PG-02'
    | 'PG-03'
    | 'PG-04'
    | 'PG-05'
    | 'PG-06'
    | 'PG-07'
    | 'PG-08'
    | 'PG-09'
    | 'PG-10'
    | 'PG-11'
    | 'PG-12'
    | 'PG-13'
    | 'PG-14'
    | 'PG-15'
    | 'PG-16'
    | 'PG-17'
    | 'PG-18'
    | 'PG-19'
    | 'PG-20';
  readonly domain: string;
  readonly currentFoundation: string;
  readonly missingProductionCapability: string;
  readonly risk: EdgeAuditRiskLevel;
  readonly blocksProduction: boolean;
  readonly recommendedPhase: string;
  readonly recommendedOwner: EdgeAuditOwner;
};
