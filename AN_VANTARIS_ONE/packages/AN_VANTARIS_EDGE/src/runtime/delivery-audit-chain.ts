import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';

import type {
  DeliveryAuditActor,
  DeliveryAuditChainRecord,
  DeliveryAuditError,
  DeliveryAuditEvent,
  DeliveryAuditEventType,
  DeliveryAuditEvidenceExport,
  DeliveryAuditIntegritySummary,
  DeliveryAuditTarget,
} from './delivery-audit-types.js';

function nowIso(): string {
  return new Date().toISOString();
}

function hashRecord(input: { previousHash: string; sequence: number; event: DeliveryAuditEvent }): string {
  const hash = createHash('sha256');
  hash.update(JSON.stringify(input));
  return hash.digest('hex');
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

export class DeliveryAuditChain {
  private readonly runtimeRoot: string;
  private readonly auditDir: string;
  private readonly ledgerPathInternal: string;
  private tailInitialized = false;
  private lastSequence = 0;
  private lastHash = 'GENESIS';

  public constructor(runtimeRoot: string) {
    this.runtimeRoot = resolve(runtimeRoot);
    this.auditDir = resolve(this.runtimeRoot, 'audit');
    this.ledgerPathInternal = resolve(this.auditDir, 'edge-delivery-audit-ledger.jsonl');
    mkdirSync(this.auditDir, { recursive: true });
  }

  public createDeliveryAuditEvent(input: {
    eventType: DeliveryAuditEventType;
    actor: DeliveryAuditActor;
    target: Partial<DeliveryAuditTarget>;
    details?: Record<string, unknown>;
  }): DeliveryAuditEvent {
    return {
      eventId: `audit-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`,
      eventType: input.eventType,
      actor: input.actor,
      target: {
        recordId: input.target.recordId ?? null,
        envelopeId: input.target.envelopeId ?? null,
        connectorId: input.target.connectorId ?? null,
        batchId: input.target.batchId ?? null,
      },
      at: nowIso(),
      details: input.details ?? {},
    };
  }

  public appendDeliveryAuditEvent(event: DeliveryAuditEvent): DeliveryAuditChainRecord {
    this.ensureTailState();
    const sequence = this.lastSequence + 1;
    const previousHash = this.lastHash;
    const currentHash = hashRecord({ previousHash, sequence, event });
    const record: DeliveryAuditChainRecord = {
      sequence,
      previousHash,
      currentHash,
      event,
    };
    appendFileSync(this.ledgerPathInternal, JSON.stringify(record) + '\n', 'utf8');
    this.lastSequence = sequence;
    this.lastHash = currentHash;
    return record;
  }

  public listDeliveryAuditEvents(): DeliveryAuditChainRecord[] {
    if (!existsSync(this.ledgerPathInternal)) return [];
    const lines = readFileSync(this.ledgerPathInternal, 'utf8')
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
    const records: DeliveryAuditChainRecord[] = [];
    for (const line of lines) {
      let parsed: unknown;
      try {
        parsed = JSON.parse(line);
      } catch {
        continue;
      }
      if (!isObject(parsed) || !isObject(parsed.event)) continue;
      if (typeof parsed.sequence != 'number') continue;
      if (typeof parsed.previousHash != 'string' || typeof parsed.currentHash != 'string') continue;
      records.push(parsed as unknown as DeliveryAuditChainRecord);
    }
    return records.sort((a, b) => a.sequence - b.sequence);
  }

  public buildDeliveryAuditChain(): DeliveryAuditChainRecord[] {
    return this.listDeliveryAuditEvents();
  }

  public validateDeliveryAuditChain(): {
    readonly valid: boolean;
    readonly errors: readonly DeliveryAuditError[];
  } {
    const records = this.listDeliveryAuditEvents();
    const errors: DeliveryAuditError[] = [];
    let expectedPreviousHash = 'GENESIS';
    for (const record of records) {
      if (record.previousHash != expectedPreviousHash) {
        errors.push({
          code: 'invalid_previous_hash',
          message: `sequence ${record.sequence} previousHash mismatch`,
          sequence: record.sequence,
        });
      }
      const expectedCurrentHash = hashRecord({
        previousHash: record.previousHash,
        sequence: record.sequence,
        event: record.event,
      });
      if (record.currentHash != expectedCurrentHash) {
        errors.push({
          code: 'invalid_current_hash',
          message: `sequence ${record.sequence} currentHash mismatch`,
          sequence: record.sequence,
        });
      }
      expectedPreviousHash = record.currentHash;
    }
    return {
      valid: errors.length == 0,
      errors,
    };
  }

  public getDeliveryAuditIntegritySummary(): DeliveryAuditIntegritySummary {
    const records = this.listDeliveryAuditEvents();
    const validation = this.validateDeliveryAuditChain();
    return {
      valid: validation.valid,
      recordCount: records.length,
      firstHash: records[0]?.currentHash ?? null,
      lastHash: records.at(-1)?.currentHash ?? null,
      brokenAtSequence: validation.errors[0]?.sequence ?? null,
      generatedAt: nowIso(),
    };
  }

  public exportDeliveryAuditEvidence(path: string): DeliveryAuditEvidenceExport {
    const payload: DeliveryAuditEvidenceExport = {
      generatedAt: nowIso(),
      ledgerPath: this.ledgerPathInternal,
      integrity: this.getDeliveryAuditIntegritySummary(),
      records: this.listDeliveryAuditEvents(),
    };
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
    return payload;
  }

  public ledgerPath(): string {
    return this.ledgerPathInternal;
  }

  private ensureTailState(): void {
    if (this.tailInitialized) return;
    const records = this.listDeliveryAuditEvents();
    const last = records.at(-1);
    this.lastSequence = last?.sequence ?? 0;
    this.lastHash = last?.currentHash ?? 'GENESIS';
    this.tailInitialized = true;
  }
}
