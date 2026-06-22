// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import type { WireTransportEvent } from '../contracts/wire-event-v1.js';

export type LinkHandoffEvent = WireTransportEvent & {
  readonly signature: string;
};

export function mapEdgeToLink(event: WireTransportEvent): LinkHandoffEvent {
  return {
    ...event,
    signature: event.signature ?? '',
  };
}
