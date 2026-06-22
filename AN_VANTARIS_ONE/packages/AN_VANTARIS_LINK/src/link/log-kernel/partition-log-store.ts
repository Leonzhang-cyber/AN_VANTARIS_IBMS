/**
 * Durable partition log — append-only storage kernel (no transport logic).
 */

import type { WireTransportEvent } from '../../generated/contracts/wire-event-v1.js';
import type { ILogStorage, LogRecord, LogRecordKind } from './storage/ilog-storage.js';

/** @deprecated Use LogRecord from ilog-storage.ts */
export type PartitionLogRecordKind = LogRecordKind;

/** @deprecated Use LogRecord from ilog-storage.ts */
export type PartitionLogEntry = LogRecord;

interface MutablePartitionLog {
  readonly records: LogRecord[];
  nextOffset: number;
}

export class PartitionLogStore implements ILogStorage {
  private readonly logs = new Map<number, MutablePartitionLog>();

  public append(partitionId: number, event: WireTransportEvent): LogRecord {
    return this.appendRecord(partitionId, event, 'enqueue');
  }

  public appendDrop(partitionId: number, event: WireTransportEvent): void {
    this.appendDropWithReason(partitionId, event, 'LINK_BACKPRESSURE_DROP');
  }

  public appendDropWithReason(
    partitionId: number,
    event: WireTransportEvent,
    reason: string,
  ): LogRecord {
    return this.appendRecord(partitionId, event, 'backpressure_drop', reason);
  }

  public readFrom(partitionId: number, offset: number): readonly LogRecord[] {
    const log = this.getLog(partitionId);
    return log.records.filter((record) => record.offset > offset);
  }

  public readEnqueueFrom(partitionId: number, offset: number): readonly LogRecord[] {
    return this.readFrom(partitionId, offset).filter((record) => record.kind === 'enqueue');
  }

  public getLatestOffset(partitionId: number): number {
    const log = this.getLog(partitionId);
    if (log.records.length === 0) {
      return -1;
    }

    return log.records[log.records.length - 1]!.offset;
  }

  public getPartitionRecordCount(partitionId: number): number {
    return this.getLog(partitionId).records.length;
  }

  public snapshot(partitionId: number): readonly LogRecord[] {
    return [...this.getLog(partitionId).records];
  }

  private appendRecord(
    partitionId: number,
    event: WireTransportEvent,
    kind: LogRecordKind,
    reason?: string,
  ): LogRecord {
    const log = this.getLog(partitionId);
    const offset = this.nextOffset(partitionId);
    const entry: LogRecord = {
      offset,
      partitionId,
      event,
      timestamp: Date.now(),
      kind,
      ...(reason !== undefined ? { reason } : {}),
    };

    log.records.push(entry);
    log.nextOffset = offset + 1;
    return entry;
  }

  private nextOffset(partitionId: number): number {
    const log = this.getLog(partitionId);
    return log.nextOffset;
  }

  private getLog(partitionId: number): MutablePartitionLog {
    let log = this.logs.get(partitionId);
    if (log === undefined) {
      log = { records: [], nextOffset: 0 };
      this.logs.set(partitionId, log);
    }
    return log;
  }
}

export function createPartitionLogStore(): PartitionLogStore {
  return new PartitionLogStore();
}

export type { ILogStorage, LogRecord, LogRecordKind };
