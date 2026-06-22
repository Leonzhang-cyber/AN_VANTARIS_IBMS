import type { EdgeRuntimeMode, HardwareKeyGuardState } from './types.js';

export interface HardwareKeyGuardConfig {
  readonly runtimeMode: EdgeRuntimeMode;
  readonly required: boolean;
  readonly provider: string;
  readonly serial: string;
  readonly label: string;
  readonly presentSignal: boolean;
  readonly explicitRealVerifierSuccess: boolean;
}

function parseBool(raw: string | undefined, fallback: boolean): boolean {
  if (raw == null) return fallback;
  return raw.toLowerCase() == 'true' || raw == '1' || raw.toLowerCase() == 'yes';
}

export function loadHardwareKeyGuardConfigFromEnv(env: NodeJS.ProcessEnv): HardwareKeyGuardConfig {
  const runtimeMode = (env.EDGE_RUNTIME_MODE ?? 'production') as EdgeRuntimeMode;
  const explicitRealVerifierSuccess =
    parseBool(env.EDGE_HARDWARE_KEY_VERIFIED, false) && (env.EDGE_HARDWARE_KEY_VERIFIER_SOURCE ?? '') == 'real-sdk';
  return {
    runtimeMode,
    required: parseBool(env.EDGE_HARDWARE_KEY_REQUIRED, false),
    provider: env.EDGE_HARDWARE_KEY_PROVIDER ?? 'pkcs11-placeholder',
    serial: env.EDGE_HARDWARE_KEY_SERIAL ?? 'HSM-SERIAL-PLACEHOLDER',
    label: env.EDGE_HARDWARE_KEY_LABEL ?? 'HSM-LABEL-PLACEHOLDER',
    presentSignal: parseBool(env.EDGE_HARDWARE_KEY_PRESENT, false),
    explicitRealVerifierSuccess,
  };
}

export function evaluateHardwareKeyGuard(config: HardwareKeyGuardConfig): HardwareKeyGuardState {
  if (!config.required) {
    return {
      required: false,
      provider: config.provider,
      serial: config.serial,
      label: config.label,
      present: config.presentSignal,
      status: 'disabled',
      locked: false,
      lockedReason: null,
      runtimeMode: config.runtimeMode,
    };
  }

  if (config.explicitRealVerifierSuccess) {
    return {
      required: true,
      provider: config.provider,
      serial: config.serial,
      label: config.label,
      present: true,
      status: 'verified',
      locked: false,
      lockedReason: null,
      runtimeMode: config.runtimeMode,
    };
  }

  const isProduction = config.runtimeMode == 'production';
  const status = isProduction ? 'locked' : config.presentSignal ? 'implementation_pending' : 'missing';
  const locked = isProduction;

  return {
    required: true,
    provider: config.provider,
    serial: config.serial,
    label: config.label,
    present: config.presentSignal,
    status,
    locked,
    lockedReason: locked ? 'hardware_key_verification_required_for_production' : null,
    runtimeMode: config.runtimeMode,
  };
}
