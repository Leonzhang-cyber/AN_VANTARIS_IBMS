/**
 * LINK recovery — rebuild execution buffers from durable partition logs.
 */

import type { WireTransportEvent } from '../../generated/contracts/wire-event-v1.js';
import type { IOffsetCommitStore } from '../log-kernel/offset/offset-commit.js';
import type { ILogStorage, LogRecord } from '../log-kernel/storage/ilog-storage.js';
import { LinkPartitionedQueues } from '../link-partition-queues.js';

export interface LinkReplayResult {
  readonly partitionId: number;
  readonly restoredCount: number;
  readonly fromOffset: number;
}

function readEnqueueFrom(storage: ILogStorage, partitionId: number, offset: number): readonly LogRecord[] {
  return storage.readFrom(partitionId, offset).filter((record) => record.kind === 'enqueue');
}

export class LinkReplayEngine {
  public constructor(
    private readonly logStorage: ILogStorage,
    private readonly partitionedQueues: LinkPartitionedQueues,
    private readonly offsetCommitStore?: IOffsetCommitStore,
  ) {}

  public replayPartition(partitionId: number): LinkReplayResult {
    return this.replayFromOffset(partitionId, -1);
  }

  public replayFromOffset(partitionId: number, offset: number): LinkReplayResult {
    const entries = readEnqueueFrom(this.logStorage, partitionId, offset);
    const restoredCount = this.partitionedQueues.restoreEnqueueEntries(partitionId, entries);
    return {
      partitionId,
      restoredCount,
      fromOffset: offset,
    };
  }

  public replayUncommitted(partitionId: number): LinkReplayResult {
    const committedOffset = this.offsetCommitStore?.getCommittedOffset(partitionId) ?? -1;
    return this.replayFromOffset(partitionId, committedOffset);
  }

  public recoverAllPartitions(): readonly LinkReplayResult[] {
    const results: LinkReplayResult[] = [];
    const partitionCount = this.partitionedQueues.getPartitionCount();

    for (let partitionId = 0; partitionId < partitionCount; partitionId += 1) {
      this.partitionedQueues.clearExecutionBuffer(partitionId);
      results.push(this.replayPartition(partitionId));
    }

    return results;
  }

  public recoverUncommittedPartitions(): readonly LinkReplayResult[] {
    const results: LinkReplayResult[] = [];
    const partitionCount = this.partitionedQueues.getPartitionCount();

    for (let partitionId = 0; partitionId < partitionCount; partitionId += 1) {
      this.partitionedQueues.clearExecutionBuffer(partitionId);
      results.push(this.replayUncommitted(partitionId));
    }

    return results;
  }
}

export function createLinkReplayEngine(
  logStorage: ILogStorage,
  partitionedQueues: LinkPartitionedQueues,
  offsetCommitStore?: IOffsetCommitStore,
): LinkReplayEngine {
  return new LinkReplayEngine(logStorage, partitionedQueues, offsetCommitStore);
}

export function recoverPartitionedQueuesOnStartup(
  logStorage: ILogStorage,
  partitionedQueues: LinkPartitionedQueues,
  offsetCommitStore?: IOffsetCommitStore,
): readonly LinkReplayResult[] {
  return createLinkReplayEngine(logStorage, partitionedQueues, offsetCommitStore).recoverAllPartitions();
}

export function recoverUncommittedQueuesOnStartup(
  logStorage: ILogStorage,
  partitionedQueues: LinkPartitionedQueues,
  offsetCommitStore: IOffsetCommitStore,
): readonly LinkReplayResult[] {
  return createLinkReplayEngine(logStorage, partitionedQueues, offsetCommitStore).recoverUncommittedPartitions();
}

export type { LogRecord, WireTransportEvent };

/** @deprecated Use LogRecord */
export type PartitionLogEntry = LogRecord;
