// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import type { WireEventSignPayload, WireTransportEvent } from './wire-event-v1.js';

export function normalizeWireTimestampUtc(timestamp?: string): string {
  if (!timestamp) return new Date().toISOString();
  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) return new Date().toISOString();
  return parsed.toISOString();
}

export function buildWireEventSignPayload(event: WireTransportEvent): WireEventSignPayload {
  return {
    protocolVersion: event.protocolVersion,
    eventId: event.eventId,
    gatewayId: event.gatewayId,
    eventType: event.eventType,
    timestamp: event.timestamp,
    payload: event.payload,
  };
}

export function serializeWireEventSignInput(payload: WireEventSignPayload): string {
  return JSON.stringify(payload);
}

export function serializeWireEvent(event: WireTransportEvent): string {
  return JSON.stringify(event);
}

export function parseWireEventJson(body: string): WireTransportEvent | null {
  try {
    return JSON.parse(body) as WireTransportEvent;
  } catch {
    return null;
  }
}
