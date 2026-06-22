/**
 * S02 LINK — queue management (transport only).
 */

import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';
import { transitionLinkState, type LinkDeliveryState, type LinkQueueRecord } from './link-state.js';

interface MutableQueueRecord {
  queueId: string;
  event: WireTransportEvent;
  state: LinkDeliveryState;
  attempts: number;
  enqueuedAt: string;
  lastAttemptAt: string | null;
  dlqReason: string | null;
}

export class LinkQueue {
  private readonly items: MutableQueueRecord[] = [];
  private sequence = 0;

  public enqueue(event: WireTransportEvent): LinkQueueRecord & { event: WireTransportEvent } {
    this.sequence += 1;
    const record: MutableQueueRecord = {
      queueId: `link-q-${this.sequence}`,
      event,
      state: 'PENDING',
      attempts: 0,
      enqueuedAt: new Date().toISOString(),
      lastAttemptAt: null,
      dlqReason: null,
    };
    this.items.push(record);
    return record;
  }

  public nextPending(): (LinkQueueRecord & { event: WireTransportEvent }) | undefined {
    return this.items.find((item) => item.state === 'PENDING' || item.state === 'RETRYING');
  }

  public applyDeliveryResult(
    queueId: string,
    deliverySucceeded: boolean,
    maxAttempts: number,
    dlqReason = 'delivery_exhausted',
  ): LinkDeliveryState | undefined {
    const item = this.items.find((entry) => entry.queueId === queueId);
    if (!item) {
      return undefined;
    }

    item.attempts += 1;
    item.lastAttemptAt = new Date().toISOString();
    item.state = transitionLinkState(item.state, deliverySucceeded, item.attempts, maxAttempts);

    if (item.state === 'FAILED') {
      item.dlqReason = dlqReason;
    }

    return item.state;
  }

  public dlqSnapshot(): readonly LinkQueueRecord[] {
    return this.items.filter((item) => item.state === 'FAILED');
  }

  public snapshot(): readonly LinkQueueRecord[] {
    return this.items.map(({ event: _event, ...record }) => record);
  }
}

export function createLinkQueue(): LinkQueue {
  return new LinkQueue();
}
