/**
 * S01 EDGE — WAL buffer (offline replay support, no business logic).
 */

import type { WireTransportEvent } from '../../generated/contracts/wire-event-v1.js';

export interface EdgeWalEntry {
  readonly sequence: number;
  readonly event: WireTransportEvent;
  readonly writtenAt: string;
}

export class EdgeWalBuffer {
  private readonly entries: EdgeWalEntry[] = [];
  private sequence = 0;

  public append(event: WireTransportEvent): EdgeWalEntry {
    this.sequence += 1;
    const entry: EdgeWalEntry = {
      sequence: this.sequence,
      event,
      writtenAt: new Date().toISOString(),
    };
    this.entries.push(entry);
    return entry;
  }

  public replay(): readonly EdgeWalEntry[] {
    return [...this.entries];
  }

  public size(): number {
    return this.entries.length;
  }
}

export function createEdgeWalBuffer(): EdgeWalBuffer {
  return new EdgeWalBuffer();
}
