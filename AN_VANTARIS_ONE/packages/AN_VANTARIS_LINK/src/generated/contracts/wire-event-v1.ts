// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export const WIRE_PROTOCOL_VERSION = 'v1' as const;
export const WIRE_PROTOCOL_VERSION_V1_1 = 'v1.1' as const;

export interface WireEventLifecycle {
  readonly edgeReceivedAt: string;
}

export interface WireEventMetrics {
  readonly ingestionLatencyMs?: number;
}

export interface WireEventV1 {
  readonly protocolVersion: string;
  readonly eventId: string;
  readonly gatewayId: string;
  readonly eventType: string;
  readonly timestamp: string;
  readonly payload: Record<string, any>;
  readonly signature: string;
  readonly dedupeKey?: string;
  readonly traceId?: string;
}

export interface WireEventV1_1 extends WireEventV1 {
  readonly protocolVersion: typeof WIRE_PROTOCOL_VERSION_V1_1;
  readonly traceId: string;
  readonly spanId?: string;
  readonly parentSpanId?: string;
  readonly lifecycle: WireEventLifecycle;
  readonly metrics?: WireEventMetrics;
}

export type WireTransportEvent = WireEventV1 | WireEventV1_1;

export interface WireEventInput {
  readonly gatewayId: string;
  readonly eventType: string;
  readonly payload: Record<string, unknown>;
  readonly timestamp?: string;
  readonly dedupeKey?: string;
  readonly traceId?: string;
}

export interface CoreWireTraceResponse {
  readonly traceId: string;
  readonly status: string;
}

export type WireEventSignPayload = Pick<
  WireEventV1,
  'protocolVersion' | 'eventId' | 'gatewayId' | 'eventType' | 'timestamp' | 'payload'
>;

export function isSupportedWireProtocolVersion(version: string): boolean {
  return version === WIRE_PROTOCOL_VERSION || version === WIRE_PROTOCOL_VERSION_V1_1;
}

export function isWireEventV1_1(event: WireTransportEvent): event is WireEventV1_1 {
  return event.protocolVersion === WIRE_PROTOCOL_VERSION_V1_1;
}
