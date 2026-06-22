import type { EdgeEnvelope } from './edge-envelope-types.js';

export type LocalBufferRecordStatus = 'staged' | 'pending' | 'failed' | 'acknowledged' | 'quarantined';

export interface LocalBufferRecord {
  readonly recordId: string;
  readonly envelopeId: string;
  readonly connectorId: string;
  readonly protocol: string;
  readonly createdAt: string;
  status: LocalBufferRecordStatus;
  readonly envelope: EdgeEnvelope;
  attempts: number;
  lastError: string | null;
  updatedAt: string;
}

export interface LocalBufferIngestResult {
  readonly ok: boolean;
  readonly recordId: string | null;
  readonly status: LocalBufferRecordStatus;
  readonly reason: string | null;
}

export interface LocalBufferQueryResult {
  readonly records: readonly LocalBufferRecord[];
  readonly total: number;
  readonly generatedAt: string;
}

export interface LocalBufferAckResult {
  readonly ok: boolean;
  readonly recordId: string;
  readonly status: LocalBufferRecordStatus;
  readonly updatedAt: string;
}

export interface LocalBufferFailResult {
  readonly ok: boolean;
  readonly recordId: string;
  readonly status: LocalBufferRecordStatus;
  readonly reason: string;
  readonly updatedAt: string;
}

export interface LocalBufferStats {
  readonly total: number;
  readonly staged: number;
  readonly pending: number;
  readonly failed: number;
  readonly acknowledged: number;
  readonly quarantined: number;
  readonly generatedAt: string;
}

export interface LocalBufferError {
  readonly code: string;
  readonly message: string;
  readonly recordId: string | null;
}

export interface LocalBufferEvidenceSnapshot {
  readonly generatedAt: string;
  readonly ledgerPath: string;
  readonly totalRecords: number;
  readonly stats: LocalBufferStats;
  readonly records: readonly LocalBufferRecord[];
  readonly errors: readonly LocalBufferError[];
}
