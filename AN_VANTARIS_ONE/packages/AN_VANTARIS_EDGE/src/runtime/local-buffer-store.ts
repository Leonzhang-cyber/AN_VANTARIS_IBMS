import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';

import type { DeliveryAuditChain } from './delivery-audit-chain.js';
import type { EdgeEnvelope } from './edge-envelope-types.js';
import type {
  LocalBufferAckResult,
  LocalBufferError,
  LocalBufferEvidenceSnapshot,
  LocalBufferFailResult,
  LocalBufferIngestResult,
  LocalBufferQueryResult,
  LocalBufferRecord,
  LocalBufferRecordStatus,
  LocalBufferStats,
} from './local-buffer-types.js';

interface LocalBufferLedgerEvent {
  readonly eventType: 'ingest' | 'status';
  readonly record: LocalBufferRecord;
  readonly reason?: string;
}

function nowIso(): string {
  return new Date().toISOString();
}

function generateRecordId(envelopeId: string): string {
  return `buf-${envelopeId}-${Date.now()}`;
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function isStatus(value: unknown): value is LocalBufferRecordStatus {
  return value == 'staged' || value == 'pending' || value == 'failed' || value == 'acknowledged' || value == 'quarantined';
}

export class LocalBufferStore {
  private readonly runtimeRoot: string;
  private readonly bufferDir: string;
  private readonly ledgerPathInternal: string;

  public constructor(
    runtimeRoot: string,
    private readonly options: {
      deliveryAuditChain?: DeliveryAuditChain;
    } = {},
  ) {
    this.runtimeRoot = resolve(runtimeRoot);
    this.bufferDir = resolve(this.runtimeRoot, 'buffer');
    this.ledgerPathInternal = resolve(this.bufferDir, 'edge-envelope-buffer.jsonl');
    mkdirSync(this.bufferDir, { recursive: true });
  }

  public ingestEdgeEnvelope(envelope: EdgeEnvelope): LocalBufferIngestResult {
    if (!envelope.header.envelopeId || !envelope.header.connectorId) {
      return {
        ok: false,
        recordId: null,
        status: 'quarantined',
        reason: 'invalid_envelope_header',
      };
    }
    const record: LocalBufferRecord = {
      recordId: generateRecordId(envelope.header.envelopeId),
      envelopeId: envelope.header.envelopeId,
      connectorId: envelope.header.connectorId,
      protocol: envelope.header.protocol,
      createdAt: nowIso(),
      status: 'staged',
      envelope,
      attempts: 0,
      lastError: null,
      updatedAt: nowIso(),
    };
    this.appendLedgerEvent({
      eventType: 'ingest',
      record,
    });
    this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
      this.options.deliveryAuditChain.createDeliveryAuditEvent({
        eventType: 'buffer.ingested',
        actor: 'buffer-store',
        target: {
          recordId: record.recordId,
          envelopeId: record.envelopeId,
          connectorId: record.connectorId,
        },
        details: {
          status: record.status,
          attempts: record.attempts,
        },
      }),
    );
    return {
      ok: true,
      recordId: record.recordId,
      status: record.status,
      reason: null,
    };
  }

  public listBufferRecords(status?: LocalBufferRecordStatus): LocalBufferQueryResult {
    const all = this.rebuildRecords();
    const records = status ? all.filter((item) => item.status == status) : all;
    return {
      records,
      total: records.length,
      generatedAt: nowIso(),
    };
  }

  public getBufferRecord(recordId: string): LocalBufferRecord | null {
    return this.rebuildRecords().find((item) => item.recordId == recordId) ?? null;
  }

  public listBufferRecordsByStatuses(statuses: readonly LocalBufferRecordStatus[]): LocalBufferQueryResult {
    const set = new Set(statuses);
    const records = this.rebuildRecords().filter((item) => set.has(item.status));
    return {
      records,
      total: records.length,
      generatedAt: nowIso(),
    };
  }

  public markPending(recordId: string): LocalBufferAckResult {
    return this.updateStatus(recordId, 'pending');
  }

  public markFailed(recordId: string, reason: string): LocalBufferFailResult {
    const result = this.updateStatus(recordId, 'failed', reason);
    return {
      ok: result.ok,
      recordId: result.recordId,
      status: result.status,
      reason,
      updatedAt: result.updatedAt,
    };
  }

  public markAcknowledged(recordId: string): LocalBufferAckResult {
    return this.updateStatus(recordId, 'acknowledged');
  }

  public quarantineRecord(recordId: string, reason: string): LocalBufferFailResult {
    const result = this.updateStatus(recordId, 'quarantined', reason);
    return {
      ok: result.ok,
      recordId: result.recordId,
      status: result.status,
      reason,
      updatedAt: result.updatedAt,
    };
  }

  public getLocalBufferStats(): LocalBufferStats {
    const records = this.rebuildRecords();
    const count = (status: LocalBufferRecordStatus) => records.filter((item) => item.status == status).length;
    return {
      total: records.length,
      staged: count('staged'),
      pending: count('pending'),
      failed: count('failed'),
      acknowledged: count('acknowledged'),
      quarantined: count('quarantined'),
      generatedAt: nowIso(),
    };
  }

  public exportLocalBufferEvidence(path: string): LocalBufferEvidenceSnapshot {
    const records = this.rebuildRecords();
    const errors: LocalBufferError[] = [];
    const snapshot: LocalBufferEvidenceSnapshot = {
      generatedAt: nowIso(),
      ledgerPath: this.ledgerPathInternal,
      totalRecords: records.length,
      stats: this.getLocalBufferStats(),
      records,
      errors,
    };
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, JSON.stringify(snapshot, null, 2) + '\n', 'utf8');
    return snapshot;
  }

  public ledgerPath(): string {
    return this.ledgerPathInternal;
  }

  private updateStatus(recordId: string, nextStatus: LocalBufferRecordStatus, reason?: string): LocalBufferAckResult {
    const current = this.getBufferRecord(recordId);
    if (!current) {
      return {
        ok: false,
        recordId,
        status: nextStatus,
        updatedAt: nowIso(),
      };
    }
    const updated: LocalBufferRecord = {
      ...current,
      status: nextStatus,
      attempts: nextStatus == 'pending' || nextStatus == 'failed' ? current.attempts + 1 : current.attempts,
      lastError: reason ?? (nextStatus == 'failed' ? 'delivery_failed' : null),
      updatedAt: nowIso(),
    };
    this.appendLedgerEvent({
      eventType: 'status',
      record: updated,
      reason,
    });
    const eventType =
      nextStatus == 'pending'
        ? 'buffer.pending'
        : nextStatus == 'failed'
          ? 'buffer.failed'
          : nextStatus == 'acknowledged'
            ? 'buffer.acknowledged'
            : 'buffer.quarantined';
    this.options.deliveryAuditChain?.appendDeliveryAuditEvent(
      this.options.deliveryAuditChain.createDeliveryAuditEvent({
        eventType,
        actor: 'buffer-store',
        target: {
          recordId: updated.recordId,
          envelopeId: updated.envelopeId,
          connectorId: updated.connectorId,
        },
        details: {
          reason: reason ?? null,
          attempts: updated.attempts,
          status: updated.status,
        },
      }),
    );
    return {
      ok: true,
      recordId,
      status: nextStatus,
      updatedAt: updated.updatedAt,
    };
  }

  private appendLedgerEvent(event: LocalBufferLedgerEvent): void {
    appendFileSync(this.ledgerPathInternal, JSON.stringify(event) + '\n', 'utf8');
  }

  private rebuildRecords(): LocalBufferRecord[] {
    if (!existsSync(this.ledgerPathInternal)) return [];
    const lines = readFileSync(this.ledgerPathInternal, 'utf8')
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const records = new Map<string, LocalBufferRecord>();
    for (const line of lines) {
      let parsed: unknown;
      try {
        parsed = JSON.parse(line);
      } catch {
        continue;
      }
      if (!isObject(parsed) || !isObject(parsed.record)) continue;
      const raw = parsed.record;
      if (typeof raw.recordId != 'string') continue;
      if (!isStatus(raw.status)) continue;
      records.set(raw.recordId, raw as unknown as LocalBufferRecord);
    }
    return Array.from(records.values()).sort((a, b) => a.createdAt.localeCompare(b.createdAt));
  }
}
