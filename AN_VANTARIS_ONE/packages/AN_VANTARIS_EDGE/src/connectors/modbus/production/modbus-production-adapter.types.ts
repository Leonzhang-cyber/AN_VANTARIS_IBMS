export type ModbusProductionAdapterMode = 'PRODUCTION_MODBUS_TCP_READONLY';

export type ModbusProductionFunctionCode = 1 | 2 | 3 | 4;

export type ModbusProductionTcpMode = 'PRODUCTION_TCP' | 'LOOPBACK_TEST';

export type ModbusProductionDnsMode = 'DENY' | 'INJECTED_TEST';

export type ModbusProductionByteOrder = 'BIG_ENDIAN' | 'LITTLE_ENDIAN';

export type ModbusProductionWordOrder = 'BIG_ENDIAN' | 'LITTLE_ENDIAN';

export type ModbusProductionDataType = 'uint16' | 'int16' | 'uint32' | 'int32' | 'float32' | 'boolean' | 'raw';

export type ModbusProductionFormulaPrefixPolicy = 'REJECT' | 'MARK';

export type ModbusProductionDangerousKeyPolicy = 'REJECT';

export type ModbusProductionErrorCode =
  | 'MODBUS_CONFIG_INVALID'
  | 'MODBUS_TARGET_REFERENCE_NOT_FOUND'
  | 'MODBUS_TARGET_NOT_ALLOWLISTED'
  | 'MODBUS_DNS_NOT_ALLOWED'
  | 'MODBUS_DNS_RESULT_REJECTED'
  | 'MODBUS_METADATA_TARGET_REJECTED'
  | 'MODBUS_PORT_NOT_ALLOWED'
  | 'MODBUS_UNIT_ID_INVALID'
  | 'MODBUS_FUNCTION_NOT_ALLOWED'
  | 'MODBUS_ADDRESS_INVALID'
  | 'MODBUS_QUANTITY_INVALID'
  | 'MODBUS_CONNECT_TIMEOUT'
  | 'MODBUS_RESPONSE_TIMEOUT'
  | 'MODBUS_FRAME_SIZE_LIMIT_EXCEEDED'
  | 'MODBUS_MBAP_INVALID'
  | 'MODBUS_TRANSACTION_MISMATCH'
  | 'MODBUS_UNIT_ID_MISMATCH'
  | 'MODBUS_FUNCTION_MISMATCH'
  | 'MODBUS_EXCEPTION_RESPONSE'
  | 'MODBUS_PDU_INVALID'
  | 'MODBUS_BYTE_COUNT_INVALID'
  | 'MODBUS_DATA_TYPE_UNSUPPORTED'
  | 'MODBUS_DECODE_FAILED'
  | 'MODBUS_FOUNDATION_VALIDATION_FAILED'
  | 'MODBUS_REQUEST_FAILED'
  | 'MODBUS_ADAPTER_DISABLED';

export type ModbusProductionResourceLimits = {
  readonly maxFrameBytes: number;
  readonly maxQuantity: number;
  readonly maxRegisterAddress: number;
  readonly connectTimeoutMs: number;
  readonly responseTimeoutMs: number;
  readonly maxRetryCount: number;
  readonly maxProcessingMilliseconds: number;
};

export type ModbusProductionAdapterConfig = {
  readonly adapterMode: ModbusProductionAdapterMode;
  readonly enabled: boolean;
  readonly targetReferenceId: string;
  readonly unitId: number;
  readonly functionCode: ModbusProductionFunctionCode;
  readonly startAddress: number;
  readonly quantity: number;
  readonly byteOrder: ModbusProductionByteOrder;
  readonly wordOrder: ModbusProductionWordOrder;
  readonly dataType: ModbusProductionDataType;
  readonly targetPort: number;
  readonly tcpMode: ModbusProductionTcpMode;
  readonly dnsMode: ModbusProductionDnsMode;
  readonly allowPrivateNetworkReference: boolean;
  readonly formulaPrefixPolicy: ModbusProductionFormulaPrefixPolicy;
  readonly dangerousKeyPolicy: ModbusProductionDangerousKeyPolicy;
} & ModbusProductionResourceLimits;

export type ModbusProductionResolvedTarget = {
  readonly hostname: string;
  readonly port: number;
};

export type ModbusProductionTargetResolver = (
  targetReferenceId: string,
) => ModbusProductionResolvedTarget | undefined;

export type ModbusProductionDnsResolver = (hostname: string) => readonly string[] | undefined;

export type ModbusProductionReadRequest = {
  readonly config: ModbusProductionAdapterConfig;
  readonly resolveTarget: ModbusProductionTargetResolver;
  readonly resolveDns?: ModbusProductionDnsResolver;
  readonly testMode?: boolean;
};

export type ModbusProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type ModbusProductionReadSuccess = {
  readonly ok: true;
  readonly targetReferenceId: string;
  readonly targetHash: string;
  readonly functionCode: ModbusProductionFunctionCode;
  readonly unitId: number;
  readonly recordCount: number;
  readonly records: readonly ModbusProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type ModbusProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: ModbusProductionErrorCode;
  readonly targetReferenceId?: string;
  readonly targetHash?: string;
  readonly functionCode?: number;
  readonly unitId?: number;
};

export type ModbusProductionReadResult = ModbusProductionReadSuccess | ModbusProductionReadFailure;

export type ModbusProductionReadOnlyAdapter = {
  readonly readOnce: (request: ModbusProductionReadRequest) => Promise<ModbusProductionReadResult>;
};

export const MODBUS_PRODUCTION_LIMIT_CAPS: ModbusProductionResourceLimits = {
  maxFrameBytes: 260,
  maxQuantity: 2000,
  maxRegisterAddress: 65535,
  connectTimeoutMs: 30_000,
  responseTimeoutMs: 30_000,
  maxRetryCount: 0,
  maxProcessingMilliseconds: 30_000,
};

export const MODBUS_PRODUCTION_READ_FUNCTION_CODES = [1, 2, 3, 4] as const;

export const MODBUS_PRODUCTION_WRITE_FUNCTION_CODES = [5, 6, 15, 16, 22, 23] as const;

export const MODBUS_PRODUCTION_COIL_MAX_QUANTITY = 2000;

export const MODBUS_PRODUCTION_REGISTER_MAX_QUANTITY = 125;

export const MODBUS_PRODUCTION_METADATA_HOSTS = [
  '169.254.169.254',
  '100.100.100.200',
  'metadata.google.internal',
  'metadata.azure.internal',
  'localhost',
  'localhost.localdomain',
] as const;

export const MODBUS_PRODUCTION_FORMULA_PREFIXES = ['=', '+', '-', '@'] as const;

export const MODBUS_PRODUCTION_DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;
