// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import type { WireTransportEvent } from './wire-event-v1.js';

export function freezeWireEvent<T extends WireTransportEvent>(event: T): Readonly<T> {
  return Object.freeze(event);
}

export function isWireEventFrozen(event: WireTransportEvent | null | undefined): boolean {
  return event !== null && event !== undefined && Object.isFrozen(event);
}
