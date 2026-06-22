/**
 * S02 LINK — routing to CORE SYSTEM (S03) only.
 */

import type { LinkHandoffEvent } from '../generated/protocol/edge-to-link.mapper.js';

export interface CoreSystemRoute {
  readonly channel: 'http' | 'mqtt' | 'webhook';
  readonly target: string;
}

export function routeToCoreSystem(
  event: LinkHandoffEvent,
  coreSystemBaseUrl: string,
): CoreSystemRoute {
  if (event.eventType === 'gateway.heartbeat') {
    return {
      channel: 'http',
      target: `${coreSystemBaseUrl}/ingest/heartbeat`,
    };
  }

  return {
    channel: 'http',
    target: `${coreSystemBaseUrl}/ingest/events`,
  };
}
