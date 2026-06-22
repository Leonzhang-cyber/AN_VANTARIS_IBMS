import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

import type { DeliveryAuditChain } from './delivery-audit-chain.js';
import type { LocalBufferStore } from './local-buffer-store.js';
import type { LocalBufferRecord, LocalBufferRecordStatus } from './local-buffer-types.js';
import type {
  LocalDeliveryAttempt,
  LocalDeliveryBatch,
  LocalDeliveryBatchItem,
  LocalDeliveryBatchStatus,
  LocalDeliveryCursor,
  LocalDeliveryOrchestratorEvidence,
  LocalDeliveryOrchestratorStats,
  LocalDeliveryPreviewResult,
  LocalRetryDecision,
  LocalRetryPolicy,
} from './delivery-orchestrator-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function clampDelay(delayMs: number, maxDelayMs: number): number {
  return Math.min(delayMs, maxDelayMs);
}

function exponentialBackoff(baseDelayMs: number, attempts: number, maxDelayMs: number): number {
  const raw = baseDelayMs * 2 ** Math.max(0, attempts - 1);
  return clampDelay(raw, maxDelayMs);
}

function buildBatchId(): string {
  return `delivery-batch-${Date.now()}`;
}

function summarizeBatch(items: readonly LocalDeliveryBatchItem[]): LocalDeliveryBatch['statusSummary'] {
  const count = (status: LocalDeliveryBatchStatus) => items.filter((item) => item.batchStatus == status).length;
  return {
    preview: count('preview'),
    ready: count('ready'),
    deferred: count('deferred'),
    exhausted: count('exhausted'),
    skipped: count('skipped'),
  };
}

export class LocalDeliveryOrchestrator {
  private lastCursor: LocalDeliveryCursor | null = null;
  private readonly attempts: LocalDeliveryAttempt[] = [];

  public constructor(
    private readonly options: {
      deliveryAuditChain?: DeliveryAuditChain;
    } = {},
  ) {}

  public createDeliveryBatchPreview(
    records: readonly LocalBufferRecord[],
    policy: LocalRetryPolicy,
  ): LocalDeliveryPreviewResult {
    const eligible = records
      .filter((record) => record.status == 'staged' || record.status == 'pending' || record.status == 'failed')
      .slice(0, policy.batchSize);

    const items: LocalDeliveryBatchItem[] = eligible.map((record) => {
      const retryDecision = this.evaluateRetryPolicy(record, policy);
      this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
        this.options.deliveryAuditChain.createDeliveryAuditEvent({
          eventType: 'delivery.retry.evaluated',
          actor: 'delivery-orchestrator',
          target: {
            recordId: record.recordId,
            envelopeId: record.envelopeId,
            connectorId: record.connectorId,
            batchId: null,
          },
          details: {
            decision: retryDecision.decision,
            delayMs: retryDecision.delayMs,
            reason: retryDecision.reason,
            attempts: record.attempts,
          },
        }),
      );
      const batchStatus = retryDecision.decision == 'ready' ? 'ready' : retryDecision.decision;
      return {
        recordId: record.recordId,
        envelopeId: record.envelopeId,
        connectorId: record.connectorId,
        protocol: record.protocol,
        status: record.status,
        attempts: record.attempts,
        retryDecision,
        batchStatus,
      };
    });

    const batch: LocalDeliveryBatch = {
      batchId: buildBatchId(),
      createdAt: nowIso(),
      policy,
      items,
      statusSummary: summarizeBatch(items),
    };
    const cursor = this.updateDeliveryCursor(batch, this.lastCursor);
    this.lastCursor = cursor;
    this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
      this.options.deliveryAuditChain.createDeliveryAuditEvent({
        eventType: 'delivery.preview.created',
        actor: 'delivery-orchestrator',
        target: {
          batchId: batch.batchId,
          recordId: batch.items[0]?.recordId ?? null,
          envelopeId: batch.items[0]?.envelopeId ?? null,
          connectorId: batch.items[0]?.connectorId ?? null,
        },
        details: {
          selectedRecords: batch.items.length,
          policy,
        },
      }),
    );
    return {
      generatedAt: nowIso(),
      sourceRecordCount: records.length,
      batch,
      cursor,
    };
  }

  public evaluateRetryPolicy(record: LocalBufferRecord, policy: LocalRetryPolicy): LocalRetryDecision {
    const now = Date.now();
    if (record.status == 'acknowledged' || record.status == 'quarantined') {
      return {
        shouldRetry: false,
        decision: 'skipped',
        delayMs: 0,
        nextEligibleAt: new Date(now).toISOString(),
        reason: `status_not_retryable:${record.status}`,
      };
    }
    if (record.attempts >= policy.maxAttempts) {
      return {
        shouldRetry: false,
        decision: 'exhausted',
        delayMs: 0,
        nextEligibleAt: new Date(now).toISOString(),
        reason: 'max_attempts_exhausted',
      };
    }
    const delayMs = exponentialBackoff(policy.baseDelayMs, Math.max(record.attempts, 1), policy.maxDelayMs);
    if (record.status == 'staged') {
      return {
        shouldRetry: true,
        decision: 'ready',
        delayMs: 0,
        nextEligibleAt: new Date(now).toISOString(),
        reason: 'fresh_staged_record',
      };
    }
    if (record.status == 'pending') {
      return {
        shouldRetry: true,
        decision: 'deferred',
        delayMs,
        nextEligibleAt: new Date(now + delayMs).toISOString(),
        reason: 'pending_backoff',
      };
    }
    return {
      shouldRetry: true,
      decision: 'deferred',
      delayMs,
      nextEligibleAt: new Date(now + delayMs).toISOString(),
      reason: 'failed_backoff',
    };
  }

  public updateDeliveryCursor(batch: LocalDeliveryBatch, previous: LocalDeliveryCursor | null): LocalDeliveryCursor {
    const processedCount = (previous?.processedCount ?? 0) + batch.items.length;
    const lastRecord = batch.items.at(-1);
    const cursor = {
      generatedAt: nowIso(),
      batchId: batch.batchId,
      nextCursorIndex: processedCount,
      lastProcessedRecordId: lastRecord?.recordId ?? previous?.lastProcessedRecordId ?? null,
      processedCount,
    } as const;
    this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
      this.options.deliveryAuditChain.createDeliveryAuditEvent({
        eventType: 'delivery.cursor.updated',
        actor: 'delivery-orchestrator',
        target: {
          batchId: batch.batchId,
          recordId: cursor.lastProcessedRecordId,
          envelopeId: lastRecord?.envelopeId ?? null,
          connectorId: lastRecord?.connectorId ?? null,
        },
        details: {
          nextCursorIndex: cursor.nextCursorIndex,
          processedCount: cursor.processedCount,
        },
      }),
    );
    return cursor;
  }

  public markBatchItemsPendingDryRun(store: LocalBufferStore, batch: LocalDeliveryBatch): readonly LocalDeliveryAttempt[] {
    return this.transitionBatchItems(store, batch, 'pending', 'delivery_pending_dry_run');
  }

  public markBatchItemsFailedDryRun(store: LocalBufferStore, batch: LocalDeliveryBatch): readonly LocalDeliveryAttempt[] {
    return this.transitionBatchItems(store, batch, 'failed', 'delivery_failed_dry_run');
  }

  public markBatchItemsAcknowledgedDryRun(
    store: LocalBufferStore,
    batch: LocalDeliveryBatch,
  ): readonly LocalDeliveryAttempt[] {
    return this.transitionBatchItems(store, batch, 'acknowledged', 'delivery_acknowledged_dry_run');
  }

  public getDeliveryOrchestratorStats(preview: LocalDeliveryPreviewResult): LocalDeliveryOrchestratorStats {
    const summary = preview.batch.statusSummary;
    return {
      totalRecords: preview.sourceRecordCount,
      selectedRecords: preview.batch.items.length,
      readyCount: summary.ready,
      deferredCount: summary.deferred,
      exhaustedCount: summary.exhausted,
      skippedCount: summary.skipped,
      generatedAt: nowIso(),
    };
  }

  public exportDeliveryOrchestratorEvidence(path: string, payload: LocalDeliveryOrchestratorEvidence): void {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
  }

  private transitionBatchItems(
    store: LocalBufferStore,
    batch: LocalDeliveryBatch,
    nextStatus: LocalBufferRecordStatus,
    reason: string,
  ): readonly LocalDeliveryAttempt[] {
    const attempts: LocalDeliveryAttempt[] = [];
    const batchEventType =
      nextStatus == 'pending'
        ? 'delivery.batch.pending'
        : nextStatus == 'failed'
          ? 'delivery.batch.failed'
          : 'delivery.batch.acknowledged';
    for (const item of batch.items) {
      const current = store.getBufferRecord(item.recordId);
      if (!current) continue;
      if (nextStatus == 'pending') {
        store.markPending(item.recordId);
      } else if (nextStatus == 'failed') {
        store.markFailed(item.recordId, reason);
      } else if (nextStatus == 'acknowledged') {
        store.markAcknowledged(item.recordId);
      }
      const attempt: LocalDeliveryAttempt = {
        recordId: item.recordId,
        previousStatus: current.status,
        nextStatus,
        at: nowIso(),
        reason,
      };
      this.attempts.push(attempt);
      attempts.push(attempt);
      this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
        this.options.deliveryAuditChain.createDeliveryAuditEvent({
          eventType: batchEventType,
          actor: 'delivery-orchestrator',
          target: {
            recordId: item.recordId,
            envelopeId: item.envelopeId,
            connectorId: item.connectorId,
            batchId: batch.batchId,
          },
          details: {
            previousStatus: current.status,
            nextStatus,
            reason,
          },
        }),
      );
    }
    return attempts;
  }
}
