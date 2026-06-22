import type { LocalBufferRecord, LocalBufferRecordStatus } from './local-buffer-types.js';

export type LocalDeliveryBatchStatus = 'preview' | 'ready' | 'deferred' | 'exhausted' | 'skipped';

export interface LocalRetryPolicy {
  readonly maxAttempts: number;
  readonly baseDelayMs: number;
  readonly maxDelayMs: number;
  readonly batchSize: number;
}

export interface LocalRetryDecision {
  readonly shouldRetry: boolean;
  readonly decision: 'ready' | 'deferred' | 'exhausted' | 'skipped';
  readonly delayMs: number;
  readonly nextEligibleAt: string;
  readonly reason: string;
}

export interface LocalDeliveryBatchItem {
  readonly recordId: string;
  readonly envelopeId: string;
  readonly connectorId: string;
  readonly protocol: string;
  readonly status: LocalBufferRecordStatus;
  readonly attempts: number;
  readonly retryDecision: LocalRetryDecision;
  batchStatus: LocalDeliveryBatchStatus;
}

export interface LocalDeliveryBatch {
  readonly batchId: string;
  readonly createdAt: string;
  readonly policy: LocalRetryPolicy;
  readonly items: readonly LocalDeliveryBatchItem[];
  readonly statusSummary: {
    readonly preview: number;
    readonly ready: number;
    readonly deferred: number;
    readonly exhausted: number;
    readonly skipped: number;
  };
}

export interface LocalDeliveryCursor {
  readonly generatedAt: string;
  readonly batchId: string;
  readonly nextCursorIndex: number;
  readonly lastProcessedRecordId: string | null;
  readonly processedCount: number;
}

export interface LocalDeliveryAttempt {
  readonly recordId: string;
  readonly previousStatus: LocalBufferRecordStatus;
  readonly nextStatus: LocalBufferRecordStatus;
  readonly at: string;
  readonly reason: string;
}

export interface LocalDeliveryPreviewResult {
  readonly generatedAt: string;
  readonly sourceRecordCount: number;
  readonly batch: LocalDeliveryBatch;
  readonly cursor: LocalDeliveryCursor;
}

export interface LocalDeliveryOrchestratorStats {
  readonly totalRecords: number;
  readonly selectedRecords: number;
  readonly readyCount: number;
  readonly deferredCount: number;
  readonly exhaustedCount: number;
  readonly skippedCount: number;
  readonly generatedAt: string;
}

export interface LocalDeliveryOrchestratorEvidence {
  readonly generatedAt: string;
  readonly policy: LocalRetryPolicy;
  readonly sourceRecords: readonly LocalBufferRecord[];
  readonly preview: LocalDeliveryPreviewResult;
  readonly stats: LocalDeliveryOrchestratorStats;
  readonly attempts: readonly LocalDeliveryAttempt[];
  readonly cursor: LocalDeliveryCursor;
}
