import type { BacnetObjectType, BacnetPropertyId, BacnetService } from '../bacnet-readonly-types.js';

export type BacnetProductionAdapterMode = 'PRODUCTION_BACNET_IP_READONLY';

export type BacnetProductionReadService = 'READ_PROPERTY' | 'READ_PROPERTY_MULTIPLE';

export type BacnetProductionDiscoveryService = 'WHO_IS';

export type BacnetProductionDeniedService =
  | 'WRITE_PROPERTY'
  | 'WRITE_PROPERTY_MULTIPLE'
  | 'SUBSCRIBE_COV'
  | 'SUBSCRIBE_COV_PROPERTY'
  | 'DEVICE_COMMUNICATION_CONTROL'
  | 'REINITIALIZE_DEVICE'
  | 'ACKNOWLEDGE_ALARM'
  | 'ATOMIC_WRITE_FILE'
  | 'ADD_LIST_ELEMENT'
  | 'REMOVE_LIST_ELEMENT'
  | 'CREATE_OBJECT'
  | 'DELETE_OBJECT'
  | 'PRIVATE_TRANSFER';

export type BacnetProductionUdpMode = 'PRODUCTION_UDP' | 'LOOPBACK_TEST';

export type BacnetProductionDnsMode = 'DENY' | 'INJECTED_TEST';

export type BacnetProductionBroadcastMode = 'DENY' | 'TEST_DISCOVERY_ONLY';

export type BacnetProductionSegmentationMode = 'DENY';

export type BacnetProductionFormulaPrefixPolicy = 'REJECT' | 'MARK';

export type BacnetProductionDangerousKeyPolicy = 'REJECT';

export type BacnetProductionErrorCode =
  | 'BACNET_CONFIG_INVALID'
  | 'BACNET_TARGET_REFERENCE_NOT_FOUND'
  | 'BACNET_TARGET_NOT_ALLOWLISTED'
  | 'BACNET_DNS_NOT_ALLOWED'
  | 'BACNET_DNS_RESULT_REJECTED'
  | 'BACNET_METADATA_TARGET_REJECTED'
  | 'BACNET_PORT_NOT_ALLOWED'
  | 'BACNET_SERVICE_NOT_ALLOWED'
  | 'BACNET_WRITE_SERVICE_REJECTED'
  | 'BACNET_BROADCAST_NOT_ALLOWED'
  | 'BACNET_OBJECT_NOT_ALLOWLISTED'
  | 'BACNET_PROPERTY_NOT_ALLOWLISTED'
  | 'BACNET_PROPERTY_LIMIT_EXCEEDED'
  | 'BACNET_CONNECT_TIMEOUT'
  | 'BACNET_RESPONSE_TIMEOUT'
  | 'BACNET_RESPONSE_SIZE_LIMIT_EXCEEDED'
  | 'BACNET_BVLC_INVALID'
  | 'BACNET_NPDU_INVALID'
  | 'BACNET_APDU_INVALID'
  | 'BACNET_INVOKE_ID_MISMATCH'
  | 'BACNET_SERVICE_MISMATCH'
  | 'BACNET_ERROR_RESPONSE'
  | 'BACNET_ABORT_REJECT_RESPONSE'
  | 'BACNET_SEGMENTATION_NOT_ALLOWED'
  | 'BACNET_DECODE_FAILED'
  | 'BACNET_FOUNDATION_VALIDATION_FAILED'
  | 'BACNET_REQUEST_FAILED'
  | 'BACNET_ADAPTER_DISABLED';

export type BacnetProductionPropertyRead = {
  readonly objectType: BacnetObjectType | string;
  readonly objectInstance: number;
  readonly propertyIdentifier: BacnetPropertyId | string;
  readonly arrayIndex?: number;
};

export type BacnetProductionResourceLimits = {
  readonly maxProperties: number;
  readonly maxObjects: number;
  readonly maxApduBytes: number;
  readonly maxResponseBytes: number;
  readonly maxSegments: number;
  readonly invokeTimeoutMs: number;
  readonly responseTimeoutMs: number;
  readonly maxProcessingMilliseconds: number;
  readonly maxRetries: number;
};

export type BacnetProductionAdapterConfig = {
  readonly adapterMode: BacnetProductionAdapterMode;
  readonly enabled: boolean;
  readonly targetReferenceId: string;
  readonly deviceInstanceReferenceId: string;
  readonly objectReferenceId: string;
  readonly propertyReferenceId: string;
  readonly service: BacnetProductionReadService;
  readonly deviceInstance: number;
  readonly reads: readonly BacnetProductionPropertyRead[];
  readonly targetPort: number;
  readonly udpMode: BacnetProductionUdpMode;
  readonly dnsMode: BacnetProductionDnsMode;
  readonly broadcastMode: BacnetProductionBroadcastMode;
  readonly segmentationMode: BacnetProductionSegmentationMode;
  readonly allowPrivateNetworkReference: boolean;
  readonly formulaPrefixPolicy: BacnetProductionFormulaPrefixPolicy;
  readonly dangerousKeyPolicy: BacnetProductionDangerousKeyPolicy;
} & BacnetProductionResourceLimits;

export type BacnetProductionResolvedTarget = {
  readonly hostname: string;
  readonly port: number;
};

export type BacnetProductionObjectAllowlistResolver = (referenceId: string) => readonly BacnetObjectType[] | undefined;

export type BacnetProductionPropertyAllowlistResolver = (
  referenceId: string,
) => readonly BacnetPropertyId[] | undefined;

export type BacnetProductionDeviceInstanceResolver = (referenceId: string) => number | undefined;

export type BacnetProductionTargetResolver = (
  targetReferenceId: string,
) => BacnetProductionResolvedTarget | undefined;

export type BacnetProductionDnsResolver = (hostname: string) => readonly string[] | undefined;

export type BacnetProductionReadRequest = {
  readonly config: BacnetProductionAdapterConfig;
  readonly resolveTarget: BacnetProductionTargetResolver;
  readonly resolveObjectAllowlist: BacnetProductionObjectAllowlistResolver;
  readonly resolvePropertyAllowlist: BacnetProductionPropertyAllowlistResolver;
  readonly resolveDeviceInstance?: BacnetProductionDeviceInstanceResolver;
  readonly resolveDns?: BacnetProductionDnsResolver;
  readonly testMode?: boolean;
};

export type BacnetProductionDiscoverRequest = BacnetProductionReadRequest & {
  readonly discoveryDeviceInstanceLow: number;
  readonly discoveryDeviceInstanceHigh: number;
};

export type BacnetProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type BacnetProductionReadSuccess = {
  readonly ok: true;
  readonly targetReferenceId: string;
  readonly targetHash: string;
  readonly service: BacnetService | BacnetProductionDiscoveryService;
  readonly recordCount: number;
  readonly records: readonly BacnetProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type BacnetProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: BacnetProductionErrorCode;
  readonly targetReferenceId?: string;
  readonly targetHash?: string;
  readonly service?: string;
  readonly objectReference?: string;
  readonly propertyReference?: string;
};

export type BacnetProductionReadResult = BacnetProductionReadSuccess | BacnetProductionReadFailure;

export type BacnetProductionReadOnlyAdapter = {
  readonly readPropertyOnce: (request: BacnetProductionReadRequest) => Promise<BacnetProductionReadResult>;
  readonly readPropertyMultipleOnce: (request: BacnetProductionReadRequest) => Promise<BacnetProductionReadResult>;
  readonly discoverOnce: (request: BacnetProductionDiscoverRequest) => Promise<BacnetProductionReadResult>;
};

export const BACNET_PRODUCTION_LIMIT_CAPS: BacnetProductionResourceLimits = {
  maxProperties: 64,
  maxObjects: 32,
  maxApduBytes: 1476,
  maxResponseBytes: 65536,
  maxSegments: 0,
  invokeTimeoutMs: 30_000,
  responseTimeoutMs: 30_000,
  maxProcessingMilliseconds: 30_000,
  maxRetries: 0,
};

export const BACNET_PRODUCTION_READ_SERVICES = ['READ_PROPERTY', 'READ_PROPERTY_MULTIPLE'] as const;

export const BACNET_PRODUCTION_DENIED_SERVICES = [
  'WRITE_PROPERTY',
  'WRITE_PROPERTY_MULTIPLE',
  'SUBSCRIBE_COV',
  'SUBSCRIBE_COV_PROPERTY',
  'DEVICE_COMMUNICATION_CONTROL',
  'REINITIALIZE_DEVICE',
  'ACKNOWLEDGE_ALARM',
  'ATOMIC_WRITE_FILE',
  'ADD_LIST_ELEMENT',
  'REMOVE_LIST_ELEMENT',
  'CREATE_OBJECT',
  'DELETE_OBJECT',
  'PRIVATE_TRANSFER',
] as const;

export const BACNET_PRODUCTION_METADATA_HOSTS = [
  '169.254.169.254',
  '100.100.100.200',
  'metadata.google.internal',
  'metadata.azure.internal',
  'localhost',
  'localhost.localdomain',
] as const;

export const BACNET_PRODUCTION_FORMULA_PREFIXES = ['=', '+', '-', '@'] as const;

export const BACNET_PRODUCTION_DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;

export const BACNET_PRODUCTION_ALLOWED_VALUE_TYPES = [
  'NULL',
  'BOOLEAN',
  'UNSIGNED',
  'SIGNED',
  'REAL',
  'DOUBLE',
  'CHARACTER_STRING',
  'ENUMERATED',
  'OBJECT_IDENTIFIER',
] as const;
