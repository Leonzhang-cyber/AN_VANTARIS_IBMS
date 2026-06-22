export type ModbusRegisterType = 'holding' | 'input' | 'coil' | 'discrete';

export interface ModbusRegisterMapping {
  readonly registerType: ModbusRegisterType;
  readonly address: number;
  readonly quantity: number;
  readonly pointRef: string;
  readonly assetRef: string;
  readonly unit: string;
  readonly scale: number;
}

export interface ModbusTcpReadonlyConfig {
  readonly connectorId: string;
  readonly host: string;
  readonly port: number;
  readonly unitId: number;
  readonly networkEnabled: boolean;
  readonly supportsWriteback: boolean;
  readonly fixturePath: string;
  readonly pollingIntervalMs: number;
  readonly timeoutMs: number;
  readonly retries: number;
  readonly registerMappings: readonly ModbusRegisterMapping[];
  readonly observedAtField: string;
}

export interface ModbusSyntheticRegister {
  readonly registerType: ModbusRegisterType;
  readonly address: number;
  readonly pointRef: string;
  readonly assetRef: string;
  readonly value: number | string | boolean;
  readonly unit: string;
  readonly quality: 'good' | 'bad' | 'uncertain';
  readonly scale: number;
  readonly metadata: Record<string, unknown>;
}

export interface ModbusSyntheticFixture {
  readonly source: string;
  readonly observedAt: string;
  readonly unitId: number;
  readonly registers: readonly ModbusSyntheticRegister[];
}

export interface ModbusTcpReadonlyPollResult {
  readonly ok: boolean;
  readonly connectorId: string;
  readonly registerCount: number;
  readonly registers: readonly ModbusSyntheticRegister[];
  readonly errors: readonly ModbusTcpReadonlyError[];
}

export interface ModbusTcpReadonlyValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
}

export interface ModbusTcpReadonlyError {
  readonly code: string;
  readonly message: string;
  readonly details?: Record<string, unknown>;
}

export interface ModbusTcpReadonlyStats {
  readonly registerCount: number;
  readonly validCount: number;
  readonly invalidCount: number;
  readonly bytesRead: number;
  readonly generatedAt: string;
}

export interface ModbusTcpReadonlyEvidence {
  readonly generatedAt: string;
  readonly config: ModbusTcpReadonlyConfig;
  readonly validation: ModbusTcpReadonlyValidationResult;
  readonly parse: {
    readonly ok: boolean;
    readonly errors: readonly ModbusTcpReadonlyError[];
    readonly registers: readonly ModbusSyntheticRegister[];
    readonly bytesRead: number;
    readonly fixturePath: string;
  };
  readonly stats: ModbusTcpReadonlyStats;
  readonly warnings: readonly string[];
}
