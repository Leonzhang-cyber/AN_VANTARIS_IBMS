export type EdgeMessageType =
  | "telemetry.point.updated"
  | "event.created"
  | "alarm.raised"
  | "device.health.updated"
  | "evidence.captured";

export type EdgeQuality = "good" | "uncertain" | "bad" | "unknown";

export interface EdgeNormalizedObject {
  schemaVersion: string;
  edgeMessageId: string;
  traceId: string;
  messageType: EdgeMessageType;
  gatewayId: string;
  connectorId: string;
  sourceSystemId: string;
  tenantId: string;
  projectId: string;
  siteId: string;
  sampledAt: string;
  receivedAt: string;
  quality: EdgeQuality;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
  assetCode?: string;
  assetUid?: string;
  deviceCode?: string;
  deviceUid?: string;
  pointCode?: string;
  pointUid?: string;
  idempotencyKey?: string;
  sourceSequence?: number;
  correlationId?: string;
}
