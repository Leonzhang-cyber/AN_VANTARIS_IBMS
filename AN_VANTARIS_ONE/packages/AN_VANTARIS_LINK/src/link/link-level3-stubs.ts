/**
 * LINK-owned minimal Level3/cluster bridge stubs for UFMS split-package import isolation.
 */

import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';

export interface MachineIdentityRef {
  readonly identityRef: string;
}

export interface Level3IngressMessage {
  readonly messageId?: string;
  readonly queueId?: string;
}

export interface ProcessLevel3IngressEventResult {
  readonly status: 'accepted_queued' | 'rejected_dead_lettered';
  readonly warnings: readonly string[];
  readonly message?: Level3IngressMessage;
  readonly partitionAssignment?: { readonly partitionId: number };
  readonly context: { readonly rejectionReason?: string };
}

export interface Level3LinkRuntimeAdapter {
  processLevel3IngressEvent(input: Record<string, unknown>): ProcessLevel3IngressEventResult;
  processSecurityRejectedIngressEvent(
    input: Record<string, unknown>,
    payload: Record<string, unknown>,
    reason: string,
  ): ProcessLevel3IngressEventResult;
}

export function buildSignedEdgeEventFromWireTransport(
  event: WireTransportEvent,
  context: Record<string, unknown>,
): { readonly event: WireTransportEvent; readonly context: Record<string, unknown> } {
  return { event, context };
}

export function validateSignedEdgeEvent(
  _event: unknown,
  _options: Record<string, unknown>,
): { readonly valid: boolean; readonly issues: readonly { readonly message: string }[] } {
  return { valid: true, issues: [] };
}

export function extractLegacyLevel3RoutingContext(event: WireTransportEvent): {
  readonly siteId?: string;
  readonly sourceSystemId?: string;
} {
  return {
    ...(typeof event.payload.siteId === 'string' ? { siteId: event.payload.siteId } : {}),
    ...(typeof event.payload.sourceSystemId === 'string'
      ? { sourceSystemId: event.payload.sourceSystemId }
      : {}),
  };
}

export function canUseCanonicalLevel3Routing(input: {
  readonly siteId?: string;
  readonly gatewayId?: string;
  readonly sourceSystemId?: string;
}): boolean {
  return Boolean(input.siteId && input.gatewayId && input.sourceSystemId);
}

export interface ClusterState {
  readonly partitionMap: Record<number, string>;
}
