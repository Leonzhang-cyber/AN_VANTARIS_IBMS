export type ConnectorRegistryKey = 'file' | 'http' | 'snmp' | 'modbus' | 'bacnet' | 'opcua';

export type ConnectorGateStatus =
  | 'PASS'
  | 'FAIL'
  | 'NOT_EVALUATED'
  | 'NOT_APPLICABLE'
  | 'DEFERRED'
  | 'REQUIRES_APPROVAL';

export type ConnectorEnablementDecision =
  | 'BLOCKED_NOT_PRODUCTION_READY'
  | 'ELIGIBLE_FOR_CONTROLLED_READ_ONLY_PILOT'
  | 'APPROVED_FOR_PRODUCTION_READ_ONLY'
  | 'REJECTED'
  | 'REVOKED';

export type ConnectorRiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'UNASSESSED';

export type ConnectorEnablementRecord = {
  readonly registryKey: ConnectorRegistryKey;
  readonly protocol: string;
  readonly currentMaturity: 'FOUNDATION_READY';
  readonly requestedMode: 'FOUNDATION_ONLY';
  readonly permittedMode: 'SYNTHETIC_ONLY';
  readonly syntheticFixtureOnly: true;
  readonly realConnectivityEnabled: false;
  readonly productionDependencyIncluded: false;
  readonly supportsRead: boolean;
  readonly supportsWriteback: false;
  readonly dependencyGate: ConnectorGateStatus;
  readonly securityGate: ConnectorGateStatus;
  readonly configurationGate: ConnectorGateStatus;
  readonly protocolGate: ConnectorGateStatus;
  readonly networkAuthorizationGate: ConnectorGateStatus;
  readonly readOnlyEnforcementGate: ConnectorGateStatus;
  readonly credentialProvisioningGate: ConnectorGateStatus;
  readonly evidenceGate: ConnectorGateStatus;
  readonly rollbackGate: ConnectorGateStatus;
  readonly operatorApprovalGate: ConnectorGateStatus;
  readonly decision: ConnectorEnablementDecision;
  readonly rejectionReasons: readonly string[];
  readonly requiredNextPhase: 'C5-01' | 'C5-02' | 'C5-03' | 'C5-04' | 'C5-05' | 'C5-06';
  readonly notes: string;
};

export type ConnectorEnablementMatrix = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-00';
  readonly classification: 'CONNECTOR_ENABLEMENT_FOUNDATION_ONLY';
  readonly connectors: readonly ConnectorEnablementRecord[];
  readonly acceptanceResult: 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_ACCEPTED';
  readonly readinessKey: 'UFMS_EDGE_C5_00_PRODUCTION_CONNECTOR_ENABLEMENT_GATE_PASS';
};

export type ConnectorRiskClassificationRecord = {
  readonly registryKey: ConnectorRegistryKey;
  readonly operationalRisk: ConnectorRiskLevel;
  readonly cybersecurityRisk: ConnectorRiskLevel;
  readonly dataIntegrityRisk: ConnectorRiskLevel;
  readonly availabilityRisk: ConnectorRiskLevel;
  readonly credentialRisk: ConnectorRiskLevel;
  readonly writebackRisk: ConnectorRiskLevel;
  readonly overallRisk: ConnectorRiskLevel;
  readonly requiredApprovalLevel: string;
  readonly notes: string;
};

export type ConnectorRiskClassification = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-00';
  readonly classification: 'CONNECTOR_ENABLEMENT_FOUNDATION_ONLY';
  readonly riskModelStatus: 'FOUNDATION_CONSERVATIVE_BASELINE';
  readonly connectors: readonly ConnectorRiskClassificationRecord[];
  readonly readinessKey: 'UFMS_EDGE_C5_00_PRODUCTION_CONNECTOR_ENABLEMENT_GATE_PASS';
};

export type ProtocolReadinessRequirements = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-00';
  readonly classification: 'CONNECTOR_ENABLEMENT_FOUNDATION_ONLY';
  readonly generalProductionRequirements: readonly string[];
  readonly protocolRequirements: Record<ConnectorRegistryKey, readonly string[]>;
  readonly notes: string;
  readonly readinessKey: 'UFMS_EDGE_C5_00_PRODUCTION_CONNECTOR_ENABLEMENT_GATE_PASS';
};

export type ConnectorEnablementEvaluationResult = {
  readonly connector: ConnectorRegistryKey;
  readonly productionEligible: boolean;
  readonly readOnlyPilotEligible: boolean;
  readonly decision: ConnectorEnablementDecision;
  readonly rejectionReasons: readonly string[];
};

export type ConnectorEnablementAcceptanceResult =
  | 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_ACCEPTED'
  | 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_REJECTED';

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};
