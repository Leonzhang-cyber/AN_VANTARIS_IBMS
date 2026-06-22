/**
 * S02 LINK — delivery to CORE SYSTEM (S03) only.
 * Partition-aware, single-attempt dispatch — no blocking retry loops.
 */

import { createDeliveryAck, type DeliveryAck } from '../generated/contracts/delivery-ack.js';
import type { LinkHandoffEvent } from '../generated/protocol/edge-to-link.mapper.js';
import {
  createMemoryOffsetCommitStore,
  MemoryOffsetCommitStore,
} from './log-kernel/offset/memory-offset-commit-store.js';
import type { IOffsetCommitStore, OffsetCommit } from './log-kernel/offset/offset-commit.js';
import {
  createLinkPartitionedQueues,
  LinkPartitionedQueues,
} from './link-partition-queues.js';
import { evaluateLinkRetry } from './link-retry.js';
import { routeToCoreSystem, type CoreSystemRoute } from './link-router.js';

export interface CoreSystemDeliverer {
  deliver(event: LinkHandoffEvent, route: CoreSystemRoute): Promise<{ accepted: boolean }>;
}

export interface LinkDeliveryResult {
  readonly delivered: boolean;
  readonly state: 'DELIVERED' | 'RETRYING' | 'FAILED';
  readonly route: CoreSystemRoute;
  readonly deliveredAt: string;
  readonly partition: number | null;
  readonly logOffset: number | null;
  readonly deliveryAck: DeliveryAck | null;
  /** Non-blocking hint for external schedulers — LINK does not sleep on this value. */
  readonly suggestedBackoffMs: number;
}

export class LinkDeliveryService {
  public constructor(
    private readonly deliverer: CoreSystemDeliverer,
    private readonly coreSystemBaseUrl: string,
    private readonly partitionedQueues: LinkPartitionedQueues = createLinkPartitionedQueues(),
    private readonly offsetCommitStore: IOffsetCommitStore = createMemoryOffsetCommitStore(),
    private readonly maxAttempts = 3,
    private readonly backoffMs: readonly number[] = [250, 500, 1000],
  ) {}

  public getPartitionedQueues(): LinkPartitionedQueues {
    return this.partitionedQueues;
  }

  public getOffsetCommitStore(): IOffsetCommitStore {
    return this.offsetCommitStore;
  }

  public enqueue(event: LinkHandoffEvent): string {
    const result = this.partitionedQueues.push(event);
    if (!result.accepted) {
      throw new Error(WIRE_BACKPRESSURE_ERROR);
    }

    return result.queueId;
  }

  /** Performs one delivery attempt; returns RETRYING with suggestedBackoffMs when re-dispatch is needed. */
  public async deliverNext(
    shouldFail?: (attempt: number) => boolean,
  ): Promise<LinkDeliveryResult | null> {
    const pending = this.partitionedQueues.nextPending();
    if (!pending) {
      return null;
    }

    const route = routeToCoreSystem(pending.event, this.coreSystemBaseUrl);
    const attemptNumber = pending.attempts + 1;
    const failed = shouldFail?.(attemptNumber) === true;
    const response = failed ? { accepted: false } : await this.deliverer.deliver(pending.event, route);
    const state = this.partitionedQueues.applyDeliveryResult(
      pending.queueId,
      response.accepted,
      this.maxAttempts,
    );
    const deliveredAt = new Date().toISOString();
    const logOffset = pending.logOffset;
    const partitionId = pending.partition;

    if (state === 'DELIVERED') {
      const deliveryAck = createDeliveryAck({
        partitionId,
        offset: logOffset,
        eventId: pending.event.eventId,
        status: 'ACK',
        timestamp: deliveredAt,
      });
      this.commitOffset({
        partitionId,
        offset: logOffset,
        committedAt: deliveredAt,
        status: 'DELIVERED',
        eventId: pending.event.eventId,
        gatewayId: pending.event.gatewayId,
      });

      return {
        delivered: true,
        state: 'DELIVERED',
        route,
        deliveredAt,
        partition: partitionId,
        logOffset,
        deliveryAck,
        suggestedBackoffMs: 0,
      };
    }

    const retry = evaluateLinkRetry(attemptNumber, this.maxAttempts, this.backoffMs, false);

    if (state === 'FAILED') {
      this.partitionedQueues
        .getPartition(partitionId)
        .dlq.move(pending, pending.event, 'delivery_exhausted');

      const deliveryAck = createDeliveryAck({
        partitionId,
        offset: logOffset,
        eventId: pending.event.eventId,
        status: 'DLQ',
        timestamp: deliveredAt,
        reason: 'delivery_exhausted',
      });
      this.commitOffset({
        partitionId,
        offset: logOffset,
        committedAt: deliveredAt,
        status: 'FAILED',
        eventId: pending.event.eventId,
        gatewayId: pending.event.gatewayId,
        reason: 'delivery_exhausted',
      });

      return {
        delivered: false,
        state: 'FAILED',
        route,
        deliveredAt,
        partition: partitionId,
        logOffset,
        deliveryAck,
        suggestedBackoffMs: 0,
      };
    }

    const deliveryAck = createDeliveryAck({
      partitionId,
      offset: logOffset,
      eventId: pending.event.eventId,
      status: 'RETRY',
      timestamp: deliveredAt,
      reason: 'delivery_retry',
    });
    this.commitOffset({
      partitionId,
      offset: logOffset,
      committedAt: deliveredAt,
      status: 'RETRYING',
      eventId: pending.event.eventId,
      gatewayId: pending.event.gatewayId,
      reason: 'delivery_retry',
    });

    return {
      delivered: false,
      state: 'RETRYING',
      route,
      deliveredAt,
      partition: partitionId,
      logOffset,
      deliveryAck,
      suggestedBackoffMs: retry.backoffMs,
    };
  }

  private commitOffset(record: OffsetCommit): void {
    this.offsetCommitStore.commit(record);
  }
}

const WIRE_BACKPRESSURE_ERROR = 'LINK_BACKPRESSURE_DROP';

export function createLinkDeliveryService(
  deliverer: CoreSystemDeliverer,
  coreSystemBaseUrl: string,
  partitionedQueues?: LinkPartitionedQueues,
  offsetCommitStore?: IOffsetCommitStore,
): LinkDeliveryService {
  return new LinkDeliveryService(deliverer, coreSystemBaseUrl, partitionedQueues, offsetCommitStore);
}

export type { DeliveryAck, IOffsetCommitStore, MemoryOffsetCommitStore };
