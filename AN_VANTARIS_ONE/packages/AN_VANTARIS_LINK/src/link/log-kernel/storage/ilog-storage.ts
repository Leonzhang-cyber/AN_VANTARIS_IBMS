/**
 * Partition log storage contract — no implementation (Kafka-ready abstraction).
 */

import type { WireTransportEvent } from '../../../generated/contracts/wire-event-v1.js';

export type LogRecordKind = 'enqueue' | 'backpressure_drop';

export interface LogRecord {
  readonly offset: number;
  readonly partitionId: number;
  readonly event: WireTransportEvent;
  readonly timestamp: number;
  readonly kind: LogRecordKind;
  readonly reason?: string;
}

export interface ILogStorage {
  append(partitionId: number, event: WireTransportEvent): LogRecord;

  appendDrop(partitionId: number, event: WireTransportEvent): void;

  readFrom(partitionId: number, offset: number): readonly LogRecord[];

  getLatestOffset(partitionId: number): number;
}
