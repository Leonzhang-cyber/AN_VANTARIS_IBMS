export type ModbusTransport = 'MODBUS_TCP';
export type ModbusRegisterSpace = 'COIL' | 'DISCRETE_INPUT' | 'HOLDING_REGISTER' | 'INPUT_REGISTER';
export type ModbusByteOrder = 'BIG_ENDIAN' | 'LITTLE_ENDIAN';
export type ModbusWordOrder = 'BIG_ENDIAN' | 'LITTLE_ENDIAN';
export type ModbusDnsResolutionMode = 'MODELED_ONLY';
export type ModbusDecodeType = 'UInt16' | 'Int16' | 'UInt32' | 'Int32' | 'Float32' | 'Boolean' | 'RAW';

export type ModbusAddressRange = {
  readonly space: ModbusRegisterSpace;
  readonly start: number;
  readonly end: number;
};

export type ModbusTcpReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-04';
  readonly classification: 'CONTROLLED_MODBUS_TCP_READ_ONLY_FOUNDATION';
  readonly allowedTransports: readonly ModbusTransport[];
  readonly allowedFunctionCodes: readonly number[];
  readonly deniedFunctionCodes: readonly number[];
  readonly allowedTargets: readonly string[];
  readonly deniedTargets: readonly string[];
  readonly allowedPorts: readonly number[];
  readonly allowedUnitIds: readonly number[];
  readonly registerSpaces: readonly ModbusRegisterSpace[];
  readonly allowedAddressRanges: readonly ModbusAddressRange[];
  readonly maxRegistersPerRequest: number;
  readonly maxCoilsPerRequest: number;
  readonly maxResponseBytes: number;
  readonly timeoutMs: number;
  readonly maxRetryAttempts: number;
  readonly retryableErrors: readonly string[];
  readonly nonRetryableErrors: readonly string[];
  readonly backoffBaseMs: number;
  readonly backoffMultiplier: number;
  readonly backoffMaxMs: number;
  readonly byteOrder: ModbusByteOrder;
  readonly wordOrder: ModbusWordOrder;
  readonly networkAccessAllowed: false;
  readonly dnsResolutionMode: ModbusDnsResolutionMode;
  readonly syntheticTransportOnly: true;
  readonly writeOperationsAllowed: false;
  readonly candidateStatus: 'CONTROLLED_MODBUS_TCP_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_04_MODBUS_TCP_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type ModbusNormalizedTarget = {
  readonly originalTarget: string;
  readonly hostname: string;
  readonly port: number;
};

export type ModbusTargetValidation = ValidationResult & {
  readonly target?: ModbusNormalizedTarget;
};

export type ModbusTargetRiskEvaluation = ValidationResult & {
  readonly risks: readonly string[];
  readonly target?: ModbusNormalizedTarget;
};

export type ModbusRequestInput = {
  readonly target: string;
  readonly port?: number;
  readonly unitId: number | string;
  readonly functionCode: number | string;
  readonly registerSpace: ModbusRegisterSpace;
  readonly startAddress: number | string;
  readonly quantity: number | string;
  readonly credentialRef?: string;
  readonly username?: string;
  readonly password?: string;
  readonly token?: string;
};

export type ModbusRequestValidation = ValidationResult & {
  readonly functionCode?: number;
  readonly unitId?: number;
  readonly startAddress?: number;
  readonly quantity?: number;
  readonly registerSpace?: ModbusRegisterSpace;
};

export type ModbusResponseFrame = {
  readonly transactionId: number;
  readonly protocolId: number;
  readonly unitId: number;
  readonly functionCode: number;
  readonly byteCount?: number;
  readonly payload?: readonly number[];
  readonly exceptionCode?: number;
  readonly rawBytes?: readonly number[];
};

export type ModbusResponseValidation = ValidationResult & {
  readonly frame: ModbusResponseFrame;
};

export type ModbusRetryBackoff = {
  readonly attempt: number;
  readonly delayMs: number;
  readonly clamped: boolean;
};

export type ModbusRetryDecision = {
  readonly shouldRetry: boolean;
  readonly attempt: number;
  readonly maxAttempts: number;
  readonly exhausted: boolean;
  readonly reason?: string;
};

export type ModbusSyntheticFixtureRequest = ModbusRequestInput & {
  readonly transactionId?: number;
};

export type ModbusSyntheticFixtureResponse = ModbusResponseFrame & {
  readonly simulatedTimeout?: boolean;
  readonly simulatedErrorClass?: string;
  readonly malformed?: boolean;
};

export type ModbusSyntheticFixture = {
  readonly request: ModbusSyntheticFixtureRequest;
  readonly response: ModbusSyntheticFixtureResponse;
};

export type ModbusSyntheticTransportResult = {
  readonly accepted: boolean;
  readonly transportMode: 'SYNTHETIC_TRANSPORT_ONLY';
  readonly functionCode: number;
  readonly target: string;
  readonly port: number;
  readonly unitId: number;
  readonly retryDecision?: ModbusRetryDecision;
  readonly backoffMs?: number;
  readonly errors: readonly string[];
};

export type ModbusAcceptanceResult =
  | 'MODBUS_TCP_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'MODBUS_TCP_READ_ONLY_FOUNDATION_REJECTED';

export type ModbusRegisterDecodeInput = {
  readonly registers: readonly number[];
  readonly dataType: ModbusDecodeType;
  readonly byteOrder?: ModbusByteOrder;
  readonly wordOrder?: ModbusWordOrder;
};

export type ModbusRegisterDecodeResult = ValidationResult & {
  readonly values?: readonly number[] | readonly boolean[];
};
