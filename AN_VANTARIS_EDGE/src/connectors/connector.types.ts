export type ConnectorStatus =
  | "configured"
  | "starting"
  | "running"
  | "degraded"
  | "stopped"
  | "failed"
  | "disabled";

export interface ConnectorDescriptor {
  connectorId: string;
  protocol: string;
  status: ConnectorStatus;
  tenantId: string;
  projectId: string;
  siteId: string;
}

export interface ConnectorHealth {
  connectorId: string;
  status: ConnectorStatus;
  updatedAt: string;
}
