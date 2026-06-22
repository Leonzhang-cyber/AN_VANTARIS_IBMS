/**
 * EDGE-owned minimal observability shim for split-package import isolation.
 */

import type { WireTransportEvent } from '../../generated/contracts/wire-event-v1.js';
import type { LinkHandoffEvent } from '../../generated/protocol/edge-to-link.mapper.js';

export interface WireObserver {
  observeEdge(event: WireTransportEvent): void;
  observeLink(event: LinkHandoffEvent): void;
}

export const wireObserver: WireObserver = {
  observeEdge() {
    // no-op in minimal restore phase
  },
  observeLink() {
    // no-op in minimal restore phase
  },
};

export function buildLifecycle(edgeReceivedAt: string): { readonly edgeReceivedAt: string } {
  return { edgeReceivedAt };
}
