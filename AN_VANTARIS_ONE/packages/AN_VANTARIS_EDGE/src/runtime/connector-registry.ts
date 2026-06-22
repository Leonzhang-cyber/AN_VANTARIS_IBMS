import type { ConnectorMetadata, ConnectorRecord, ConnectorStatus } from './types.js';

function nowIso(): string {
  return new Date().toISOString();
}

export class ConnectorRegistry {
  private readonly connectors = new Map<string, ConnectorRecord>();

  public register(metadata: ConnectorMetadata): ConnectorRecord {
    const current = this.connectors.get(metadata.id);
    const next: ConnectorRecord = {
      metadata,
      status: metadata.enabled ? current?.status ?? 'configured' : 'disabled',
      lastError: current?.lastError ?? null,
      lastDataAt: current?.lastDataAt ?? null,
      healthStatus: current?.healthStatus ?? 'stopped',
      updatedAt: nowIso(),
    };
    this.connectors.set(metadata.id, next);
    return next;
  }

  public list(): readonly ConnectorRecord[] {
    return Array.from(this.connectors.values());
  }

  public start(id: string): ConnectorRecord {
    return this.transition(id, 'running', 'healthy');
  }

  public stop(id: string): ConnectorRecord {
    return this.transition(id, 'stopped', 'stopped');
  }

  public restart(id: string): ConnectorRecord {
    this.transition(id, 'starting', 'starting');
    return this.transition(id, 'running', 'healthy');
  }

  public getStatus(id: string): ConnectorStatus | null {
    return this.connectors.get(id)?.status ?? null;
  }

  public getCapability(id: string): readonly string[] {
    return this.connectors.get(id)?.metadata.capabilities ?? [];
  }

  public recordLastError(id: string, message: string): ConnectorRecord {
    const item = this.require(id);
    item.lastError = message;
    item.status = 'degraded';
    item.healthStatus = 'degraded';
    item.updatedAt = nowIso();
    return item;
  }

  public recordLastDataTime(id: string, timestamp: string): ConnectorRecord {
    const item = this.require(id);
    item.lastDataAt = timestamp;
    item.updatedAt = nowIso();
    return item;
  }

  public recordHealthStatus(
    id: string,
    health: ConnectorRecord['healthStatus'],
    status?: ConnectorStatus,
  ): ConnectorRecord {
    const item = this.require(id);
    item.healthStatus = health;
    item.status = status ?? (health == 'failed' ? 'failed' : item.status);
    item.updatedAt = nowIso();
    return item;
  }

  public exportStatusSnapshot(): { readonly generatedAt: string; readonly connectors: readonly ConnectorRecord[] } {
    return {
      generatedAt: nowIso(),
      connectors: this.list(),
    };
  }

  private transition(id: string, status: ConnectorStatus, health: ConnectorRecord['healthStatus']): ConnectorRecord {
    const item = this.require(id);
    item.status = status;
    item.healthStatus = health;
    item.updatedAt = nowIso();
    return item;
  }

  private require(id: string): ConnectorRecord {
    const found = this.connectors.get(id);
    if (!found) {
      throw new Error(`connector not registered: ${id}`);
    }
    return found;
  }
}
