import type { ConnectorStatus } from "./connector.types.js";
import type {
  ConnectorRegistryEntry,
  ConnectorRegistryOperationResult,
  ConnectorRegistrySnapshot
} from "./connector-registry.types.js";

const ISO_NOW = (): string => new Date().toISOString();

const EMPTY_STATUS_COUNTER = (): Record<ConnectorStatus, number> => ({
  configured: 0,
  starting: 0,
  running: 0,
  degraded: 0,
  stopped: 0,
  failed: 0,
  disabled: 0
});

export class ConnectorRegistry {
  private readonly entries = new Map<string, ConnectorRegistryEntry>();

  register(entry: Omit<ConnectorRegistryEntry, "createdAt" | "updatedAt">): ConnectorRegistryOperationResult {
    if (this.entries.has(entry.connectorId)) {
      return {
        success: false,
        action: "register",
        connectorId: entry.connectorId,
        error: {
          code: "CONNECTOR_ALREADY_EXISTS",
          message: `Connector already exists: ${entry.connectorId}`
        }
      };
    }

    const now = ISO_NOW();
    const created: ConnectorRegistryEntry = {
      ...entry,
      createdAt: now,
      updatedAt: now
    };
    this.entries.set(entry.connectorId, created);
    return { success: true, action: "register", connectorId: entry.connectorId, connector: { ...created } };
  }

  list(): ConnectorRegistryEntry[] {
    return [...this.entries.values()].map((entry) => ({ ...entry }));
  }

  get(connectorId: string): ConnectorRegistryEntry | undefined {
    const found = this.entries.get(connectorId);
    return found ? { ...found } : undefined;
  }

  start(connectorId: string): ConnectorRegistryOperationResult {
    return this.setStatus(connectorId, "start", "running");
  }

  stop(connectorId: string): ConnectorRegistryOperationResult {
    return this.setStatus(connectorId, "stop", "stopped");
  }

  restart(connectorId: string): ConnectorRegistryOperationResult {
    const found = this.entries.get(connectorId);
    if (!found) {
      return this.notFound("restart", connectorId);
    }
    found.status = "running";
    found.lastError = undefined;
    found.updatedAt = ISO_NOW();
    this.entries.set(connectorId, found);
    return { success: true, action: "restart", connectorId, connector: { ...found } };
  }

  disable(connectorId: string): ConnectorRegistryOperationResult {
    return this.setStatus(connectorId, "disable", "disabled");
  }

  enable(connectorId: string): ConnectorRegistryOperationResult {
    return this.setStatus(connectorId, "enable", "configured");
  }

  markFailed(connectorId: string, error: string): ConnectorRegistryOperationResult {
    const found = this.entries.get(connectorId);
    if (!found) {
      return this.notFound("markFailed", connectorId);
    }
    found.status = "failed";
    found.lastError = error;
    found.updatedAt = ISO_NOW();
    this.entries.set(connectorId, found);
    return { success: true, action: "markFailed", connectorId, connector: { ...found } };
  }

  markDegraded(connectorId: string, warning: string): ConnectorRegistryOperationResult {
    const found = this.entries.get(connectorId);
    if (!found) {
      return this.notFound("markDegraded", connectorId);
    }
    found.status = "degraded";
    found.lastError = warning;
    found.updatedAt = ISO_NOW();
    this.entries.set(connectorId, found);
    return { success: true, action: "markDegraded", connectorId, connector: { ...found } };
  }

  updateLastDataAt(connectorId: string, timestamp: string): ConnectorRegistryOperationResult {
    const found = this.entries.get(connectorId);
    if (!found) {
      return this.notFound("updateLastDataAt", connectorId);
    }
    found.lastDataAt = timestamp;
    found.updatedAt = ISO_NOW();
    this.entries.set(connectorId, found);
    return { success: true, action: "updateLastDataAt", connectorId, connector: { ...found } };
  }

  snapshot(): ConnectorRegistrySnapshot {
    const entries = this.list();
    const byStatus = EMPTY_STATUS_COUNTER();
    for (const entry of entries) {
      byStatus[entry.status] += 1;
    }
    return {
      generatedAt: ISO_NOW(),
      total: entries.length,
      byStatus,
      entries
    };
  }

  private setStatus(
    connectorId: string,
    action: "start" | "stop" | "disable" | "enable",
    status: ConnectorStatus
  ): ConnectorRegistryOperationResult {
    const found = this.entries.get(connectorId);
    if (!found) {
      return this.notFound(action, connectorId);
    }
    found.status = status;
    found.updatedAt = ISO_NOW();
    this.entries.set(connectorId, found);
    return { success: true, action, connectorId, connector: { ...found } };
  }

  private notFound(
    action: ConnectorRegistryOperationResult["action"],
    connectorId: string
  ): ConnectorRegistryOperationResult {
    return {
      success: false,
      action,
      connectorId,
      error: {
        code: "CONNECTOR_NOT_FOUND",
        message: `Connector not found: ${connectorId}`
      }
    };
  }
}
