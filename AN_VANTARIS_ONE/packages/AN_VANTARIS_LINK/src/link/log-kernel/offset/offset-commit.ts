/**
 * Offset commit contract — transport delivery progress only (no business logic).
 */

export type OffsetCommitStatus = 'DELIVERED' | 'FAILED' | 'RETRYING';

export interface OffsetCommit {
  readonly partitionId: number;
  readonly offset: number;
  readonly committedAt: string;
  readonly status: OffsetCommitStatus;
  readonly eventId?: string;
  readonly gatewayId?: string;
  readonly nodeId?: string;
  readonly reason?: string;
}

export interface IOffsetCommitStore {
  commit(record: OffsetCommit): OffsetCommit;

  getCommittedOffset(partitionId: number): number;

  getCommit(partitionId: number, offset: number): OffsetCommit | undefined;

  listCommits(partitionId: number): readonly OffsetCommit[];
}
