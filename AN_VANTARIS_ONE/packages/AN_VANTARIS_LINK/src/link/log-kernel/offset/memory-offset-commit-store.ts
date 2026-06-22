/**
 * In-memory offset commit store — per-partition delivery progress tracking.
 */

import type { IOffsetCommitStore, OffsetCommit } from './offset-commit.js';

export class MemoryOffsetCommitStore implements IOffsetCommitStore {
  private readonly commitsByKey = new Map<string, OffsetCommit>();
  private readonly commitsByPartition = new Map<number, OffsetCommit[]>();
  private readonly deliveredHighWaterMark = new Map<number, number>();

  public commit(record: OffsetCommit): OffsetCommit {
    const key = commitKey(record.partitionId, record.offset);
    const existing = this.commitsByKey.get(key);
    if (existing !== undefined) {
      return existing;
    }

    this.commitsByKey.set(key, record);
    const partitionCommits = this.commitsByPartition.get(record.partitionId) ?? [];
    partitionCommits.push(record);
    this.commitsByPartition.set(record.partitionId, partitionCommits);

    if (record.status === 'DELIVERED') {
      const current = this.deliveredHighWaterMark.get(record.partitionId) ?? -1;
      if (record.offset > current) {
        this.deliveredHighWaterMark.set(record.partitionId, record.offset);
      }
    }

    return record;
  }

  public getCommittedOffset(partitionId: number): number {
    return this.deliveredHighWaterMark.get(partitionId) ?? -1;
  }

  public getCommit(partitionId: number, offset: number): OffsetCommit | undefined {
    return this.commitsByKey.get(commitKey(partitionId, offset));
  }

  public listCommits(partitionId: number): readonly OffsetCommit[] {
    return [...(this.commitsByPartition.get(partitionId) ?? [])];
  }
}

function commitKey(partitionId: number, offset: number): string {
  return `${partitionId}:${offset}`;
}

export function createMemoryOffsetCommitStore(): MemoryOffsetCommitStore {
  return new MemoryOffsetCommitStore();
}
