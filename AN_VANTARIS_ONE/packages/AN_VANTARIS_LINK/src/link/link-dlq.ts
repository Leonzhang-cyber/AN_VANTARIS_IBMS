/**
 * S02 LINK — DLQ handling (transport failures only).
 * Optional durable append-only log backing per partition.
 */

import type { LinkHandoffEvent } from '../generated/protocol/edge-to-link.mapper.js';
import type { PartitionDlqLogStore } from './log-kernel/partition-dlq-log-store.js';
import type { LinkQueueRecord } from './link-state.js';

export interface LinkDlqEntry {
  readonly queueId: string;
  readonly event: LinkHandoffEvent;
  readonly reason: string;
  readonly movedAt: string;
}

export class LinkDlq {
  private readonly entries: LinkDlqEntry[] = [];

  public constructor(
    private readonly partitionId?: number,
    private readonly dlqLog?: PartitionDlqLogStore,
  ) {}

  public move(record: LinkQueueRecord, event: LinkHandoffEvent, reason: string): LinkDlqEntry {
    const entry: LinkDlqEntry = {
      queueId: record.queueId,
      event,
      reason,
      movedAt: new Date().toISOString(),
    };
    this.entries.push(entry);

    if (this.dlqLog !== undefined && this.partitionId !== undefined) {
      this.dlqLog.append(this.partitionId, record.queueId, event, reason, entry.movedAt);
    }

    return entry;
  }

  public snapshot(): readonly LinkDlqEntry[] {
    return [...this.entries];
  }

  public replay(): readonly LinkDlqEntry[] {
    if (this.dlqLog === undefined || this.partitionId === undefined) {
      return this.snapshot();
    }

    return this.dlqLog.replay(this.partitionId).map((record) => ({
      queueId: record.queueId,
      event: record.event,
      reason: record.reason,
      movedAt: record.movedAt,
    }));
  }
}

export function createLinkDlq(partitionId?: number, dlqLog?: PartitionDlqLogStore): LinkDlq {
  return new LinkDlq(partitionId, dlqLog);
}
