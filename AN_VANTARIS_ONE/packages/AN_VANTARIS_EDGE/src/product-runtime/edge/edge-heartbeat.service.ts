/**
 * S01 EDGE — heartbeat generation (WireEventV1 output).
 */

import { randomUUID } from 'node:crypto';

import type { WireEventV1 } from '../../generated/contracts/wire-event-v1.js';
import { WIRE_PROTOCOL_VERSION } from '../../generated/contracts/wire-event-v1.js';
import { attachWireEventSignature } from '../../generated/security/edge-link-security-headers.js';

export interface EdgeHeartbeatInput {
  readonly gatewayId: string;
  readonly signingSecret: string;
  readonly uptimeSeconds?: number;
  readonly traceId?: string;
}

export function buildEdgeHeartbeatEvent(input: EdgeHeartbeatInput): WireEventV1 {
  const timestamp = new Date().toISOString();
  const payload: Record<string, unknown> = {
    uptimeSeconds: input.uptimeSeconds ?? 0,
    edgeLayer: 'S01',
  };

  const unsigned = {
    protocolVersion: WIRE_PROTOCOL_VERSION,
    eventId: randomUUID(),
    gatewayId: input.gatewayId,
    eventType: 'gateway.heartbeat',
    timestamp,
    payload,
    ...(input.traceId !== undefined ? { traceId: input.traceId } : {}),
  } as Omit<WireEventV1, 'signature'>;

  return attachWireEventSignature(unsigned, input.signingSecret) as WireEventV1;
}
