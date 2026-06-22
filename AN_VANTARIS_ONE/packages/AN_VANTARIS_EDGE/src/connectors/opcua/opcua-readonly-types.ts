export type OpcUaTransport = 'OPC_TCP';
export type OpcUaDiscoveryMode = 'MODELED_ONLY';
export type OpcUaDnsResolutionMode = 'MODELED_ONLY';
export type OpcUaCredentialMode = 'REFERENCE_ONLY';
export type OpcUaCertificateMode = 'REFERENCE_ONLY';

export type OpcUaSecurityPolicy =
  | 'Basic256Sha256'
  | 'Aes128_Sha256_RsaOaep'
  | 'Aes256_Sha256_RsaPss'
  | 'None'
  | 'Basic128Rsa15'
  | 'Basic256';

export type OpcUaMessageSecurityMode = 'NONE' | 'SIGN' | 'SIGN_AND_ENCRYPT';

export type OpcUaService =
  | 'BROWSE'
  | 'BROWSE_NEXT'
  | 'READ'
  | 'TRANSLATE_BROWSE_PATHS_TO_NODE_IDS'
  | 'WRITE'
  | 'CALL'
  | 'ADD_NODES'
  | 'DELETE_NODES'
  | 'ADD_REFERENCES'
  | 'DELETE_REFERENCES'
  | 'CREATE_SUBSCRIPTION'
  | 'CREATE_MONITORED_ITEMS'
  | 'MODIFY_MONITORED_ITEMS'
  | 'DELETE_MONITORED_ITEMS'
  | 'HISTORY_UPDATE'
  | 'HISTORY_READ';

export type OpcUaNodeIdType = 'NUMERIC' | 'STRING' | 'GUID' | 'BYTESTRING';

export type OpcUaAttributeId =
  | 'NODE_ID'
  | 'NODE_CLASS'
  | 'BROWSE_NAME'
  | 'DISPLAY_NAME'
  | 'DESCRIPTION'
  | 'VALUE'
  | 'DATA_TYPE'
  | 'VALUE_RANK'
  | 'ARRAY_DIMENSIONS'
  | 'ACCESS_LEVEL'
  | 'USER_ACCESS_LEVEL'
  | 'MINIMUM_SAMPLING_INTERVAL'
  | 'HISTORIZING';

export type OpcUaVariantType =
  | 'NULL'
  | 'BOOLEAN'
  | 'SBYTE'
  | 'BYTE'
  | 'INT16'
  | 'UINT16'
  | 'INT32'
  | 'UINT32'
  | 'INT64'
  | 'UINT64'
  | 'FLOAT'
  | 'DOUBLE'
  | 'STRING'
  | 'DATETIME'
  | 'GUID'
  | 'BYTESTRING'
  | 'NODE_ID';

export type OpcUaStringNodeIdPrefix = {
  readonly namespaceIndex: number;
  readonly prefix: string;
};

export type OpcUaNumericNodeIdAllow = {
  readonly namespaceIndex: number;
  readonly identifier: number;
};

export type OpcUaReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-06';
  readonly classification: 'CONTROLLED_OPC_UA_READ_ONLY_FOUNDATION';
  readonly allowedTransports: readonly OpcUaTransport[];
  readonly allowedEndpointUrls: readonly string[];
  readonly allowedHosts: readonly string[];
  readonly allowedPorts: readonly number[];
  readonly allowedSecurityPolicies: readonly OpcUaSecurityPolicy[];
  readonly allowedMessageSecurityModes: readonly OpcUaMessageSecurityMode[];
  readonly anonymousAllowed: false;
  readonly credentialMode: OpcUaCredentialMode;
  readonly certificateMode: OpcUaCertificateMode;
  readonly trustedServerFingerprintRefs: readonly string[];
  readonly hostnameVerificationRequired: boolean;
  readonly applicationUriVerificationRequired: boolean;
  readonly allowedServices: readonly OpcUaService[];
  readonly deniedServices: readonly OpcUaService[];
  readonly subscriptionsAllowed: false;
  readonly monitoredItemsAllowed: false;
  readonly historyReadAllowed: false;
  readonly allowedNamespaceIndexes: readonly number[];
  readonly allowedNamespaceUris: readonly string[];
  readonly allowedNodeIdTypes: readonly OpcUaNodeIdType[];
  readonly allowedNumericNodeIds: readonly OpcUaNumericNodeIdAllow[];
  readonly allowedStringNodeIdPrefixes: readonly OpcUaStringNodeIdPrefix[];
  readonly deniedStringNodeIdPrefixes: readonly OpcUaStringNodeIdPrefix[];
  readonly allowedAttributes: readonly OpcUaAttributeId[];
  readonly allowedVariantTypes: readonly OpcUaVariantType[];
  readonly rejectUncertainStatusCodes: boolean;
  readonly maxNodesPerRead: number;
  readonly maxNodesPerBrowse: number;
  readonly maxBrowseDepth: number;
  readonly maxResponseBytes: number;
  readonly maxArrayLength: number;
  readonly maxStringLength: number;
  readonly maxContinuationPointLength: number;
  readonly timeoutMs: number;
  readonly maxRetryAttempts: number;
  readonly retryableErrors: readonly string[];
  readonly nonRetryableErrors: readonly string[];
  readonly backoffBaseMs: number;
  readonly backoffMultiplier: number;
  readonly backoffMaxMs: number;
  readonly endpointDiscoveryMode: OpcUaDiscoveryMode;
  readonly networkAccessAllowed: false;
  readonly dnsResolutionMode: OpcUaDnsResolutionMode;
  readonly syntheticTransportOnly: true;
  readonly writeOperationsAllowed: false;
  readonly candidateStatus: 'CONTROLLED_OPC_UA_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_06_OPC_UA_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type OpcUaNormalizedEndpoint = {
  readonly originalUrl: string;
  readonly scheme: string;
  readonly hostname: string;
  readonly port: number;
  readonly path: string;
};

export type OpcUaEndpointValidation = ValidationResult & {
  readonly endpoint?: OpcUaNormalizedEndpoint;
};

export type OpcUaEndpointRiskEvaluation = ValidationResult & {
  readonly risks: readonly string[];
  readonly endpoint?: OpcUaNormalizedEndpoint;
};

export type OpcUaNormalizedNodeId = {
  readonly originalNodeId: string;
  readonly namespaceIndex: number;
  readonly identifierType: OpcUaNodeIdType;
  readonly identifier: string;
  readonly canonical: string;
};

export type OpcUaNodeIdValidation = ValidationResult & {
  readonly normalized?: OpcUaNormalizedNodeId;
};

export type OpcUaReadTarget = {
  readonly nodeId: string;
  readonly attributeId: string;
  readonly indexRange?: string;
};

export type OpcUaBrowseTarget = {
  readonly nodeId: string;
  readonly browseDirection?: string;
  readonly referenceTypeId?: string;
  readonly includeSubtypes?: boolean;
  readonly nodeClassMask?: number;
  readonly continuationPoint?: string;
  readonly depth?: number;
  readonly maxNodesPerBrowse?: number;
};

export type OpcUaRequestInput = {
  readonly endpointUrl: string;
  readonly securityPolicy: string;
  readonly messageSecurityMode: string;
  readonly credentialRef?: string;
  readonly clientCertificateRef?: string;
  readonly clientPrivateKeyRef?: string;
  readonly serverFingerprintRef?: string;
  readonly inlineCertificate?: string;
  readonly inlinePrivateKey?: string;
  readonly username?: string;
  readonly password?: string;
  readonly token?: string;
  readonly anonymous?: boolean;
  readonly applicationUri?: string;
  readonly serverApplicationUri?: string;
  readonly service: string;
  readonly requestHandle?: number | string;
  readonly reads?: readonly OpcUaReadTarget[];
  readonly browse?: OpcUaBrowseTarget;
  readonly endpointDiscovery?: boolean;
};

export type OpcUaReadResult = {
  readonly nodeId: string;
  readonly attributeId: string;
  readonly statusCode: string;
  readonly valueType?: string;
  readonly value?: unknown;
  readonly sourceTimestamp?: string;
  readonly serverTimestamp?: string;
};

export type OpcUaResponsePayload = {
  readonly requestHandle: number;
  readonly service: string;
  readonly results?: readonly OpcUaReadResult[];
  readonly responseBytes?: number;
  readonly malformed?: boolean;
};

export type OpcUaSyntheticFixture = {
  readonly request: OpcUaRequestInput;
  readonly response: OpcUaResponsePayload & {
    readonly simulatedTimeout?: boolean;
    readonly simulatedErrorClass?: string;
  };
};

export type OpcUaSyntheticTransportResult = {
  readonly accepted: boolean;
  readonly transportMode: 'SYNTHETIC_TRANSPORT_ONLY';
  readonly service: string;
  readonly endpointUrl: string;
  readonly requestHandle: number;
  readonly retryDecision?: OpcUaRetryDecision;
  readonly backoffMs?: number;
  readonly errors: readonly string[];
};

export type OpcUaRetryBackoff = {
  readonly attempt: number;
  readonly delayMs: number;
  readonly clamped: boolean;
};

export type OpcUaRetryDecision = {
  readonly shouldRetry: boolean;
  readonly attempt: number;
  readonly maxAttempts: number;
  readonly exhausted: boolean;
  readonly reason?: string;
};

export type OpcUaAcceptanceResult =
  | 'OPC_UA_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'OPC_UA_READ_ONLY_FOUNDATION_REJECTED';
