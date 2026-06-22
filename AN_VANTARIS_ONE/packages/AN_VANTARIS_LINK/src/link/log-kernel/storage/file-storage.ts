/**
 * File-backed log storage — future backend placeholder (not implemented).
 */

import type { WireTransportEvent } from '../../../generated/contracts/wire-event-v1.js';
import type { ILogStorage, LogRecord } from './ilog-storage.js';

export class FileLogStorage implements ILogStorage {
  public append(_partitionId: number, _event: WireTransportEvent): LogRecord {
    throw new Error('FileLogStorage is not implemented');
  }

  public appendDrop(_partitionId: number, _event: WireTransportEvent): void {
    throw new Error('FileLogStorage is not implemented');
  }

  public readFrom(_partitionId: number, _offset: number): readonly LogRecord[] {
    throw new Error('FileLogStorage is not implemented');
  }

  public getLatestOffset(_partitionId: number): number {
    throw new Error('FileLogStorage is not implemented');
  }
}

export function createFileLogStorage(): FileLogStorage {
  return new FileLogStorage();
}
