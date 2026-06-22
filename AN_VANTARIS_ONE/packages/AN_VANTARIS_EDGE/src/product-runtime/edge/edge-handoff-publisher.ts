import type { WireTransportEvent } from '../../generated/contracts/wire-event-v1.js';
import type { LinkHandoffEvent } from '../../generated/protocol/edge-to-link.mapper.js';

export type EdgeHandoffPublishStatus = 'accepted' | 'buffered' | 'failed';

export interface EdgeHandoffPublishResult {
  readonly status: EdgeHandoffPublishStatus;
  readonly reason?: string;
  readonly acceptedAt?: string;
}

export interface EdgeHandoffPublishEnvelope {
  readonly event: WireTransportEvent;
  readonly handoff: LinkHandoffEvent;
  readonly headers: Record<string, string>;
  readonly body: string;
}

export interface EdgeHandoffPublisher<TEnvelope = unknown> {
  publish(envelope: TEnvelope): Promise<EdgeHandoffPublishResult>;
}

export function createNoopEdgeHandoffPublisher(): EdgeHandoffPublisher<EdgeHandoffPublishEnvelope> {
  return {
    async publish(): Promise<EdgeHandoffPublishResult> {
      return { status: 'accepted', acceptedAt: new Date().toISOString() };
    },
  };
}
