// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import { createHmac, timingSafeEqual } from 'node:crypto';

import {
  buildWireEventSignPayload,
  serializeWireEventSignInput,
} from '../contracts/wire-serializer-v1.js';
import type { WireEventSignPayload, WireTransportEvent } from '../contracts/wire-event-v1.js';

export interface EdgeLinkSecurityContext {
  readonly machineId: string;
  readonly credentialRef: string;
  readonly timestamp: string;
  readonly signature: string;
}

export function computeWireEventSignature(
  payload: WireEventSignPayload,
  signingSecret: string,
): string {
  const canonical = serializeWireEventSignInput(payload);
  return createHmac('sha256', signingSecret).update(canonical).digest('hex');
}

export function signWireEventPayload(
  payload: WireEventSignPayload,
  signingSecret: string,
): string {
  return computeWireEventSignature(payload, signingSecret);
}

export function verifyWireEventSignature(event: WireTransportEvent, signingSecret: string): boolean {
  const signPayload = buildWireEventSignPayload(event);
  const expected = computeWireEventSignature(signPayload, signingSecret);
  if (event.signature.length !== expected.length) {
    return false;
  }
  return timingSafeEqual(Buffer.from(event.signature, 'utf8'), Buffer.from(expected, 'utf8'));
}

export function attachWireEventSignature<T extends Omit<WireTransportEvent, 'signature'>>(
  event: T,
  signingSecret: string,
): T & { readonly signature: string } {
  const payload = buildWireEventSignPayload({
    protocolVersion: event.protocolVersion,
    eventId: event.eventId,
    gatewayId: event.gatewayId,
    eventType: event.eventType,
    timestamp: event.timestamp,
    payload: event.payload,
    signature: '',
  });
  return {
    ...event,
    signature: signWireEventPayload(payload, signingSecret),
  };
}

export function buildEdgeLinkHeaders(
  machineId: string,
  credentialRef: string,
  timestamp: string,
  signature: string,
): Record<string, string> {
  return {
    machineId,
    credentialRef,
    timestamp,
    signature,
  };
}

export function signEdgeEventPayload(
  payload: WireEventSignPayload,
  signingSecret: string,
): string {
  return signWireEventPayload(payload, signingSecret);
}

export function extractLinkIngressHeaders(
  headers: Record<string, string | undefined>,
): EdgeLinkSecurityContext | null {
  const signature = headers.signature;
  if (!signature) {
    return null;
  }
  return {
    machineId: headers.machineId ?? '',
    credentialRef: headers.credentialRef ?? '',
    timestamp: headers.timestamp ?? '',
    signature,
  };
}
