import { appendFileSync, existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

import type { BufferState, EdgeLocalEnvelope } from './types.js';

interface MessageRecord {
  readonly recordType: 'message';
  readonly messageId: string;
  readonly insertedAt: string;
  readonly ttlSeconds: number;
  readonly priority: number;
  readonly envelope: EdgeLocalEnvelope;
}

interface StateRecord {
  readonly recordType: 'state';
  readonly messageId: string;
  readonly state: BufferState;
  readonly reason?: string;
  readonly updatedAt: string;
}

type BufferRecord = MessageRecord | StateRecord;

export interface RecoveryWarning {
  readonly lineNumber: number;
  readonly code: 'invalid_json' | 'invalid_record' | 'state_without_message' | 'empty_line';
  readonly detail: string;
}

export interface DurableLocalBufferOptions {
  readonly maxRecordBytes?: number;
}

function nowIso(): string {
  return new Date().toISOString();
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value == 'object' && value != null;
}

function isBufferState(value: unknown): value is BufferState {
  return value == 'pending' || value == 'accepted_local' || value == 'failed' || value == 'expired' || value == 'purged';
}

function appendJsonl(path: string, value: BufferRecord): void {
  appendFileSync(path, `${JSON.stringify(value)}\n`, 'utf8');
}

export class DurableLocalBuffer {
  private readonly outboxDir: string;
  private readonly dlqDir: string;
  private readonly quarantineDir: string;
  private readonly ledgerFile: string;
  private readonly maxRecordBytes: number;

  public constructor(private readonly runtimeBaseDir: string, options: DurableLocalBufferOptions = {}) {
    this.outboxDir = join(runtimeBaseDir, 'outbox');
    this.dlqDir = join(runtimeBaseDir, 'dlq');
    this.quarantineDir = join(runtimeBaseDir, 'quarantine');
    this.ledgerFile = join(this.outboxDir, 'messages.jsonl');
    this.maxRecordBytes = options.maxRecordBytes ?? 64 * 1024;
    this.ensureDirs();
  }

  public append(message: EdgeLocalEnvelope, ttlSeconds = 3600, priority = 5): string | null {
    const record: MessageRecord = {
      recordType: 'message',
      messageId: message.messageId,
      insertedAt: nowIso(),
      ttlSeconds,
      priority,
      envelope: message,
    };
    const encoded = JSON.stringify(record);
    if (Buffer.byteLength(encoded, 'utf8') > this.maxRecordBytes) {
      this.quarantineInvalidSample('max_record_guard', {
        messageId: message.messageId,
        bytes: Buffer.byteLength(encoded, 'utf8'),
        maxRecordBytes: this.maxRecordBytes,
      });
      return null;
    }
    appendJsonl(this.ledgerFile, record);
    this.appendState(message.messageId, 'pending');
    return message.messageId;
  }

  public listPending(): readonly MessageRecord[] {
    return this.reconstruct().filter((item) => item.currentState == 'pending').map((item) => item.message);
  }

  public replayList(): readonly MessageRecord[] {
    return this.reconstruct().filter((item) => item.currentState != 'purged').map((item) => item.message);
  }

  public markAcceptedLocal(messageId: string): void {
    this.appendState(messageId, 'accepted_local');
  }

  public markFailed(messageId: string, reason: string): void {
    this.appendState(messageId, 'failed', reason);
  }

  public purgeExpired(referenceNow = new Date()): number {
    let purged = 0;
    for (const item of this.reconstruct()) {
      const expiresAt = new Date(item.message.insertedAt);
      expiresAt.setSeconds(expiresAt.getSeconds() + item.message.ttlSeconds);
      if (expiresAt < referenceNow && item.currentState != 'purged') {
        this.appendState(item.message.messageId, 'expired');
        this.appendState(item.message.messageId, 'purged');
        purged += 1;
      }
    }
    return purged;
  }

  public summary(): {
    readonly pending: number;
    readonly accepted_local: number;
    readonly failed: number;
    readonly expired: number;
    readonly purged: number;
    readonly outboxCount: number;
    readonly dlqCount: number;
    readonly quarantineCount: number;
  } {
    const summary = this.countByStatus();
    return {
      ...summary,
      outboxCount: this.recoverFromLedger().records.length,
      dlqCount: this.countDir(this.dlqDir),
      quarantineCount: this.countDir(this.quarantineDir),
    };
  }

  public restartRecoveryEvidence(): {
    readonly recoveredMessageCount: number;
    readonly pendingCount: number;
    readonly recoveryWarnings: readonly RecoveryWarning[];
  } {
    const recovered = this.recoverFromLedger();
    return {
      recoveredMessageCount: recovered.records.length,
      pendingCount: recovered.records.filter((item) => item.currentState == 'pending').length,
      recoveryWarnings: recovered.warnings,
    };
  }

  public countByStatus(): Record<BufferState, number> {
    const summary: Record<BufferState, number> = {
      pending: 0,
      accepted_local: 0,
      failed: 0,
      expired: 0,
      purged: 0,
    };
    for (const item of this.recoverFromLedger().records) {
      summary[item.currentState] += 1;
    }
    return summary;
  }

  public recoverFromLedger(): {
    readonly records: Array<{ message: MessageRecord; currentState: BufferState }>;
    readonly warnings: readonly RecoveryWarning[];
  } {
    const warnings: RecoveryWarning[] = [];
    const records = this.readLedger(warnings);
    return {
      records: this.reconstructFromRecords(records, warnings),
      warnings,
    };
  }

  public exportLedgerSnapshot(path?: string): {
    readonly generatedAt: string;
    readonly ledgerPath: string;
    readonly messageCount: number;
    readonly stateCount: number;
    readonly countByStatus: Record<BufferState, number>;
    readonly warnings: readonly RecoveryWarning[];
  } {
    const warnings: RecoveryWarning[] = [];
    const records = this.readLedger(warnings);
    const messageCount = records.filter((item) => item.recordType == 'message').length;
    const stateCount = records.filter((item) => item.recordType == 'state').length;
    const snapshot = {
      generatedAt: nowIso(),
      ledgerPath: this.ledgerFile,
      messageCount,
      stateCount,
      countByStatus: this.countByStatus(),
      warnings,
    } as const;
    if (path) writeFileSync(path, JSON.stringify(snapshot, null, 2) + '\n', 'utf8');
    return snapshot;
  }

  public validateLedgerLine(line: string, lineNumber: number): { readonly record?: BufferRecord; readonly warning?: RecoveryWarning } {
    const trimmed = line.trim();
    if (!trimmed) {
      return {
        warning: {
          lineNumber,
          code: 'empty_line',
          detail: 'empty ledger line ignored',
        },
      };
    }
    let parsed: unknown;
    try {
      parsed = JSON.parse(trimmed);
    } catch (error) {
      return {
        warning: {
          lineNumber,
          code: 'invalid_json',
          detail: error instanceof Error ? error.message : 'invalid json',
        },
      };
    }

    if (!isObject(parsed) || typeof parsed.recordType != 'string' || typeof parsed.messageId != 'string') {
      return {
        warning: {
          lineNumber,
          code: 'invalid_record',
          detail: 'record must include recordType and messageId',
        },
      };
    }

    if (parsed.recordType == 'message') {
      if (!isObject(parsed.envelope) || typeof parsed.insertedAt != 'string' || typeof parsed.ttlSeconds != 'number' || typeof parsed.priority != 'number') {
        return {
          warning: {
            lineNumber,
            code: 'invalid_record',
            detail: 'message record missing required fields',
          },
        };
      }
      return {
        record: {
          recordType: 'message',
          messageId: parsed.messageId,
          insertedAt: parsed.insertedAt,
          ttlSeconds: parsed.ttlSeconds,
          priority: parsed.priority,
          envelope: parsed.envelope as unknown as EdgeLocalEnvelope,
        },
      };
    }

    if (parsed.recordType == 'state') {
      if (!isBufferState(parsed.state) || typeof parsed.updatedAt != 'string') {
        return {
          warning: {
            lineNumber,
            code: 'invalid_record',
            detail: 'state record missing required fields',
          },
        };
      }
      return {
        record: {
          recordType: 'state',
          messageId: parsed.messageId,
          state: parsed.state,
          reason: typeof parsed.reason == 'string' ? parsed.reason : undefined,
          updatedAt: parsed.updatedAt,
        },
      };
    }

    return {
      warning: {
        lineNumber,
        code: 'invalid_record',
        detail: `unsupported recordType: ${parsed.recordType}`,
      },
    };
  }

  public compactLedger(): { readonly beforeLines: number; readonly afterLines: number } {
    const recovered = this.recoverFromLedger().records;
    const beforeLines = existsSync(this.ledgerFile)
      ? readFileSync(this.ledgerFile, 'utf8').split('\n').filter((line) => line.trim().length > 0).length
      : 0;
    const compactLines: BufferRecord[] = [];
    for (const item of recovered) {
      compactLines.push(item.message);
      compactLines.push({
        recordType: 'state',
        messageId: item.message.messageId,
        state: item.currentState,
        updatedAt: nowIso(),
      });
    }
    writeFileSync(this.ledgerFile, compactLines.map((item) => JSON.stringify(item)).join('\n') + '\n', 'utf8');
    return {
      beforeLines,
      afterLines: compactLines.length,
    };
  }

  public quarantineInvalidSample(reason: string, sample: unknown): string {
    const filePath = join(this.quarantineDir, `${Date.now()}-${Math.random().toString(16).slice(2)}.json`);
    writeFileSync(
      filePath,
      JSON.stringify(
        {
          createdAt: nowIso(),
          reason,
          sample,
        },
        null,
        2,
      ) + '\n',
      'utf8',
    );
    return filePath;
  }

  public ledgerPath(): string {
    return this.ledgerFile;
  }

  private appendState(messageId: string, state: BufferState, reason?: string): void {
    const stateRecord: StateRecord = {
      recordType: 'state',
      messageId,
      state,
      reason,
      updatedAt: nowIso(),
    };
    appendJsonl(this.ledgerFile, stateRecord);
  }

  private reconstruct(): Array<{ message: MessageRecord; currentState: BufferState }> {
    return this.recoverFromLedger().records;
  }

  private reconstructFromRecords(
    records: readonly BufferRecord[],
    warnings: RecoveryWarning[],
  ): Array<{ message: MessageRecord; currentState: BufferState }> {
    const messages = new Map<string, MessageRecord>();
    const states = new Map<string, BufferState>();
    for (const record of records) {
      if (record.recordType == 'message') {
        messages.set(record.messageId, record);
        if (!states.has(record.messageId)) states.set(record.messageId, 'pending');
      } else {
        if (!messages.has(record.messageId)) {
          warnings.push({
            lineNumber: -1,
            code: 'state_without_message',
            detail: `state for missing messageId: ${record.messageId}`,
          });
        }
        states.set(record.messageId, record.state);
      }
    }
    return Array.from(messages.values()).map((message) => ({
      message,
      currentState: states.get(message.messageId) ?? 'pending',
    }));
  }

  private readLedger(warnings: RecoveryWarning[]): BufferRecord[] {
    if (!existsSync(this.ledgerFile)) return [];
    const lines = readFileSync(this.ledgerFile, 'utf8').split('\n');
    const records: BufferRecord[] = [];
    for (let idx = 0; idx < lines.length; idx += 1) {
      const lineNumber = idx + 1;
      const checked = this.validateLedgerLine(lines[idx] ?? '', lineNumber);
      if (checked.record) records.push(checked.record);
      if (checked.warning && checked.warning.code != 'empty_line') warnings.push(checked.warning);
    }
    return records;
  }

  private ensureDirs(): void {
    mkdirSync(this.outboxDir, { recursive: true });
    mkdirSync(this.dlqDir, { recursive: true });
    mkdirSync(this.quarantineDir, { recursive: true });
  }

  private countDir(path: string): number {
    if (!existsSync(path)) return 0;
    return readdirSync(path).length;
  }
}
