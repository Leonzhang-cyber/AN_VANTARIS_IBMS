export type SnmpProductionAdapterMode = 'PRODUCTION_SNMPV3_READONLY';

export type SnmpProductionOperation = 'GET' | 'GETNEXT' | 'GETBULK';

export type SnmpProductionDeniedOperation = 'SET' | 'TRAP' | 'INFORM' | 'TRAP_SEND';

export type SnmpProductionUdpMode = 'PRODUCTION_UDP' | 'LOOPBACK_TEST';

export type SnmpProductionDnsMode = 'DENY' | 'INJECTED_TEST';

export type SnmpProductionSecurityMode = 'authPriv';

export type SnmpProductionErrorCode =
  | 'SNMP_CONFIG_INVALID'
  | 'SNMP_TARGET_REFERENCE_NOT_FOUND'
  | 'SNMP_TARGET_NOT_ALLOWLISTED'
  | 'SNMP_DNS_NOT_ALLOWED'
  | 'SNMP_DNS_RESULT_REJECTED'
  | 'SNMP_METADATA_TARGET_REJECTED'
  | 'SNMP_PORT_NOT_ALLOWED'
  | 'SNMP_CREDENTIAL_REFERENCE_FAILED'
  | 'SNMP_SECURITY_MODE_NOT_ALLOWED'
  | 'SNMP_COMMUNITY_STRING_REJECTED'
  | 'SNMP_OPERATION_NOT_ALLOWED'
  | 'SNMP_OID_NOT_ALLOWLISTED'
  | 'SNMP_OID_INVALID'
  | 'SNMP_WALK_LIMIT_EXCEEDED'
  | 'SNMP_BULK_LIMIT_EXCEEDED'
  | 'SNMP_CONNECT_TIMEOUT'
  | 'SNMP_RESPONSE_TIMEOUT'
  | 'SNMP_RESPONSE_SIZE_LIMIT_EXCEEDED'
  | 'SNMP_PDU_INVALID'
  | 'SNMP_REQUEST_ID_MISMATCH'
  | 'SNMP_ERROR_STATUS'
  | 'SNMP_VARBIND_LIMIT_EXCEEDED'
  | 'SNMP_FOUNDATION_VALIDATION_FAILED'
  | 'SNMP_REQUEST_FAILED'
  | 'SNMP_ADAPTER_DISABLED';

export type SnmpProductionResourceLimits = {
  readonly connectTimeoutMs: number;
  readonly responseTimeoutMs: number;
  readonly maxResponseBytes: number;
  readonly maxOids: number;
  readonly maxVarbinds: number;
  readonly maxWalkDepth: number;
  readonly maxWalkRows: number;
  readonly maxBulkRepetitions: number;
  readonly maxOidLength: number;
  readonly maxRetries: number;
  readonly maxProcessingMilliseconds: number;
};

export type SnmpProductionAdapterConfig = {
  readonly adapterMode: SnmpProductionAdapterMode;
  readonly enabled: boolean;
  readonly targetReferenceId: string;
  readonly targetPort: number;
  readonly oidAllowlistReference: string;
  readonly credentialReferenceId: string;
  readonly authProtocolReference: string;
  readonly privProtocolReference: string;
  readonly engineIdReference?: string;
  readonly snmpVersion: '3';
  readonly securityMode: SnmpProductionSecurityMode;
  readonly operation: SnmpProductionOperation;
  readonly oids: readonly string[];
  readonly bulkRepetitions: number;
  readonly udpMode: SnmpProductionUdpMode;
  readonly dnsMode: SnmpProductionDnsMode;
  readonly allowPrivateNetworkReference: boolean;
} & SnmpProductionResourceLimits;

export type SnmpProductionResolvedTarget = {
  readonly hostname: string;
  readonly port: number;
};

export type SnmpProductionCredentialBundle = {
  readonly credentialReferenceId: string;
  readonly authProtocolReference: string;
  readonly privProtocolReference: string;
  readonly engineIdReference?: string;
  readonly securityMode: SnmpProductionSecurityMode;
};

export type SnmpProductionTargetResolver = (
  targetReferenceId: string,
) => SnmpProductionResolvedTarget | undefined;

export type SnmpProductionDnsResolver = (hostname: string) => readonly string[] | undefined;

export type SnmpProductionOidAllowlistResolver = (referenceId: string) => readonly string[] | undefined;

export type SnmpProductionCredentialResolver = (
  credentialReferenceId: string,
) => SnmpProductionCredentialBundle | undefined;

export type SnmpProductionReadRequest = {
  readonly config: SnmpProductionAdapterConfig;
  readonly resolveTarget: SnmpProductionTargetResolver;
  readonly resolveOidAllowlist: SnmpProductionOidAllowlistResolver;
  readonly resolveCredential: SnmpProductionCredentialResolver;
  readonly resolveDns?: SnmpProductionDnsResolver;
  readonly testMode?: boolean;
};

export type SnmpProductionWalkRequest = SnmpProductionReadRequest & {
  readonly walkRootOid: string;
};

export type SnmpProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type SnmpProductionReadSuccess = {
  readonly ok: true;
  readonly targetReferenceId: string;
  readonly targetHash: string;
  readonly operation: SnmpProductionOperation | 'WALK';
  readonly recordCount: number;
  readonly records: readonly SnmpProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type SnmpProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: SnmpProductionErrorCode;
  readonly targetReferenceId?: string;
  readonly targetHash?: string;
  readonly operation?: string;
  readonly oidReference?: string;
};

export type SnmpProductionReadResult = SnmpProductionReadSuccess | SnmpProductionReadFailure;

export type SnmpProductionReadOnlyAdapter = {
  readonly readOnce: (request: SnmpProductionReadRequest) => Promise<SnmpProductionReadResult>;
  readonly walkOnce: (request: SnmpProductionWalkRequest) => Promise<SnmpProductionReadResult>;
};

export const SNMP_PRODUCTION_LIMIT_CAPS: SnmpProductionResourceLimits = {
  connectTimeoutMs: 30_000,
  responseTimeoutMs: 30_000,
  maxResponseBytes: 65_536,
  maxOids: 64,
  maxVarbinds: 128,
  maxWalkDepth: 32,
  maxWalkRows: 256,
  maxBulkRepetitions: 25,
  maxOidLength: 128,
  maxRetries: 0,
  maxProcessingMilliseconds: 30_000,
};

export const SNMP_PRODUCTION_READ_OPERATIONS = ['GET', 'GETNEXT', 'GETBULK'] as const;

export const SNMP_PRODUCTION_DENIED_OPERATIONS = ['SET', 'TRAP', 'INFORM', 'TRAP_SEND'] as const;

export const SNMP_PRODUCTION_METADATA_HOSTS = [
  '169.254.169.254',
  '100.100.100.200',
  'metadata.google.internal',
  'metadata.azure.internal',
  'localhost',
  'localhost.localdomain',
] as const;

export const SNMP_PRODUCTION_ALLOWED_VARBIND_TYPES = [
  'INTEGER',
  'OCTET_STRING',
  'OBJECT_IDENTIFIER',
  'IP_ADDRESS',
  'COUNTER32',
  'GAUGE32',
  'TIMETICKS',
  'COUNTER64',
  'NULL',
] as const;
