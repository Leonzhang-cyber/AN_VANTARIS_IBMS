import type { ConnectorStatus } from "./connector.types.js";
import type { ProtocolCode } from "../protocol-plugins/protocol-plugin.types.js";

export type ConnectorRegistryLifecycleAction =
  | "register"
  | "start"
  | "stop"
  | "restart"
  | "disable"
  | "enable"
  | "markFailed"
  | "markDegraded"
  | "updateLastDataAt";

export interface ConnectorRegistryEntry {
  connectorId: string;
  connectorName: string;
  protocolCode: ProtocolCode;
  tenantId: string;
  projectId: string;
  siteId: string;
  sourceSystemId: string;
  gatewayId: string;
  status: ConnectorStatus;
  capabilities: string[];
  lastError?: string;
  lastDataAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ConnectorRegistrySnapshot {
  generatedAt: string;
  total: number;
  byStatus: Record<ConnectorStatus, number>;
  entries: ConnectorRegistryEntry[];
}

export interface ConnectorRegistryError {
  code:
    | "CONNECTOR_ALREADY_EXISTS"
    | "CONNECTOR_NOT_FOUND"
    | "INVALID_STATE_TRANSITION";
  message: string;
}

export interface ConnectorRegistryOperationResult {
  success: boolean;
  action: ConnectorRegistryLifecycleAction;
  connectorId: string;
  connector?: ConnectorRegistryEntry;
  error?: ConnectorRegistryError;
}
