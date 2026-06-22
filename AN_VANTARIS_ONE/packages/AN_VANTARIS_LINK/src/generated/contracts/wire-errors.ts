// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export const WIRE_ERROR_CODES = {
  WIRE_ZONE_VIOLATION: 'WIRE_ZONE_VIOLATION',
  WIRE_FORMAT_INVALID: 'WIRE_FORMAT_INVALID',
  WIRE_PROTOCOL_MISSING: 'WIRE_PROTOCOL_MISSING',
  MISSING_GATEWAY_ID: 'MISSING_GATEWAY_ID',
  UNSUPPORTED_PROTOCOL: 'UNSUPPORTED_PROTOCOL',
  TIMESTAMP_SKEW: 'TIMESTAMP_SKEW',
  INVALID_SIGNATURE: 'INVALID_SIGNATURE',
  LINK_BACKPRESSURE_DROP: 'LINK_BACKPRESSURE_DROP',
} as const;

export type WireErrorCode = (typeof WIRE_ERROR_CODES)[keyof typeof WIRE_ERROR_CODES];

export class WireTransportError extends Error {
  public constructor(
    public readonly code: WireErrorCode,
    message: string,
    public readonly traceId?: string,
  ) {
    super(message);
  }
}

export class WireTraceError extends WireTransportError {}
