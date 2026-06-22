export type BacnetTransport = 'BACNET_IP';
export type BacnetDiscoveryMode = 'MODELED_ONLY';
export type BacnetDnsResolutionMode = 'MODELED_ONLY';
export type BacnetService =
  | 'READ_PROPERTY'
  | 'READ_PROPERTY_MULTIPLE'
  | 'WRITE_PROPERTY'
  | 'WRITE_PROPERTY_MULTIPLE'
  | 'SUBSCRIBE_COV'
  | 'SUBSCRIBE_COV_PROPERTY'
  | 'DEVICE_COMMUNICATION_CONTROL'
  | 'REINITIALIZE_DEVICE'
  | 'ATOMIC_READ_FILE'
  | 'ATOMIC_WRITE_FILE'
  | 'ADD_LIST_ELEMENT'
  | 'REMOVE_LIST_ELEMENT'
  | 'CREATE_OBJECT'
  | 'DELETE_OBJECT'
  | 'WHO_IS'
  | 'I_AM';

export type BacnetObjectType =
  | 'DEVICE'
  | 'ANALOG_INPUT'
  | 'ANALOG_OUTPUT'
  | 'ANALOG_VALUE'
  | 'BINARY_INPUT'
  | 'BINARY_OUTPUT'
  | 'BINARY_VALUE'
  | 'MULTI_STATE_INPUT'
  | 'MULTI_STATE_OUTPUT'
  | 'MULTI_STATE_VALUE';

export type BacnetPropertyId =
  | 'OBJECT_IDENTIFIER'
  | 'OBJECT_NAME'
  | 'OBJECT_TYPE'
  | 'PRESENT_VALUE'
  | 'STATUS_FLAGS'
  | 'EVENT_STATE'
  | 'OUT_OF_SERVICE'
  | 'UNITS'
  | 'DESCRIPTION'
  | 'RELIABILITY'
  | 'ACTIVE_TEXT'
  | 'INACTIVE_TEXT'
  | 'STATE_TEXT'
  | 'NUMBER_OF_STATES'
  | 'SYSTEM_STATUS'
  | 'VENDOR_IDENTIFIER'
  | 'MODEL_NAME'
  | 'FIRMWARE_REVISION'
  | 'APPLICATION_SOFTWARE_VERSION'
  | 'PRIORITY_ARRAY'
  | 'RELINQUISH_DEFAULT'
  | 'RECIPIENT_LIST'
  | 'TIME_DELAY'
  | 'NOTIFICATION_CLASS';

export type BacnetValueType =
  | 'NULL'
  | 'BOOLEAN'
  | 'UNSIGNED'
  | 'SIGNED'
  | 'REAL'
  | 'DOUBLE'
  | 'OCTET_STRING'
  | 'CHARACTER_STRING'
  | 'BIT_STRING'
  | 'ENUMERATED'
  | 'DATE'
  | 'TIME'
  | 'OBJECT_IDENTIFIER';

export type BacnetObjectInstanceRange = {
  readonly objectType: BacnetObjectType;
  readonly start: number;
  readonly end: number;
};

export type BacnetIpReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-05';
  readonly classification: 'CONTROLLED_BACNET_IP_READ_ONLY_FOUNDATION';
  readonly allowedTransports: readonly BacnetTransport[];
  readonly allowedTargets: readonly string[];
  readonly deniedTargets: readonly string[];
  readonly allowedPorts: readonly number[];
  readonly allowedDeviceInstances: readonly number[];
  readonly allowedServices: readonly BacnetService[];
  readonly deniedServices: readonly BacnetService[];
  readonly allowedObjectTypes: readonly BacnetObjectType[];
  readonly allowedObjectInstanceRanges: readonly BacnetObjectInstanceRange[];
  readonly allowedProperties: readonly BacnetPropertyId[];
  readonly deniedProperties: readonly BacnetPropertyId[];
  readonly discoveryMode: BacnetDiscoveryMode;
  readonly broadcastAllowed: false;
  readonly bbmdAllowed: false;
  readonly foreignDeviceRegistrationAllowed: false;
  readonly covSubscriptionAllowed: false;
  readonly maxObjectsPerRequest: number;
  readonly maxPropertiesPerRequest: number;
  readonly maxResponseBytes: number;
  readonly maxApduBytes: number;
  readonly maxArrayIndex: number;
  readonly maxInvokeId: number;
  readonly segmentationAllowed: false;
  readonly timeoutMs: number;
  readonly maxRetryAttempts: number;
  readonly retryableErrors: readonly string[];
  readonly nonRetryableErrors: readonly string[];
  readonly backoffBaseMs: number;
  readonly backoffMultiplier: number;
  readonly backoffMaxMs: number;
  readonly networkAccessAllowed: false;
  readonly dnsResolutionMode: BacnetDnsResolutionMode;
  readonly syntheticTransportOnly: true;
  readonly writeOperationsAllowed: false;
  readonly allowedValueTypes: readonly BacnetValueType[];
  readonly candidateStatus: 'CONTROLLED_BACNET_IP_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_05_BACNET_IP_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type BacnetNormalizedTarget = {
  readonly originalTarget: string;
  readonly hostname: string;
  readonly port: number;
};

export type BacnetTargetValidation = ValidationResult & {
  readonly target?: BacnetNormalizedTarget;
};

export type BacnetTargetRiskEvaluation = ValidationResult & {
  readonly risks: readonly string[];
  readonly target?: BacnetNormalizedTarget;
};

export type BacnetObjectIdentifier = {
  readonly objectType: BacnetObjectType;
  readonly objectInstance: number;
};

export type BacnetPropertyRead = {
  readonly objectType: BacnetObjectType;
  readonly objectInstance: number | string;
  readonly propertyId: string;
  readonly arrayIndex?: number | string;
};

export type BacnetRequestInput = {
  readonly target: string;
  readonly port?: number;
  readonly deviceInstance: number | string;
  readonly service: string;
  readonly invokeId?: number | string;
  readonly reads: readonly BacnetPropertyRead[];
  readonly credentialRef?: string;
  readonly username?: string;
  readonly password?: string;
  readonly token?: string;
  readonly bbmd?: boolean;
  readonly foreignDeviceRegistration?: boolean;
  readonly broadcast?: boolean;
};

export type BacnetRequestValidation = ValidationResult & {
  readonly service?: BacnetService;
  readonly deviceInstance?: number;
  readonly invokeId?: number;
};

export type BacnetPropertyResult = {
  readonly objectType: BacnetObjectType;
  readonly objectInstance: number;
  readonly propertyId: string;
  readonly arrayIndex?: number;
  readonly valueType?: BacnetValueType | string;
  readonly value?: unknown;
};

export type BacnetResponsePayload = {
  readonly invokeId: number;
  readonly service: BacnetService | string;
  readonly deviceInstance: number;
  readonly segmented?: boolean;
  readonly results?: readonly BacnetPropertyResult[];
  readonly errorClass?: 'ERROR' | 'REJECT' | 'ABORT';
  readonly errorCode?: string;
  readonly responseBytes?: number;
  readonly apduBytes?: number;
};

export type BacnetResponseValidation = ValidationResult & {
  readonly response: BacnetResponsePayload;
};

export type BacnetRetryBackoff = {
  readonly attempt: number;
  readonly delayMs: number;
  readonly clamped: boolean;
};

export type BacnetRetryDecision = {
  readonly shouldRetry: boolean;
  readonly attempt: number;
  readonly maxAttempts: number;
  readonly exhausted: boolean;
  readonly reason?: string;
};

export type BacnetSyntheticFixture = {
  readonly request: BacnetRequestInput;
  readonly response: BacnetResponsePayload & {
    readonly simulatedTimeout?: boolean;
    readonly simulatedErrorClass?: string;
    readonly malformed?: boolean;
  };
};

export type BacnetSyntheticTransportResult = {
  readonly accepted: boolean;
  readonly transportMode: 'SYNTHETIC_TRANSPORT_ONLY';
  readonly service: string;
  readonly target: string;
  readonly port: number;
  readonly deviceInstance: number;
  readonly retryDecision?: BacnetRetryDecision;
  readonly backoffMs?: number;
  readonly errors: readonly string[];
};

export type BacnetAcceptanceResult =
  | 'BACNET_IP_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'BACNET_IP_READ_ONLY_FOUNDATION_REJECTED';
