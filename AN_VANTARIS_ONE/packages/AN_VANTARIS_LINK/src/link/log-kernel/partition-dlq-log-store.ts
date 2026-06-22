/**
 * Durable partition DLQ log — append-only, replayable.
 */

import type { LinkHandoffEvent } from '../../generated/protocol/edge-to-link.mapper.js';

export interface PartitionDlqLogEntry {
  readonly offset: number;
  readonly partitionId: number;
  readonly queueId: string;
  readonly event: LinkHandoffEvent;
  readonly reason: string;
  readonly movedAt: string;
  readonly timestamp: number;
}

interface MutableDlqLog {
  readonly records: PartitionDlqLogEntry[];
  nextOffset: number;
}

export class PartitionDlqLogStore {
  private readonly logs = new Map<number, MutableDlqLog>();

  public append(
    partitionId: number,
    queueId: string,
    event: LinkHandoffEvent,
    reason: string,
    movedAt: string,
  ): PartitionDlqLogEntry {
    const log = this.getLog(partitionId);
    const offset = log.nextOffset;
    const entry: PartitionDlqLogEntry = {
      offset,
      partitionId,
      queueId,
      event,
      reason,
      movedAt,
      timestamp: Date.now(),
    };

    log.records.push(entry);
    log.nextOffset = offset + 1;
    return entry;
  }

  public readFrom(partitionId: number, offset: number): readonly PartitionDlqLogEntry[] {
    const log = this.getLog(partitionId);
    return log.records.filter((record) => record.offset > offset);
  }

  public getLatestOffset(partitionId: number): number {
    const log = this.getLog(partitionId);
    if (log.records.length === 0) {
      return -1;
    }

    return log.records[log.records.length - 1]!.offset;
  }

  public snapshot(partitionId: number): readonly PartitionDlqLogEntry[] {
    return [...this.getLog(partitionId).records];
  }

  public replay(partitionId: number): readonly PartitionDlqLogEntry[] {
    return this.snapshot(partitionId);
  }

  private getLog(partitionId: number): MutableDlqLog {
    let log = this.logs.get(partitionId);
    if (log === undefined) {
      log = { records: [], nextOffset: 0 };
      this.logs.set(partitionId, log);
    }
    return log;
  }
}

export function createPartitionDlqLogStore(): PartitionDlqLogStore {
  return new PartitionDlqLogStore();
}
