import type { OpcUaAttributeId, OpcUaService, OpcUaVariantType } from '../opcua-readonly-types.js';

export type OpcuaProductionAdapterMode = 'PRODUCTION_OPC_UA_READONLY';

export type OpcuaProductionReadService = 'READ' | 'BROWSE' | 'HEALTH_PROBE';

export type OpcuaProductionDeniedService =
  | 'WRITE'
  | 'CALL'
  | 'CREATE_SUBSCRIPTION'
  | 'CREATE_MONITORED_ITEMS'
  | 'MODIFY_MONITORED_ITEMS'
  | 'DELETE_MONITORED_ITEMS'
  | 'HISTORY_UPDATE'
  | 'ADD_NODES'
  | 'DELETE_NODES'
  | 'ADD_REFERENCES'
  | 'DELETE_REFERENCES';

export type OpcuaProductionTcpMode = 'PRODUCTION_OPC_TCP' | 'LOOPBACK_TEST';

export type OpcuaProductionDnsMode = 'DENY' | 'INJECTED_TEST';

export type OpcuaProductionFormulaPrefixPolicy = 'REJECT' | 'MARK';

export type OpcuaProductionDangerousKeyPolicy = 'REJECT';

export type OpcuaProductionErrorCode =
  | 'OPCUA_CONFIG_INVALID'
  | 'OPCUA_ADAPTER_DISABLED'
  | 'OPCUA_ENDPOINT_REFERENCE_NOT_FOUND'
  | 'OPCUA_ENDPOINT_NOT_ALLOWLISTED'
  | 'OPCUA_DNS_NOT_ALLOWED'
  | 'OPCUA_DNS_RESULT_REJECTED'
  | 'OPCUA_METADATA_ENDPOINT_REJECTED'
  | 'OPCUA_PORT_NOT_ALLOWED'
  | 'OPCUA_SERVICE_NOT_ALLOWED'
  | 'OPCUA_WRITE_SERVICE_REJECTED'
  | 'OPCUA_CALL_METHOD_REJECTED'
  | 'OPCUA_SUBSCRIPTION_REJECTED'
  | 'OPCUA_NODE_NOT_ALLOWLISTED'
  | 'OPCUA_ATTRIBUTE_NOT_ALLOWLISTED'
  | 'OPCUA_NODE_LIMIT_EXCEEDED'
  | 'OPCUA_VALUE_SIZE_LIMIT_EXCEEDED'
  | 'OPCUA_CONNECT_TIMEOUT'
  | 'OPCUA_RESPONSE_TIMEOUT'
  | 'OPCUA_RESPONSE_SIZE_LIMIT_EXCEEDED'
  | 'OPCUA_REQUEST_MAGIC_INVALID'
  | 'OPCUA_RESPONSE_MAGIC_INVALID'
  | 'OPCUA_REQUEST_FRAME_INVALID'
  | 'OPCUA_RESPONSE_FRAME_INVALID'
  | 'OPCUA_REQUEST_ID_MISMATCH'
  | 'OPCUA_SERVICE_MISMATCH'
  | 'OPCUA_STATUS_ERROR_RESPONSE'
  | 'OPCUA_BAD_STATUS_RESPONSE'
  | 'OPCUA_DECODE_FAILED'
  | 'OPCUA_FOUNDATION_VALIDATION_FAILED'
  | 'OPCUA_REQUEST_FAILED'
  | 'OPCUA_CREDENTIAL_REFERENCE_INVALID'
  | 'OPCUA_INSECURE_ENDPOINT_REJECTED';

export type OpcuaProductionReadTarget = {
  readonly nodeId: string;
  readonly attributeId: string;
  readonly indexRange?: string;
};

export type OpcuaProductionBrowseTarget = {
  readonly nodeId: string;
  readonly browseDirection?: string;
  readonly referenceTypeId?: string;
  readonly includeSubtypes?: boolean;
  readonly nodeClassMask?: number;
  readonly depth?: number;
  readonly maxNodesPerBrowse?: number;
};

export type OpcuaProductionResourceLimits = {
  readonly maxNodes: number;
  readonly maxBrowseNodes: number;
  readonly maxNodeIdLength: number;
  readonly maxValueBytes: number;
  readonly maxResponseBytes: number;
  readonly maxBrowseDepth: number;
  readonly responseTimeoutMs: number;
  readonly maxProcessingMilliseconds: number;
  readonly maxRetries: number;
};

export type OpcuaProductionAdapterConfig = {
  readonly adapterMode: OpcuaProductionAdapterMode;
  readonly enabled: boolean;
  readonly endpointReferenceId: string;
  readonly nodeAllowlistReferenceId: string;
  readonly credentialReferenceId: string;
  readonly clientCertificateReferenceId?: string;
  readonly clientPrivateKeyReferenceId?: string;
  readonly serverFingerprintReferenceId?: string;
  readonly securityPolicy: string;
  readonly messageSecurityMode: string;
  readonly service: OpcuaProductionReadService;
  readonly reads: readonly OpcuaProductionReadTarget[];
  readonly browse?: OpcuaProductionBrowseTarget;
  readonly endpointPort: number;
  readonly tcpMode: OpcuaProductionTcpMode;
  readonly dnsMode: OpcuaProductionDnsMode;
  readonly allowPrivateNetworkReference: boolean;
  readonly formulaPrefixPolicy: OpcuaProductionFormulaPrefixPolicy;
  readonly dangerousKeyPolicy: OpcuaProductionDangerousKeyPolicy;
} & OpcuaProductionResourceLimits;

export type OpcuaProductionResolvedEndpoint = {
  readonly hostname: string;
  readonly port: number;
};

export type OpcuaProductionEndpointResolver = (
  endpointReferenceId: string,
) => OpcuaProductionResolvedEndpoint | undefined;

export type OpcuaProductionNodeAllowlistResolver = (
  referenceId: string,
) => readonly string[] | undefined;

export type OpcuaProductionDnsResolver = (hostname: string) => readonly string[] | undefined;

export type OpcuaProductionReadRequest = {
  readonly config: OpcuaProductionAdapterConfig;
  readonly resolveEndpoint: OpcuaProductionEndpointResolver;
  readonly resolveNodeAllowlist: OpcuaProductionNodeAllowlistResolver;
  readonly resolveDns?: OpcuaProductionDnsResolver;
  readonly testMode?: boolean;
};

export type OpcuaProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type OpcuaProductionReadSuccess = {
  readonly ok: true;
  readonly endpointReferenceId: string;
  readonly endpointHash: string;
  readonly service: OpcUaService | OpcuaProductionReadService;
  readonly recordCount: number;
  readonly records: readonly OpcuaProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type OpcuaProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: OpcuaProductionErrorCode;
  readonly endpointReferenceId?: string;
  readonly endpointHash?: string;
  readonly service?: string;
  readonly nodeReference?: string;
};

export type OpcuaProductionReadResult = OpcuaProductionReadSuccess | OpcuaProductionReadFailure;

export type OpcuaProductionReadOnlyAdapter = {
  readonly readOnce: (request: OpcuaProductionReadRequest) => Promise<OpcuaProductionReadResult>;
  readonly browseOnce: (request: OpcuaProductionReadRequest) => Promise<OpcuaProductionReadResult>;
  readonly healthProbeOnce: (request: OpcuaProductionReadRequest) => Promise<OpcuaProductionReadResult>;
};

export const OPCUA_PRODUCTION_LIMIT_CAPS: OpcuaProductionResourceLimits = {
  maxNodes: 64,
  maxBrowseNodes: 32,
  maxNodeIdLength: 256,
  maxValueBytes: 8192,
  maxResponseBytes: 65536,
  maxBrowseDepth: 8,
  responseTimeoutMs: 30_000,
  maxProcessingMilliseconds: 30_000,
  maxRetries: 0,
};

export const OPCUA_PRODUCTION_READ_SERVICES = ['READ', 'BROWSE', 'HEALTH_PROBE'] as const;

export const OPCUA_PRODUCTION_DENIED_SERVICES = [
  'WRITE',
  'CALL',
  'CREATE_SUBSCRIPTION',
  'CREATE_MONITORED_ITEMS',
  'MODIFY_MONITORED_ITEMS',
  'DELETE_MONITORED_ITEMS',
  'HISTORY_UPDATE',
  'ADD_NODES',
  'DELETE_NODES',
  'ADD_REFERENCES',
  'DELETE_REFERENCES',
] as const;

export const OPCUA_PRODUCTION_METADATA_HOSTS = [
  '169.254.169.254',
  '100.100.100.200',
  'metadata.google.internal',
  'metadata.azure.internal',
  'localhost',
  'localhost.localdomain',
] as const;

export const OPCUA_PRODUCTION_ALLOWED_ATTRIBUTES = [
  'VALUE',
  'DISPLAY_NAME',
  'BROWSE_NAME',
  'DESCRIPTION',
  'DATA_TYPE',
  'STATUS_CODE',
  'SOURCE_TIMESTAMP',
  'SERVER_TIMESTAMP',
] as const;

export const OPCUA_PRODUCTION_ALLOWED_VARIANT_TYPES = [
  'NULL',
  'BOOLEAN',
  'INT32',
  'UINT32',
  'DOUBLE',
  'STRING',
  'DATETIME',
] as const;

export const OPCUA_PRODUCTION_FORMULA_PREFIXES = ['=', '+', '-', '@'] as const;

export const OPCUA_PRODUCTION_DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;

export type { OpcUaAttributeId, OpcUaVariantType };
