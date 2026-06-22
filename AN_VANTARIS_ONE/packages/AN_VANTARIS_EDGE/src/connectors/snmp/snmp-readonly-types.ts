export type SnmpVersionToken = '1' | '2c' | '3' | 'v1' | 'v2c' | 'v3';
export type SnmpOperation = 'GET' | 'GETNEXT' | 'GETBULK' | 'SET' | 'INFORM' | 'TRAP_SEND';
export type SnmpCredentialMode = 'REFERENCE_ONLY';
export type SnmpDnsResolutionMode = 'MODELED_ONLY';

export type SnmpReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-03';
  readonly classification: 'CONTROLLED_SNMP_READ_ONLY_FOUNDATION';
  readonly allowedVersions: readonly string[];
  readonly preferredVersion: string;
  readonly productionAllowedVersions: readonly string[];
  readonly allowedOperations: readonly SnmpOperation[];
  readonly deniedOperations: readonly SnmpOperation[];
  readonly allowedTargets: readonly string[];
  readonly deniedTargets: readonly string[];
  readonly defaultPort: number;
  readonly allowedOidPrefixes: readonly string[];
  readonly deniedOidPrefixes: readonly string[];
  readonly credentialMode: SnmpCredentialMode;
  readonly plaintextCommunityAllowed: false;
  readonly plaintextAuthSecretAllowed: false;
  readonly plaintextPrivacySecretAllowed: false;
  readonly timeoutMs: number;
  readonly maxRetryAttempts: number;
  readonly retryableErrors: readonly string[];
  readonly nonRetryableErrors: readonly string[];
  readonly backoffBaseMs: number;
  readonly backoffMultiplier: number;
  readonly backoffMaxMs: number;
  readonly maxVarbinds: number;
  readonly maxResponseBytes: number;
  readonly maxWalkRows: number;
  readonly maxWalkDepth: number;
  readonly maxOidComponents: number;
  readonly maxOidComponentValue: number;
  readonly networkAccessAllowed: false;
  readonly dnsResolutionMode: SnmpDnsResolutionMode;
  readonly syntheticTransportOnly: true;
  readonly writeOperationsAllowed: false;
  readonly allowedVarbindTypes: readonly string[];
  readonly candidateStatus: 'CONTROLLED_SNMP_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_03_SNMP_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type SnmpNormalizedTarget = {
  readonly originalTarget: string;
  readonly hostname: string;
  readonly port: number;
};

export type SnmpTargetValidation = ValidationResult & {
  readonly target?: SnmpNormalizedTarget;
};

export type SnmpTargetRiskEvaluation = ValidationResult & {
  readonly risks: readonly string[];
  readonly target?: SnmpNormalizedTarget;
};

export type SnmpNormalizedOid = {
  readonly originalOid: string;
  readonly oid: string;
  readonly components: readonly number[];
};

export type SnmpOidValidation = ValidationResult & {
  readonly normalized?: SnmpNormalizedOid;
};

export type SnmpVarbind = {
  readonly oid: string;
  readonly type: string;
  readonly value: string | number | boolean | null;
};

export type SnmpResponseMetadata = {
  readonly errorStatus: number;
  readonly errorIndex: number;
  readonly varbinds: readonly SnmpVarbind[];
  readonly responseBytes: number;
  readonly walkDepth?: number;
  readonly walkRows?: number;
  readonly operation?: string;
};

export type SnmpResponseValidation = ValidationResult & {
  readonly metadata: SnmpResponseMetadata;
};

export type SnmpRetryBackoff = {
  readonly attempt: number;
  readonly delayMs: number;
  readonly clamped: boolean;
};

export type SnmpRetryDecision = {
  readonly shouldRetry: boolean;
  readonly attempt: number;
  readonly maxAttempts: number;
  readonly exhausted: boolean;
  readonly reason?: string;
};

export type SnmpSyntheticFixtureRequest = {
  readonly version: string;
  readonly operation: string;
  readonly target: string;
  readonly port?: number;
  readonly credentialRef?: string;
  readonly community?: string;
  readonly authPassword?: string;
  readonly privPassword?: string;
  readonly username?: string;
  readonly oids?: readonly string[];
};

export type SnmpSyntheticFixtureResponse = {
  readonly errorStatus?: number;
  readonly errorIndex?: number;
  readonly varbinds?: readonly SnmpVarbind[];
  readonly simulatedErrorClass?: string;
  readonly simulatedTimeout?: boolean;
  readonly malformed?: boolean;
};

export type SnmpSyntheticFixture = {
  readonly request: SnmpSyntheticFixtureRequest;
  readonly response: SnmpSyntheticFixtureResponse;
};

export type SnmpSyntheticTransportResult = {
  readonly accepted: boolean;
  readonly transportMode: 'SYNTHETIC_TRANSPORT_ONLY';
  readonly version: string;
  readonly operation: string;
  readonly target: string;
  readonly varbindCount: number;
  readonly retryDecision?: SnmpRetryDecision;
  readonly backoffMs?: number;
  readonly errors: readonly string[];
};

export type SnmpAcceptanceResult =
  | 'SNMP_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'SNMP_READ_ONLY_FOUNDATION_REJECTED';
