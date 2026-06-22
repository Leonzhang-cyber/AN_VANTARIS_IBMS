/**
 * S02 LINK — Kafka-style partitioned queues (per-partition buffer, retry, DLQ).
 * Durable append-only log is source of truth; in-memory buffer is execution-only.
 */

import type { WireTransportEvent } from '../generated/contracts/wire-event-v1.js';
import {
  createPartitionDlqLogStore,
  PartitionDlqLogStore,
} from './log-kernel/partition-dlq-log-store.js';
import {
  createPartitionLogStore,
  PartitionLogStore,
  type PartitionLogEntry,
} from './log-kernel/partition-log-store.js';
import { createLinkDlq, LinkDlq } from './link-dlq.js';
import {
  createPartitionRouter,
  PartitionRouter,
  DEFAULT_PARTITION_COUNT,
  routeWithOptionalCanonicalPartition,
  type ExtendedPartitionRouteResult,
  type OptionalCanonicalRouteOptions,
  type PartitionRoutingMode,
} from './link-partition-router.js';
import { transitionLinkState, type LinkDeliveryState, type LinkQueueRecord } from './link-state.js';

export const DEFAULT_MAX_PARTITION_QUEUE_SIZE = 10_000;

export interface LinkPartitionedQueuesOptions {
  readonly partitionCount?: number;
  readonly maxPartitionQueueSize?: number;
  readonly router?: PartitionRouter;
  readonly logStore?: PartitionLogStore;
  readonly dlqLogStore?: PartitionDlqLogStore;
}

interface MutableQueueRecord {
  queueId: string;
  event: WireTransportEvent;
  state: LinkDeliveryState;
  attempts: number;
  enqueuedAt: string;
  lastAttemptAt: string | null;
  dlqReason: string | null;
  logOffset: number;
}

export interface PartitionEnqueueAccepted {
  readonly accepted: true;
  readonly partitionId: number;
  readonly offset: number;
  /** @deprecated Use partitionId */
  readonly partition: number;
  readonly queueId: string;
  /** @deprecated Use offset */
  readonly logOffset: number;
  readonly record: LinkQueueRecord & { event: WireTransportEvent };
}

export interface PartitionBackpressureDrop {
  readonly accepted: false;
  readonly partitionId: number;
  readonly offset: number;
  /** @deprecated Use partitionId */
  readonly partition: number;
  readonly reason: 'LINK_BACKPRESSURE_DROP';
  /** @deprecated Use offset */
  readonly logOffset: number;
}

export type PartitionPushResult = PartitionEnqueueAccepted | PartitionBackpressureDrop;

export type PartitionPushWithRoutingResult = PartitionPushResult & {
  readonly routingMode: PartitionRoutingMode;
  readonly routingKey: string;
  readonly warnings?: readonly string[];
};

export class LinkPartitionQueue {
  private readonly buffer: MutableQueueRecord[] = [];
  private sequence = 0;

  public constructor(
    public readonly partitionIndex: number,
    private readonly maxSize: number,
    private readonly logStore: PartitionLogStore,
    public readonly dlq: LinkDlq,
  ) {}

  public get pendingSize(): number {
    return this.buffer.filter((item) => item.state === 'PENDING' || item.state === 'RETRYING').length;
  }

  public get retrySize(): number {
    return this.buffer.filter((item) => item.state === 'RETRYING').length;
  }

  public push(event: WireTransportEvent): PartitionPushResult {
    if (this.pendingSize >= this.maxSize) {
      const dropEntry = this.logStore.appendDropWithReason(
        this.partitionIndex,
        event,
        'LINK_BACKPRESSURE_DROP',
      );

      return {
        accepted: false,
        partitionId: this.partitionIndex,
        offset: dropEntry.offset,
        partition: this.partitionIndex,
        reason: 'LINK_BACKPRESSURE_DROP',
        logOffset: dropEntry.offset,
      };
    }

    const logEntry = this.logStore.append(this.partitionIndex, event);
    return this.pushFromLogEntry(logEntry);
  }

  public pushFromLogEntry(logEntry: PartitionLogEntry): PartitionEnqueueAccepted {
    this.sequence += 1;
    const record: MutableQueueRecord = {
      queueId: `link-q-p${this.partitionIndex}-${this.sequence}`,
      event: logEntry.event,
      state: 'PENDING',
      attempts: 0,
      enqueuedAt: new Date(logEntry.timestamp).toISOString(),
      lastAttemptAt: null,
      dlqReason: null,
      logOffset: logEntry.offset,
    };
    this.buffer.push(record);

    return {
      accepted: true,
      partitionId: this.partitionIndex,
      offset: logEntry.offset,
      partition: this.partitionIndex,
      queueId: record.queueId,
      logOffset: logEntry.offset,
      record,
    };
  }

  public restoreFromLogEntry(logEntry: PartitionLogEntry): PartitionEnqueueAccepted {
    return this.pushFromLogEntry(logEntry);
  }

  public clearExecutionBuffer(): void {
    this.buffer.length = 0;
    this.sequence = 0;
  }

  public nextPending(): (LinkQueueRecord & { event: WireTransportEvent; logOffset: number }) | undefined {
    return this.buffer.find((item) => item.state === 'PENDING' || item.state === 'RETRYING');
  }

  public applyDeliveryResult(
    queueId: string,
    deliverySucceeded: boolean,
    maxAttempts: number,
    dlqReason = 'delivery_exhausted',
  ): LinkDeliveryState | undefined {
    const item = this.buffer.find((entry) => entry.queueId === queueId);
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

  public snapshot(): readonly LinkQueueRecord[] {
    return this.buffer.map(({ event: _event, logOffset: _logOffset, ...record }) => record);
  }

  public retrySnapshot(): readonly LinkQueueRecord[] {
    return this.buffer
      .filter((item) => item.state === 'RETRYING')
      .map(({ event: _event, logOffset: _logOffset, ...record }) => record);
  }
}

export class LinkPartitionedQueues {
  private readonly partitions: LinkPartitionQueue[];
  private readonly router: PartitionRouter;
  private readonly logStore: PartitionLogStore;
  private readonly dlqLogStore: PartitionDlqLogStore;
  private roundRobinCursor = 0;

  public constructor(options: LinkPartitionedQueuesOptions = {}) {
    this.router = options.router ?? createPartitionRouter(options.partitionCount ?? DEFAULT_PARTITION_COUNT);
    this.logStore = options.logStore ?? createPartitionLogStore();
    this.dlqLogStore = options.dlqLogStore ?? createPartitionDlqLogStore();
    const partitionCount = this.router.getPartitionCount();
    const maxSize = options.maxPartitionQueueSize ?? DEFAULT_MAX_PARTITION_QUEUE_SIZE;

    this.partitions = Array.from({ length: partitionCount }, (_, index) => {
      const dlq = createLinkDlq(index, this.dlqLogStore);
      return new LinkPartitionQueue(index, maxSize, this.logStore, dlq);
    });
  }

  public getLogStore(): PartitionLogStore {
    return this.logStore;
  }

  public getDlqLogStore(): PartitionDlqLogStore {
    return this.dlqLogStore;
  }

  public getRouter(): PartitionRouter {
    return this.router;
  }

  public getPartitionCount(): number {
    return this.partitions.length;
  }

  public getPartition(partition: number): LinkPartitionQueue {
    const target = this.partitions[partition];
    if (target === undefined) {
      throw new Error(`partition ${partition} is out of range`);
    }
    return target;
  }

  public push(event: WireTransportEvent): PartitionPushResult {
    const route = this.router.route(event);
    return this.getPartition(route.partition).push(route.payload);
  }

  /**
   * Opt-in canonical Level 3 partition routing when full context is present.
   * Legacy gateway-only routing remains when canonicalRoutingEnabled is false or context incomplete.
   */
  public pushWithRoutingOption(
    event: WireTransportEvent,
    options: OptionalCanonicalRouteOptions = {},
  ): PartitionPushWithRoutingResult {
    const route: ExtendedPartitionRouteResult = routeWithOptionalCanonicalPartition(
      event,
      this.router,
      options,
    );
    const pushResult = this.getPartition(route.partition).push(route.payload);
    return {
      ...pushResult,
      routingMode: route.routingMode,
      routingKey: route.key,
      ...(route.warnings !== undefined ? { warnings: route.warnings } : {}),
    };
  }

  public nextPending(): (LinkQueueRecord & { event: WireTransportEvent; logOffset: number; partition: number }) | undefined {
    const count = this.partitions.length;
    for (let offset = 0; offset < count; offset += 1) {
      const index = (this.roundRobinCursor + offset) % count;
      const pending = this.partitions[index]?.nextPending();
      if (pending !== undefined) {
        this.roundRobinCursor = (index + 1) % count;
        return { ...pending, partition: index };
      }
    }

    return undefined;
  }

  public applyDeliveryResult(
    queueId: string,
    deliverySucceeded: boolean,
    maxAttempts: number,
    dlqReason?: string,
  ): LinkDeliveryState | undefined {
    for (const partition of this.partitions) {
      const state = partition.applyDeliveryResult(queueId, deliverySucceeded, maxAttempts, dlqReason);
      if (state !== undefined) {
        return state;
      }
    }

    return undefined;
  }

  public totalPendingSize(): number {
    return this.partitions.reduce((sum, partition) => sum + partition.pendingSize, 0);
  }

  public clearExecutionBuffer(partitionId: number): void {
    this.getPartition(partitionId).clearExecutionBuffer();
  }

  public restoreEnqueueEntries(partitionId: number, entries: readonly PartitionLogEntry[]): number {
    const partition = this.getPartition(partitionId);
    for (const entry of entries) {
      partition.restoreFromLogEntry(entry);
    }
    return entries.length;
  }
}

export function createLinkPartitionedQueues(options?: LinkPartitionedQueuesOptions): LinkPartitionedQueues {
  return new LinkPartitionedQueues(options);
}

export function logLinkBackpressureDrop(event: WireTransportEvent, partition: number): void {
  console.error(
    JSON.stringify({
      layer: 'LINK',
      action: 'LINK_BACKPRESSURE_DROP',
      partition,
      gatewayId: event.gatewayId,
      eventId: event.eventId,
      timestamp: new Date().toISOString(),
    }),
  );
}

export type { PartitionLogEntry, PartitionLogStore, PartitionDlqLogStore };
